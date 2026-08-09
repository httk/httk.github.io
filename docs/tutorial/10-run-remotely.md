# Send and run a batch remotely

A *remote* is one machine the project can reach, named like a `git remote`.
Workspace names are owned by the machine the workspace lives on: `kappa:runs`
means "the workspace this user calls `runs` on kappa", resolved on kappa each
time it is used. Setting up a cluster is a one-time sequence:

```console
httk workflow remote add kappa --template ssh-slurm
httk workflow remote configure kappa \
    --set host=kappa.example.org --set username=rar
httk workflow remote install kappa
httk workflow workspace init kappa:runs
httk workflow workspace settings set kappa:runs vasp.command "srun -n 32 vasp_std"
```

`workspace init kappa:runs` runs the same command on kappa that you would type
there: it creates `runs` under your login home (any path works —
`kappa:/scratch/rar/runs` names the workspace `runs` too) and registers the
name in *kappa's* per-user registry. Ssh in and `httk workflow workspace list`
shows `runs`; any other machine with a remote for kappa can address
`kappa:runs` with nothing to set up.

After that, each batch is send, run, watch — and one command to bring the
finished jobs home:

```console
httk workflow transfer default kappa:runs --job JOB_ID --placement batch
httk workflow run kappa:runs --workers 8
httk workflow workspace status kappa:runs
httk workflow transfer kappa:runs default
```

`transfer` detaches the selected jobs from the local default workspace, pushes
each sealed bundle, validates its digest, and retires the source only after
acknowledgement, so a job never exists in two runnable places. `run` on a
remote workspace submits managers through the remote's scheduler over its
adapter. The reverse `transfer` pulls home whatever has finished; a local
`httk workflow collect` then reads the results (next step).

Before starting managers, the read-only readiness report checks the workspace:

```console
httk workflow precheck WORKSPACE
```

Workflow packages can also declare `[workflow.build]` for compiled runners.
Build and register one binary per platform class on the destination, then run
the package normally:

```console
httk workflow build WORKSPACE ./my-workflow
```

The runner SDK family covers Python plus Bash, C, Fortran, Rust, Perl, Ada,
C++, and Java, so the runner need not be authored in Python.

See the task manager and workflow CLI guides in the versioned *httk-workflow*
documentation listed by the {doc}`module directory <../modules>`.

See also the {doc}`/campaigns` topic page for the current workflow vocabulary.
