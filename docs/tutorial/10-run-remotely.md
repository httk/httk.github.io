# Run the batch

## Local demonstration path

The local manager runs until the workspace is idle. Configure the tutorial mock
as the VASP command; it writes the same output-file contract as a finished
`vasp-relax` job, but its numbers are canned demonstration values, not
physics.

```console
httk workflow workspace settings set --key vasp.command \
    --value "$PWD/docs/tutorial/data/mock_vasp_catio3.py" default
httk workflow run --workers 2
```

`run` is the local executor here: it prepares, runs, and publishes every job,
then exits when no work remains. On a real VASP machine, use the same flow and
set the command to `vasp_std` or to the site launcher, for example:

```console
httk workflow workspace settings set --key vasp.command --value "srun -n 32 vasp_std" default
httk workflow run --workers 8
```

The mock deliberately emits demonstration numbers chosen for the phase-diagram
exercise. They are not calculated material energies.

## Cluster variant

For a real cluster, configure a remote once and transfer the complete batch.
`--job` is repeatable; list every page-09 job so the whole batch moves:

```console
httk workflow remote add --template ssh-slurm kappa
httk workflow remote configure \
    --set host=kappa.example.org --set username=rar kappa
httk workflow remote check kappa
httk workflow workspace init kappa:runs
httk workflow workspace settings set --key vasp.command --value "srun -n 32 vasp_std" kappa:runs

httk workflow transfer \
    --job ca --job cao --job catio3 --job o --job ti --job tio default kappa:runs
httk workflow run --workspace kappa:runs --workers 8
httk workflow workspace status kappa:runs
httk workflow transfer kappa:runs default
```

The manager can advertise the resources available in the cluster allocation:

```console
httk workflow run --workspace kappa:runs --workers 4 \
  --worker-resource procs 32 --worker-resource mem 128000 \
  --worker-resource matlab_license_slots 2
```

Jobs that require a resource this manager does not have remain idle and are
listed in its summary; in a SLURM allocation, `procs`, `gpus`, `nodes`, and
`mem` can be derived from the allocation when not specified.

The reverse transfer brings finished jobs home; run the local collector in the
next step. `workspace init kappa:runs` creates the named workspace on kappa,
so its name is resolved by kappa rather than by the local machine.

See the task manager and workflow CLI guides in the versioned *httk-workflow*
documentation for cluster-specific options.
