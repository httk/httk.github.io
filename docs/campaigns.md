# Compute campaigns, small and large

Start locally with the four-command cycle: initialize a workspace, create a
job, run its manager, and collect the result. The packaged `vasp-relax`
workflow accepts a POSCAR and needs no runner authoring:

```console
$ httk workflow workspace init . --name default
$ httk workflow job new --workflow vasp-relax --input structure=POSCAR
$ httk workflow run
$ httk workflow collect --into results.sqlite
```

The workspace holds durable state and provenance; collection is the boundary
where finished jobs become records in *httk-store*. Re-collecting is safe and
deduplicated. Run `httk workflow precheck WORKSPACE` before starting managers
to report missing settings, runner references, and machine readiness.

For a remote, add and configure the machine, initialize its workspace, then
transfer jobs and run a manager there:

```console
httk workflow remote add kappa --template ssh-slurm
httk workflow remote configure kappa \
    --set host=kappa.example.org --set username=rar \
    --set check_connectivity=yes
httk workflow remote install kappa
httk workflow workspace init kappa:/scratch/rar/httk/runs
httk workflow workspace settings set kappa:runs slurm.partition batch
httk workflow workspace settings set kappa:runs vasp.command "srun -n 32 vasp_std"
httk workflow transfer default kappa:runs --job JOB-ID
httk workflow precheck kappa:runs
httk workflow run kappa:runs --workers 8
httk workflow transfer kappa:runs default --state succeeded --state failed
```

The remote workspace owns scheduler settings. A large campaign partitions
ordinary workspaces, assigns root jobs by hash, round-robin, or explicit name,
and keeps spawned children with their parent's partition. Use
`campaign init`, `campaign submit`, `campaign start-managers`, and
`campaign collect` to manage those partitions one at a time or together.

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
