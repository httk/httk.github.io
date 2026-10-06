# Run Slurm jobs through a mounted exchange

Use the `mount-daemon` adapter when you want to send jobs over a mount such as
SSHFS and control Slurm through signed files. On the cluster, an operator runs
`httk workspace daemon`. You mount only its exchange directory, never the
workspace. The daemon accepts health, start, status and cancellation requests.
A start selects an operator-approved Slurm launcher; clients cannot attach
commands, Slurm options or changed manager settings to it.

This guide describes the current development implementation in *httk-workflow*.
Check that both installations provide `httk workspace daemon --help` and
`httk workflow remote daemon --help`. The ordinary SSH remote and Slurm launcher
in {doc}`hpc` remain separate execution paths.

## What runs where

| Component | Role |
| --- | --- |
| Client | Ejects jobs into the exchange and adopts finished ones, signs requests with your httk identity, verifies replies. |
| Destination daemon | Runs inside Bubblewrap, reads requests, checks authorization and approved launchers, moves bundles between the exchange and the workspace, invokes fixed Slurm operations. |
| Slurm allocation | Runs the trusted manager, unconfined, as the operator. The manager starts every job attempt in its own Bubblewrap sandbox. |
| Protected local state | Holds the daemon's private response key and durable request ledger. It is outside the transport export. |

