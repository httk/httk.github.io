# Running on a remote HPC system

Once a bulk set of runs exists (page {doc}`03-bulk-runs`), the next step is to
push them to a cluster and start managers there. In *httk₂* a cluster is a
*remote*: a machine definition made from a packaged adapter template, plus a
workspace that the remote owns. *httk₂* never installs software on the cluster
for you — you log in and set *httk₂* up yourself, then *httk₂* only verifies that
it answers.

Install *httk₂* on the far side first (log in and, e.g., `pipx install
httk-workflow`), then define and check the SSH remote. A remote only describes
how to reach a machine; it is not the manager launcher:

```console
httk workflow remote add --template ssh kappa
httk workflow remote configure \
    --set host=kappa.example.org --set username=rar kappa
httk workflow remote check kappa
```

`remote check` verifies that `httk` answers over the adapter's
*non-interactive* shell and reports its version. This matters: a `module load`
guarded by an interactivity test in `.bashrc` works when you log in but not in
the shell the adapter uses. If `httk` is not on the default path there, point
at a specific binary with `remote configure --set
httk_command="/proj/venv/bin/httk" kappa` instead.

More often the whole environment is missing, not just the binary: `ssh` runs
the adapter's commands through a non-interactive shell, so `module load`
lines and virtualenv activation that your login shell sets up never run
there. Put that setup in the remote's `prelude` instead of `~/.bashrc` — it
runs under `set -e` ahead of every command the adapter sends, including the
`remote check` probe above — and note it is distinct from the
`environment.prelude` workspace setting below: the adapter `prelude`
bootstraps the shell so `httk` can run at all, while `environment.prelude` is
applied later by the manager once it is already running on kappa.

```console
httk workflow remote configure --set prelude='module load Python/3.13.5-bundle
source ~/venv/bin/activate' kappa
```

```{admonition} In httk v1
:class: note

`httk-computer-setup` copied a scheduler-specific computer template into
`ht.project/computers/kappa/` and ran an interactive `make_config`, then
`httk-computer-install kappa` ran the template's `install` script *on the
cluster*. *httk₂* never installs software remotely: `remote check` only
verifies. An old computer bundle can be mapped with `httk workflow remote
import-v1`, which reads its assignment-only `config` — the legacy shell code
(`push`, `pull`, `install`, `command`) is never executed.
```

## Give the workspace a manager launcher

The machine that owns a workspace chooses its path. Initialize the workspace on
the remote, install/check the Slurm launcher there, then set the launcher and
scheduler settings on the workspace itself:

```console
httk workspace init kappa:/scratch/rar/httk/runs
httk workflow launcher add --template slurm --global cluster
httk workflow launcher check cluster
httk workspace settings set --key manager.launch --value cluster kappa:runs
httk workspace settings set --key manager.count --value 1 kappa:runs
httk workspace settings set --key slurm.partition --value batch kappa:runs
httk workspace settings set --key slurm.time_limit --value 01:00:00 kappa:runs
httk workspace settings set --key manager.workers --value 8 kappa:runs
httk workspace settings set --key environment.prelude --value "module load httk vasp" kappa:runs
httk workspace settings set --key manager.command --value httk kappa:runs
httk workspace settings set --key vasp.command --value "srun -n 32 vasp_std" kappa:runs
```

The launcher and scheduler settings live with the workspace, not with the
remote:
`slurm.account`, `slurm.partition`, `slurm.time_limit`, `slurm.nodes`,
`slurm.cpus_per_task`, and `slurm.reservation` become batch directives, and
`manager.workers` supplies the default worker count.

```{admonition} In httk v1
:class: note

Per-queue `config.<queue>` files carried the scheduler knobs, and a queue was
a first-class concept you selected. In *httk₂* there are no queues: the same
knobs are per-workspace settings under the `slurm.*` and `manager.*` names,
and the remote workspace owns them.
```

## Transfer, run, and check

`transfer SRC DST` moves jobs whichever way the two names point. Send the batch
up, then run the workspace. The same command works on the login node, through a
self-addressed `machine_names` name, or from the desk via the remote:

```console
httk workflow transfer --job JOB-ID default kappa:runs
httk workflow precheck --workspace kappa:runs
httk workflow run --workspace kappa:runs --count 1
httk workspace status kappa:runs
```

`precheck` reports readiness — declared-environment resolution, runner-reference
availability and digests, whether a live manager can claim the jobs, and any
required staged inputs — before you start managers. `run --workspace
kappa:runs` reaches the machine through the remote adapter when necessary,
then runs the workspace's configured launcher there. The workspace settings,
including `manager.launch`, determine how managers start; the remote itself
only transfers jobs and runs commands on the machine.

The v1 mindset of one task per manager maps to a worker pool with explicit
resource capacities: use `--workers` for concurrency and repeat
`--worker-resource` for the resources each manager can allot. For example:

```console
httk workflow run --workers 4 \
  --worker-resource procs 32 --worker-resource mem 128000 \
  --worker-resource matlab_license_slots 2
```

Each manager owns its own allotment, so `--count N` starts N managers with
auto-detected capacities split between them while explicit resource values
remain per manager. A job requiring a resource a manager lacks is left idle
and shown in that manager's summary.

```{admonition} In httk v1
:class: note

`httk-tasks-send-to-computer kappa Runs/` renamed the `ht.task.*` directories
to assign them and rsync'd them across; `httk-tasks-start-taskmanager kappa`
submitted `taskmanager.sh` with `sbatch`; `httk-tasks-status` counted
directories in `ht.waitstart/`, `ht.running/`, and `ht.finished/`. Those three
are replaced by `transfer`, `run`, and `workspace status`.
```

## Read next

- {doc}`../tutorial/10-run-remotely` — the same flow, end to end.
- {doc}`05-fetching-results` — bringing finished jobs home.
- {doc}`../campaigns` — scaling this to a partitioned campaign.
- [Task manager](https://docs.httk.org/httk-workflow/dev/main/taskmanager/) and
  [task-manager details](https://docs.httk.org/httk-workflow/dev/main/details/taskmanager/).
- [CLI details](https://docs.httk.org/httk-workflow/dev/main/details/workflow_cli/) and
  [launcher authoring](https://docs.httk.org/httk-workflow/dev/main/launcher_authoring/).
