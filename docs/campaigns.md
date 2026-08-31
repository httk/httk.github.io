# Compute campaigns, small and large

Start locally with the four-command cycle: initialize a workspace, create a
job, run its manager, and collect the result. The packaged `vasp-relax`
workflow accepts a POSCAR and needs no runner authoring:

```console
$ httk workspace init --name default .
$ httk job new --workflow vasp-relax --input structure=POSCAR
$ httk workflow run
$ httk workflow collect --into results.sqlite
```

The workspace holds durable state and provenance; collection is the boundary
where finished jobs become records in *httk-store*. Re-collecting is safe and
deduplicated. Run `httk workflow precheck --workspace WORKSPACE` before starting managers
to report missing settings, runner references, and machine readiness.

For a remote, add and configure the SSH machine, initialize its workspace, set
that workspace's launcher and scheduler settings, then transfer jobs and run
the workspace there:

```console
httk workflow remote add --template ssh kappa
httk workflow remote configure \
    --set host=kappa.example.org --set username=rar \
    --set check_connectivity=yes kappa
httk workflow remote check kappa
httk workspace init kappa:/scratch/rar/httk/runs
httk workflow launcher add --template slurm --global cluster
httk workflow launcher check cluster
httk workspace settings set --key manager.launch --value cluster kappa:runs
httk workspace settings set --key slurm.partition --value batch kappa:runs
httk workspace settings set --key manager.workers --value 8 kappa:runs
httk workspace settings set --key vasp.command --value "srun -n 32 vasp_std" kappa:runs
httk workflow transfer --job JOB-ID default kappa:runs
httk workflow precheck --workspace kappa:runs
httk workflow run --workspace kappa:runs --count 1
httk workflow transfer --state succeeded --state failed kappa:runs default
```

`ssh` runs the adapter's commands through a non-interactive shell, so
`module load` lines and virtualenv activation your login shell sets up don't
apply there. Put that setup in the remote's `prelude` instead of
`~/.bashrc` — it runs under `set -e` ahead of every command the adapter
sends, including the probe `remote check` uses:

```console
httk workflow remote configure --set prelude='module load Python/3.13.5-bundle
source ~/venv/bin/activate' kappa
```

Size tasks against the resources a manager advertises. For example, a manager
with four workers and the following capacities can pack tasks by their actual
requirements:

```console
httk workflow run --workers 4 \
  --worker-resource procs 32 --worker-resource mem 128000 \
  --worker-resource matlab_license_slots 2
```

Requirements are `NAME = integer`. `procs` and `mem` are special: a job that
omits either is assumed to need the manager's fair share (`capacity //
--workers`), so only jobs declaring both can pack more densely than one per
worker. A job needing a resource the manager lacks, or has at 0, is never run
by that manager and appears in its idle summary. With the manager above,
`relax` runs alone while up to two `analyse` steps run concurrently because
two `matlab_license_slots` are available. Inside a SLURM allocation, the
manager derives `procs`, `gpus`, `nodes`, and `mem` from `SLURM_*` unless they
are given. Each manager owns its own allotment; `--count N` starts N managers,
splitting auto-detected capacities across them while keeping explicit
`--worker-resource` values per manager.

Package manifests can declare workflow-wide and per-step resource tables; see
the [workflow package details](https://docs.httk.org/httk-workflow/dev/main/details/workflow_packages/)
for the manifest rules:

```toml
[workflow.resources]
procs = 4
mem = 16000            # MB

[workflow.steps.relax]
resources = { procs = 32, mem = 120000 }

[workflow.steps.analyse]
resources = { procs = 1, mem = 2000, matlab_license_slots = 1 }
```

The Python SDK can publish a dynamic requirement for the next activation:
`a.advance("analyse", resources={"procs": 1, "mem": 2000, "matlab_license_slots": 1})`.

Each workspace owns its launcher and scheduler settings. A large campaign partitions
ordinary workspaces, assigns root jobs by hash, round-robin, or explicit name,
and keeps spawned children with their parent's partition. Use
`campaign init`, `campaign submit`, `workflow run`, and `campaign collect` to
manage those partitions one at a time or together.

Author reusable workflows as packages with an `httk_workflow.toml` manifest.
The nine-language SDK family gives the same runner surface from Python, Bash,
C, Fortran, Rust, Perl, Ada, C++, and Java. jobflow/atomate2, CWL, PWD, and
httk-v1 documents are also normal workflow language realizations.

Compiled packages declare `[workflow.build]`. Publication carries sources-only
digests; `httk workflow build` builds and registers a binary per machine, so
managers execute registered artifacts and never compile jobs themselves.

## Read next

- [Workflow quickstart](https://docs.httk.org/httk-workflow/dev/main/quickstart/), [campaigns](https://docs.httk.org/httk-workflow/dev/main/campaigns/), [collecting](https://docs.httk.org/httk-workflow/dev/main/collecting/), and [CLI](https://docs.httk.org/httk-workflow/dev/main/workflow_cli/).
- [Workflow package authoring](https://docs.httk.org/httk-workflow/dev/main/workflow_packages/), [languages](https://docs.httk.org/httk-workflow/dev/main/workflow_languages/), and [SDKs](https://docs.httk.org/httk-workflow/dev/main/sdks/).
- [CLI details](https://docs.httk.org/httk-workflow/dev/main/details/workflow_cli/), [package details](https://docs.httk.org/httk-workflow/dev/main/details/workflow_packages/), and [task-manager details](https://docs.httk.org/httk-workflow/dev/main/details/taskmanager/).
