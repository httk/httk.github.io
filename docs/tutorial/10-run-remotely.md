# Run the batch

## Local demonstration path

The local manager runs until the workspace is idle. Configure the tutorial mock
as the VASP command; it writes the same output-file contract as a finished
`vasp.relax` job, but its numbers are canned demonstration values, not
physics.

```console
httk workspace set -w default \
    vasp.command="$PWD/docs/tutorial/data/mock_vasp_catio3.py"
httk run --workers 2
```

`run` is the local executor here: it prepares, runs, and publishes every job,
then exits when no work remains. On a real VASP machine, use the same flow and
set the command to the bare program, for example (the parallel start comes
from the attempt's launch prefix, not from the command):

```console
httk workspace set -w default vasp.command=vasp_std
httk run --workers 8
```

The mock deliberately emits demonstration numbers chosen for the phase-diagram
exercise. They are not calculated material energies.

## Cluster variant

For a real cluster, configure an SSH remote once and transfer the complete
batch. The remote is only the path to the machine; manager launch belongs to
the workspace, and the transfer ships the workflow the jobs need.
`push` moves every `ready` job, so the page-09 `batch` placement moves at
once (`--job` narrows the selection):

```console
httk remote add --kind ssh kappa
httk remote set kappa host=kappa.example.org username=rar
httk remote check kappa
httk workspace init kappa:runs
httk launcher add --kind slurm --global cluster
httk launcher check cluster
httk workspace set -w kappa:runs manager.launch=cluster slurm.partition=batch \
    slurm.time_limit=01:00:00 manager.workers=8 \
    'environment.prelude=module load httk vasp' \
    vasp.command=vasp_std

httk push kappa:runs
httk run --workspace kappa:runs --count 1
httk workspace status kappa:runs
httk pull kappa:runs
```

`ssh` runs the adapter's commands through a non-interactive shell, so
`module load` lines and virtualenv activation from your login shell don't
apply there, and `httk` may not even be on `PATH`. Put that setup in the
remote's `cli_prelude` instead of `~/.bashrc` — it runs under `set -e` ahead of
every `httk` command the adapter sends over ssh, including the `remote check`
probe but not the `tar` of a pull; it must not read stdin or print to stdout.
When only the `httk` binary lives somewhere nonstandard, the narrower
`httk_command=/path/to/httk` setting is enough. This adapter `cli_prelude` is
distinct from the `environment.prelude` workspace setting above: the
`cli_prelude` runs before each `httk` command the CLI sends to kappa, while
`environment.prelude` is applied later by the manager once it is already
running on kappa.

```console
httk remote set kappa cli_prelude='module load Python/3.13.5-bundle
source ~/venv/bin/activate'
```

The manager can advertise the resources available in the cluster allocation:

```console
httk run --workspace kappa:runs --workers 4 \
  --worker-resource procs 32 --worker-resource mem 128000 \
  --worker-resource matlab_license_slots 2
```

Jobs that require a resource this manager does not have remain idle and are
listed in its summary; in a Slurm allocation, `procs`, `gpus`, `nodes`, and
`mem` can be derived from the allocation when not specified.

`pull` brings every finished (`succeeded`) job home and replaces the `away` copies the push left (`httk job list --state away`; `httk job recover JOB` if a job was lost remotely); run the local collector in the next step.
`workspace init kappa:runs` creates the named workspace on kappa, so its name
is resolved by kappa rather than by the local machine.

See the [launcher authoring guide](https://docs.httk.org/httk-workflow/dev/main/details/launcher_authoring.html)
and workflow CLI guide in the versioned *httk-workflow* documentation for
cluster-specific options.
