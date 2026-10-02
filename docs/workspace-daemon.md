# Run Slurm jobs through a mounted workspace

Use the `mount-daemon` adapter when you want to transfer jobs over a mount such
as SSHFS and control Slurm through signed files. On the cluster, an operator runs
`httk workspace daemon`. It accepts health, start, status and cancellation
requests. A start selects a locally approved manager configuration; clients
cannot attach commands, Slurm options or changed manager settings to it.

This guide describes the current development implementation in *httk-workflow*.
Check that both installations provide `httk workspace daemon --help` and
`httk workflow remote daemon --help`. The ordinary SSH remote and Slurm launcher
in {doc}`hpc` remain separate execution paths.

## What runs where

| Component | Role |
| --- | --- |
| Client | Transfers job files, signs requests with your httk identity, verifies replies. |
| Destination daemon | Runs inside Bubblewrap, reads requests, checks authorization and approved settings, invokes fixed Slurm operations. |
| Slurm allocation | Starts the manager inside a separate Bubblewrap sandbox before its prelude or workflow runs. |
| Protected local state | Holds the daemon's private response key and durable request ledger. It is outside the transport export. |

The broker can reach Slurm authentication, such as MUNGE. Workflow payloads do
not receive those broker mounts. MPI adds a separate site-approved launch path
described below. The
[full daemon reference](https://docs.httk.org/httk-workflow/dev/main/details/workspace_daemon.html)
specifies the mount restrictions, policy fields and deployment checks.

## 1. Find your client public key

On the computer that will send requests, inspect your existing identities:

```console
httk identity list --json
```

Each entry has `short`, `name`, `email`, `public_key` and `default`. Use the
`public_key` of the default identity: the daemon client signs with that identity.
To select another existing identity, run `httk identity default SHORT`, replacing
`SHORT` with its short name. To establish an identity when none exists:

```console
httk init --name "Your Name" --email you@example.org
```

`httk init` preserves an existing default identity. To print just the selected
public key:

```console
python -c 'from httk.core.identity import identity_public_key; print(identity_public_key())'
```

Give the destination operator the **complete `ed25519:...` string**, including
the prefix. `None` means no usable default key was found; finish identity setup
before continuing. Run these commands with the same user and `HTTK_CONFIG_HOME`
as the client commands below. Never copy a private key or seed into the workspace,
mailboxes, policy or endpoint export.

There are three separate credentials:

- Your httk public key goes in the daemon policy's `authorized_keys`; your private
  key stays on the client and signs requests.
- The daemon has its own response-signing key. Its public half comes in the
  endpoint export, which you obtain from the operator through a trusted channel.
- Slurm uses the site's authentication, for example MUNGE. Httk signatures
  authorize mailbox requests; they do not replace Slurm authentication.

## 2. Approve a manager on the destination

Run this section on the cluster as the daemon operator. Install *httk-workflow*
and its dependencies in a trusted location visible on compute nodes. The site
needs Linux, Bubblewrap 0.9.0 or later with the required namespace features,
permitted unprivileged user namespaces, and Slurm 23.11.6 or later.

Choose a writable workspace, separate request/response directories and protected
state. This example uses the following mapping; provision the parent directories
with appropriate ownership first:

| Purpose | Destination path | Client mount path |
| --- | --- | --- |
| Workspace | `/srv/httk/example/data` | `/home/me/mounts/cluster/data` |
| Requests | `/srv/httk/example/data.daemon-requests` | `/home/me/mounts/cluster/data.daemon-requests` |
| Responses | `/srv/httk/example/data.daemon-responses` | `/home/me/mounts/cluster/data.daemon-responses` |
| Private ledger | `/var/lib/httk/example` | Not exported |
| Policy and snapshots | `/opt/httk-control/` | Not exported |

The private ledger needs a local filesystem with reliable locking and durability.
Snapshots beside the policy must be visible at the same absolute path on compute
nodes. Export only the workspace and mailboxes. Their parents must prevent the
transport user from replacing these roots. An SSHFS mount path alone does not
restrict the server account: enforce the restriction on the server, or use a
separate restricted transport identity.

Create a workspace and a named Slurm launcher:

```console
httk workspace init --name runs /srv/httk/example/data
httk workflow launcher add --template slurm --global small \
  --set slurm.cpus_per_task=2 --set slurm.mem=4G \
  --set slurm.time_limit=01:00:00 --set slurm.partition=batch \
  --set manager.workers=2
```

Replace `batch` with a partition valid at your site; add `slurm.account` if
required. Launcher settings override workspace settings. You can create several
named launchers and approve each. Every start launches one manager; workers
share that manager's capacity. CPU count, memory and time must be finite and
explicit. An approved `environment.prelude` runs inside the payload sandbox.

Save this operator policy as `/opt/httk-control/example.json`, replacing the key
and adjusting installation/configuration paths to your site:

```json
{
  "format": "httk-workspace-daemon-policy",
  "format_version": 2,
  "workspace": "/srv/httk/example/data",
  "state": "/var/lib/httk/example",
  "readonly_paths": ["/usr", "/bin", "/lib", "/lib64", "/opt/httk"],
  "broker_paths": ["/etc/slurm", "/run/munge"],
  "slurm_conf": "/etc/slurm/slurm.conf",
  "authorized_keys": ["ed25519:REPLACE_WITH_CLIENT_PUBLIC_KEY"],
  "allowed_launchers": ["small"]
}
```

`readonly_paths` must expose the trusted Python environment, *httk₂*, libraries
and application binaries. Broker-only paths must remain separate. The initial
operator PATH is trusted: setup finds `bwrap`, `sbatch`, `squeue` and `scancel`
and records their paths; Python defaults to the running interpreter. Explicit
tool paths are also supported. Slurm cluster discovery uses the environment,
configuration or a bounded `scontrol show config` call.

Initialize, check the broker, and export its public endpoint:

```console
httk workspace daemon /srv/httk/example/data --policy /opt/httk-control/example.json --initialize
httk workspace daemon /srv/httk/example/data --policy /opt/httk-control/example.json --check
httk workspace daemon /srv/httk/example/data --policy /opt/httk-control/example.json --export-endpoint > endpoint.json
httk workspace daemon /srv/httk/example/data --policy /opt/httk-control/example.json
```

Initialization saves an immutable approval snapshot and creates the default
sibling mailboxes. `--check` tests the real broker sandbox and scheduler clients;
it does not submit a compute job. The final command stays in the foreground;
a site service supervisor may manage it. Give the client `endpoint.json` through
a trusted channel. It contains public identities, the response key, approved
configuration digests and request lifetime, with no private key.

## 3. Connect the client and transfer jobs

Mount the three exported directories using your site's SSHFS arrangement. The
mount must preserve atomic rename, metadata visibility and server symlink
semantics; validate those properties at the site. Then, in your client project:

```console
httk workflow remote add --template mount-daemon confined
httk workflow remote daemon configure confined --endpoint endpoint.json \
  --mount-root /home/me/mounts/cluster/data \
  --requests /home/me/mounts/cluster/data.daemon-requests \
  --responses /home/me/mounts/cluster/data.daemon-responses
httk workflow remote check confined
```

Use `--global` with `remote add` if you want a user-wide remote instead of a
project remote. Import validates the endpoint and mounted workspace without
sending a command. `remote check` sends a signed health request and verifies
the response. The daemon must be running and your public key must be authorized.

Create jobs in a local workspace as in {doc}`campaigns`. Transfer one using its
actual job ID and the **absolute mounted workspace path**:

```console
httk job transfer default /home/me/mounts/cluster/data --job JOB
```

For this adapter, use the typed commands below to control managers. Generic
`confined:runs` execution and `httk workflow run --workspace confined:runs`
are refused. Native mounted transfers do not run the uploaded workflow on the
client.

## 4. Start, inspect and cancel a manager

Generate a request ID once for a new operation and retain it:

```console
python -c 'import secrets; print(secrets.token_hex(16))'
httk workflow remote daemon start confined --configuration small --request-id REQUEST_ID
httk workflow remote daemon status confined --handle MANAGER_HANDLE
```

Replace `REQUEST_ID` with the generated 32-character lowercase hexadecimal value.
Use the returned opaque manager handle as `MANAGER_HANDLE`. Status creates a fresh
request ID by default, so each call asks for a fresh observation. To cancel, generate
and retain a **different** ID for that new operation:

```console
python -c 'import secrets; print(secrets.token_hex(16))'
httk workflow remote daemon cancel confined --handle MANAGER_HANDLE --request-id CANCEL_REQUEST_ID
```

Each call writes its request ID to stderr and a verified JSON response to stdout.
After a timeout, repeat the same operation with **the same ID and identical
fields**. The client caches the exact signed request; the daemon's durable ledger
prevents a retry from submitting twice. Do not generate a new ID or delete request
history to resolve an uncertain submission. Ask the operator to reconcile it.
Run original and retry commands as the same user with the same httk data directory
(`HTTK_DATA_HOME`, otherwise `$XDG_DATA_HOME/httk` or `~/.local/share/httk`).
Retain its `daemon-requests/` cache so retries reuse the original signature.

Requests include signed timestamps, with **130 minutes of allowed clock skew**
on each side. Default lifetime is one hour, so first execution can fall between
creation minus 130 minutes and expiry plus 130 minutes. Completed responses can
be replayed after expiry by a still-authorized signer; replay does not resubmit.

Exit 2 covers refusals, busy/uncertain outcomes and unacknowledged calls. `UNKNOWN`
status does not mean completion, and cancellation acknowledgement does not prove
termination. Once jobs are finished or otherwise quiescent, transfer results back:

```console
httk job transfer /home/me/mounts/cluster/data default --state succeeded
```

## 5. Change approvals

On the destination, stop the daemon, edit the allowed launcher/workspace settings
or authorized keys, then approve them again:

```console
httk workspace daemon /srv/httk/example/data --policy /opt/httk-control/example.json --reload
httk workspace daemon /srv/httk/example/data --policy /opt/httk-control/example.json --export-endpoint > endpoint.json
httk workspace daemon /srv/httk/example/data --policy /opt/httk-control/example.json
```

Reload refuses while the daemon is running. Changing workspace settings alone
does not change approvals. Queued and running managers retain their original
snapshot; new requests must match the current catalog. Re-import the export on
clients using the same `remote daemon configure` command. Keep the previous
export for exact retries using an old digest; a revised configuration needs a new
operation ID. Preserve the ledger, response key and old snapshots. Removing a
client key also prevents that key from replaying recorded responses.

## MPI applications

The operator can approve MPI launchers and the additional site policy described
in the [MPI reference](https://docs.httk.org/httk-workflow/dev/main/details/workspace_daemon.html#mpi-applications).
This includes fixed rank geometry, PMIx socket roots, devices and node-local
control/shared-memory locations. MPI configurations run one manager worker and
one application step at a time.

Inside a workflow, invoke the application through:

```console
httk workflow mpi run -- /opt/application/bin/program input.dat
```

The trusted launcher uses fixed `srun --mpi=pmix` bootstrap arguments, and each
rank enters Bubblewrap before reading application instructions. Ranks on a node
share an allocation-specific directory mounted at `/dev/shm`, supporting shared
memory without exposing unrelated host objects. The manager remains network
isolated; MPI ranks use host networking and a bounded PMIx endpoint.

Use this wrapper for daemon MPI jobs instead of embedding `mpirun` or nested
`srun` commands in the workflow. Site acceptance must cover real communication,
shared-memory transport, filesystem/process isolation, dynamic spawn, nested
scheduler access and cancellation/cleanup. A generic `MPI_ERR_SPAWN` alone does
not establish a containment boundary. The full reference includes a site probe
and the required checks; local tests do not establish security on every cluster.
