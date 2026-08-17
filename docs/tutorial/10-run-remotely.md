# Run the batch

## Local demonstration path

The local manager runs until the workspace is idle. Configure the tutorial mock
as the VASP command; it writes the same output-file contract as a finished
`vasp-relax` job, but its numbers are canned demonstration values, not
physics.

```console
httk workflow workspace settings set vasp.command \
    "$PWD/docs/tutorial/data/mock_vasp_catio3.py"
httk workflow run --workers 2
```

`run` is the local executor here: it prepares, runs, and publishes every job,
then exits when no work remains. On a real VASP machine, use the same flow and
set the command to `vasp_std` or to the site launcher, for example:

```console
httk workflow workspace settings set vasp.command "srun -n 32 vasp_std"
httk workflow run --workers 8
```

The mock deliberately emits demonstration numbers chosen for the phase-diagram
exercise. They are not calculated material energies.

## Cluster variant

For a real cluster, configure a remote once and transfer the complete batch.
`--job` is repeatable; list every page-09 job so the whole batch moves:

```console
httk workflow remote add kappa --template ssh-slurm
httk workflow remote configure kappa \
    --set host=kappa.example.org --set username=rar
httk workflow remote check kappa
httk workflow workspace init kappa:runs
httk workflow workspace settings set kappa:runs vasp.command "srun -n 32 vasp_std"

httk workflow transfer default kappa:runs \
    --job ca --job cao --job catio3 --job o --job ti --job tio
httk workflow run kappa:runs --workers 8
httk workflow workspace status kappa:runs
httk workflow transfer kappa:runs default
```

The reverse transfer brings finished jobs home; run the local collector in the
next step. `workspace init kappa:runs` creates the named workspace on kappa,
so its name is resolved by kappa rather than by the local machine.

See the task manager and workflow CLI guides in the versioned *httk-workflow*
documentation for cluster-specific options.
