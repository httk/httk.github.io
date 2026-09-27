# Run the batch

## Local demonstration path

The local manager runs until the workspace is idle. Configure the tutorial mock
as the VASP command; it writes the same output-file contract as a finished
`vasp-relax` job, but its numbers are canned demonstration values, not
physics.

```console
httk workspace settings set --key vasp.command \
    --value "$PWD/docs/tutorial/data/mock_vasp_catio3.py" default
httk workflow run --workers 2
```

`run` is the local executor here: it prepares, runs, and publishes every job,
then exits when no work remains. On a real VASP machine, use the same flow and
set the command to `vasp_std` or to the site launcher, for example:

```console
httk workspace settings set --key vasp.command --value "srun -n 32 vasp_std" default
httk workflow run --workers 8
```

The mock deliberately emits demonstration numbers chosen for the phase-diagram
exercise. They are not calculated material energies.

## Cluster variant

For a real cluster, configure an SSH remote once and transfer the complete
batch. The remote is only the path to the machine; manager launch belongs to
the workspace.
`--job` is repeatable; list every page-09 job so the whole batch moves:

```console
httk workflow remote add --template ssh kappa
httk workflow remote configure \
    --set host=kappa.example.org --set username=rar kappa
httk workflow remote check kappa
httk workspace init kappa:runs
httk workflow launcher add --template slurm --global cluster
httk workflow launcher check cluster
httk workspace settings set --key manager.launch --value cluster kappa:runs
httk workspace settings set --key slurm.partition --value batch kappa:runs
httk workspace settings set --key slurm.time_limit --value 01:00:00 kappa:runs
httk workspace settings set --key manager.workers --value 8 kappa:runs
httk workspace settings set --key environment.prelude --value "module load httk vasp" kappa:runs
httk workspace settings set --key vasp.command --value "srun -n 32 vasp_std" kappa:runs

httk workflow transfer \
    --job ca --job cao --job catio3 --job o --job ti --job tio default kappa:runs
httk workflow run --workspace kappa:runs --count 1
httk workspace status kappa:runs
httk workflow transfer kappa:runs default
```

`ssh` runs the adapter's commands through a non-interactive shell, so
`module load` lines and virtualenv activation from your login shell don't
apply there, and `httk` may not even be on `PATH`. Put that setup in the
remote's `prelude` instead of `~/.bashrc` — it runs under `set -e` ahead of
every command the adapter sends, including the probe `remote check` uses;
when only the `httk` binary lives somewhere nonstandard, the narrower
`httk_command=/path/to/httk` setting is enough. This adapter `prelude` is
distinct from the `environment.prelude` workspace setting above: the adapter
prelude bootstraps the shell so `httk` can run at all, while
`environment.prelude` is applied later by the manager once it is already
running on kappa.

```console
httk workflow remote configure --set prelude='module load Python/3.13.5-bundle
source ~/venv/bin/activate' kappa
```

The manager can advertise the resources available in the cluster allocation:

```console
httk workflow run --workspace kappa:runs --workers 4 \
  --worker-resource procs 32 --worker-resource mem 128000 \
  --worker-resource matlab_license_slots 2
```

Jobs that require a resource this manager does not have remain idle and are
listed in its summary; in a Slurm allocation, `procs`, `gpus`, `nodes`, and
`mem` can be derived from the allocation when not specified.

The reverse transfer brings finished jobs home; run the local collector in the
next step. `workspace init kappa:runs` creates the named workspace on kappa,
so its name is resolved by kappa rather than by the local machine.

See the [launcher authoring guide](https://docs.httk.org/httk-workflow/dev/main/launcher_authoring/)
and workflow CLI guide in the versioned *httk-workflow* documentation for
cluster-specific options.