The remote host, the installation, the operator's launchers and the workspace
settings are trusted. The manager is trusted too and runs unconfined. Each job
attempt, and each rank of a parallel launch, is confined: it can write only its
own job directory, it can read the workspace, and it has no scheduler
authority. The broker runs only *httk* code and the Slurm clients, so it sees
the host filesystem read-only (Slurm, MUNGE, user database) and writes only the
daemon directory and its state. The
[full daemon reference](https://docs.httk.org/httk-workflow/dev/main/details/workspace_daemon.html)
specifies the layout rules, confinement settings and deployment checks.

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
exchange or endpoint file.

There are three separate credentials:

- Your httk public key is given to the daemon as an `authorized_keys` entry; your private
  key stays on the client and signs requests.
- The daemon has its own response-signing key. Its public half is in
  `endpoint.json` in the exchange; confirm it with the operator through a trusted
  channel.
- Slurm uses the site's authentication, for example MUNGE. Httk signatures
  authorize mailbox requests; they do not replace Slurm authentication.

## 2. Approve a launcher on the destination

Run this section on the cluster as the daemon operator. Install *httk-workflow*
and its dependencies in a trusted location visible on compute nodes. The site
needs Linux, Bubblewrap 0.6 or later (0.8.0 or later also blocks nested user
namespaces inside the sandbox),
permitted unprivileged user namespaces, and Slurm 23.11.6 or later.

The workspace and the exchange must be siblings in a dedicated parent that
holds nothing else, on one filesystem and one mount, so that jobs move by a
plain rename. Setup and startup check this. Example mapping:

| Purpose | Destination path | Client mount path |
| --- | --- | --- |
| Dedicated parent | `/srv/httk/example` | Not exported |
| Workspace | `/srv/httk/example/workspace` | Not mounted |
| Exchange | `/srv/httk/example/exchange` | `/mnt/cluster/exchange` |
| Private state | `/var/lib/httk/example` | Not exported |
| Snapshots | `/opt/httk-control/example.snapshots` | Not exported |

The private ledger needs a local filesystem with reliable locking and durability.
Snapshots must be visible at the same absolute path on compute nodes. Export
only the exchange. An SSHFS mount path alone does not restrict the server
account: enforce the restriction on the server, or use a separate restricted
transport identity.

Create the workspace and an ordinary global `slurm` launcher that sets
`manager.confine=bwrap`. Setup reads only the launcher, never workspace
settings:

```console
httk workspace init --name runs /srv/httk/example/workspace
httk workflow launcher add --template slurm --global small \
  --set manager.confine=bwrap --set slurm.cpus_per_task=2 --set slurm.mem=4G \
  --set slurm.time_limit=01:00:00 --set slurm.partition=batch \
  --set manager.workers=2
httk workflow launcher configure --add-path confine.readonly_paths=/software small
```

Replace `batch` with a partition valid at your site; add `slurm.account` if
required. You can create and approve several launchers. Every start launches
one manager; workers share that manager's capacity. Attempts see the workspace
read-only and their own job directory writable. Everything else they need at
run time, such as a module tree, a conda prefix or code binaries, must be listed
in `confine.readonly_paths`; `--add-path` extends the computed default
(`/usr`, `/etc`, the Python installation and where *httk* is imported from)
without restating it. `init` ends with the broker check.

Initialize, check the broker, and run it:

```console
httk workspace daemon init /srv/httk/example/workspace \
  --exchange /srv/httk/example/exchange --add launchers=small \
  --state /var/lib/httk/example --snapshots /opt/httk-control/example.snapshots \
  --add authorized_keys=ed25519:REPLACE_WITH_CLIENT_PUBLIC_KEY
httk workspace daemon check /srv/httk/example/workspace --state /var/lib/httk/example
httk workspace daemon run /srv/httk/example/workspace --state /var/lib/httk/example
```

`init` creates the exchange (it must not exist or be empty), saves the daemon
configuration, prints it, and writes the public `exchange/endpoint.json`.
`httk workspace daemon show` prints the configuration again. `check` tests the
real broker sandbox and scheduler clients; it does not submit a compute job.
`run` stays in the foreground; a site service supervisor may manage it. A
non-default `--state` must be repeated on every later invocation; the
enrollment remembers its snapshot directory.

## 3. Connect the client and send jobs

Mount the exchange with your site's SSHFS arrangement, without
`follow_symlinks` and outside any local workspace. Then, in your client project:

```console
httk workflow remote add --template mount-daemon confined
httk workflow remote daemon configure confined --exchange /mnt/cluster/exchange
httk workflow remote check confined
```

Use `--global` with `remote add` for a user-wide remote. `configure` pins the
identities in `endpoint.json` without sending a command; confirm them with the
operator. `remote check` sends a signed health request. The daemon must be
running and your public key authorized.

Create jobs in a local workspace as in {doc}`campaigns`, then eject one into the
exchange inbox using its actual job ID:

```console
httk job eject JOB /mnt/cluster/exchange/inbox
```

Managers started by the daemon adopt it. Generic `confined:runs` execution is
refused: use the typed commands below to control managers.

## 4. Start, inspect and cancel a manager

Generate a request ID once for a new operation and retain it:

```console
python -c 'import secrets; print(secrets.token_hex(16))'
httk workflow remote daemon start confined --configuration small --request-id REQUEST_ID
httk workflow remote daemon status confined --handle MANAGER_HANDLE
```

Replace `REQUEST_ID` with the generated 32-character lowercase hexadecimal value.
Use the returned opaque manager handle as `MANAGER_HANDLE`. Status creates a fresh
request ID by default, so each call asks for a fresh observation. Without
`--handle`, `httk workflow remote daemon status confined` instead prints the
passive `status.json` and `managers.json` from the exchange, which are
informational. To cancel, generate
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
termination. A job that has succeeded, failed or been cancelled is ejected
automatically, about 60 seconds after it finishes, to `outbox/JOB_KEY` in the
exchange. Fetch it:

```console
httk job adopt /mnt/cluster/exchange/outbox/JOB_KEY
```

A bundle the daemon refuses appears in `outbox/rejected/`, with the reason in
`status.json`. To resume a failed job, adopt it, fix it and eject it to the inbox
again.

The broker also follows each manager's Slurm job. `managers.json` shows its
state, exit code and times, and the bundles still waiting. When a manager ends,
its Slurm output is published as `outbox/managers/<handle>.log`
(`httk workflow remote daemon log REMOTE --handle HANDLE`). If no manager can
run your jobs, `httk workflow remote daemon withdraw REMOTE --request-id ID`
returns the waiting bundles unchanged to `outbox/withdrawn/`, from where
`httk job adopt` takes them back.

## 5. Change the configuration

On the destination, edit a launcher with `httk workflow launcher configure`,
or the daemon configuration (launchers, authorized keys, Slurm clients,
`force` for resources above the sanity limits) with
`httk workspace daemon configure`, then restart the daemon:

```console
httk workspace daemon configure /srv/httk/example/workspace \
  --state /var/lib/httk/example --add launchers=large \
  --add authorized_keys=ed25519:ANOTHER_CLIENT_PUBLIC_KEY
httk workspace daemon run /srv/httk/example/workspace --state /var/lib/httk/example
```

`configure` validates the result before saving it. Every `check` and `run`
reads the listed launchers and the configuration again, and when they changed,
activates them and rewrites `endpoint.json`; a running daemon keeps its
configuration until it is restarted. The same restart applies an *httk*
upgrade. The workspace, exchange, state and snapshot directories and the
cluster are fixed; changing them needs a new enrollment. Queued and running
managers retain their original snapshot; new requests must match the current
catalog. Clients read the catalog live from `endpoint.json`, so they need no
reconfiguration. Preserve the ledger, response key and old snapshots.
Removing a client key also prevents that key from replaying recorded responses.

## Parallel launches

Code commands name only the program, for example `vasp.command = "vasp_std"`.
The parallel start comes from the attempt's launch prefix,
`HTTK_WORKFLOW_LAUNCH`, rendered from the launcher's `manager.launch_template`
or the built-in Slurm prefix. The code run helpers prepend it for you.

Inside a confined attempt the sandbox has no scheduler access, so the prefix is
a launch client: it asks the trusted manager to start the launch, and each rank
then enters its own sandbox, which can write only the job directory. Used by
hand, it works like any prefix:

```console
$HTTK_WORKFLOW_LAUNCH ./program input.dat
```

Ranks use the host network and share a private `/dev/shm` per node and launch.
MPI tuning variables set in the attempt do not reach the ranks; the operator
sets them as `confine.environment.NAME`. Each launch style (the built-in `srun`
prefix with the site's default MPI plugin, Open MPI `mpirun`, `mpprun`, Intel MPI) needs its own site
acceptance: real multi-node communication, shared memory, filesystem and
process isolation, dynamic spawn, nested scheduler access, and cancellation and
cleanup. A generic `MPI_ERR_SPAWN` alone does not establish a containment
boundary. The
[parallel launches reference](https://docs.httk.org/httk-workflow/dev/main/details/workspace_daemon.html#parallel-launches)
describes the rank sandboxes and includes the site probe; local tests do not
establish security on every cluster.
