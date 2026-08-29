# High-throughput on HPC systems

This is the shortest path from an installed `httk` on the cluster to 1000
SLURM jobs. The example assumes you are logged in to `arrhenius`, that
`my_executable` is available there, and that its command-line form is
`srun my_executable <int>`. Replace `<account>` and `<partition>` with values
for your allocation.

The workspace runs one 24-hour httk manager per `sbatch` allocation. Each
manager has 10 CPUs and runs its workspace jobs one after another inside that
allocation; `--count N` starts N allocations in parallel.

## Set up the project, workspace, and launcher

Run this once on the cluster:

```console
mkdir ~/my_bulk_runs && cd ~/my_bulk_runs
httk project init --name my_bulk_runs .
httk workspace init --name my_bulk_runs .
httk workflow launcher add --template slurm --global arrhenius \
    --set slurm.account=<account> --set slurm.partition=<partition> \
    --set slurm.time_limit=24:00:00 --set slurm.nodes=1 \
    --set slurm.ntasks=10 --set slurm.cpus_per_task=1
httk workspace settings set --key manager.launch --value arrhenius
httk workspace settings set --key manager.workers --value 1
httk workspace settings set --key environment.prelude --value "module load my_stack"   # only if needed
```

## Create the jobs

Run this from the command line where you normally launch the program. The
`{n}` parameter is filled for each job; httk generates and stores the one-step
workflow wrapper once:

```console
for n in $(seq 1 1000); do
  httk job new --from-command 'srun --ntasks=10 --cpus-per-task=1 my_executable {n}' --parameter n=$n --tag n$n
done
```

## Run and watch the batch

Submit 20 manager allocations and return immediately with their SLURM job
IDs:

```console
httk workflow run --count 20        # submits 20 allocations; returns at once with their SLURM job ids
squeue -u $USER                     # the httk-manager jobs
httk job list                       # ready / running / succeeded per job
httk job why jobs/n17--*            # a stuck or failed job
```

Outputs are stored in `jobs/n<N>--<uuid>/run/`, including anything that
`my_executable` writes there. Its console output is in
`jobs/n<N>--<uuid>/logs/stdio.out`, with attempt markers.

If a job is interrupted by the 24-hour limit, it returns to the queue and a
later manager retries it. Run `httk workflow run --count 20` again until
`httk job list` shows every job as succeeded. For individual records, use
`httk job show` and `httk job log`. If you want the results in a database, run:

```console
httk workflow collect --into results.sqlite
```

See the {doc}`database walkthrough <walkthrough/06-database>` for the
collection path and database details.

```{admonition} Writing the wrapper yourself
:class: note

The shortcut generates this `run.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
source "$HTTK_WORKFLOW_BASH_API"
httk_workflow_runner command run

step_run() {
    httk_workflow_run -- srun --ntasks=10 --cpus-per-task=1 my_executable "$(httk_workflow_parameter n)"
    httk_workflow_succeed
}

httk_workflow_main
```

Use it directly for a job, for example:

```console
httk job new --from-runner ./run.sh --parameter n=17
```

Full workflows can declare inputs, resources per step, spawn child jobs,
publish data transactionally, and be packaged and versioned. See the
[authoring guide](https://docs.httk.org/httk-workflow/dev/main/details/runtime_helpers/),
[workflow packages](https://docs.httk.org/httk-workflow/dev/main/workflow_packages/),
[Bash SDK](https://docs.httk.org/httk-workflow/dev/main/sdks/native_bash_api/),
[launchers](https://docs.httk.org/httk-workflow/dev/main/launchers/), and
[remotes](https://docs.httk.org/httk-workflow/dev/main/remotes/) documentation.
```

## Faster job creation

For very large sets, use the Python `new_jobs(...)` streaming form; see the
{doc}`bulk-runs walkthrough <walkthrough/03-bulk-runs>`.
