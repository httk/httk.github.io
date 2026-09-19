# High-throughput on HPC systems

This is the shortest path from an installed `httk` on the cluster to 1000
SLURM jobs. The example assumes you are logged in to `arrhenius`, that
`my_executable` is available there, and that its command-line form is
`srun my_executable <int>`. Replace `<account>` and `<partition>` with values
for your allocation.

The workspace runs one 24-hour httk manager per `sbatch` allocation. Each
manager has 10 CPUs and runs its workspace jobs one after another inside that
allocation; `--count N` starts N allocations in parallel.

## Set up the workspace and launcher

Run this once on the cluster. No httk project is needed: the workspace is
registered under your user, and `--global` stores the launcher under your user
as well (`~/.config/httk/launchers/`), so it serves every workspace on this
cluster. The repeatable `--setting KEY=VALUE` options seed application
settings while the workspace is created.

```console
mkdir ~/my_bulk_runs && cd ~/my_bulk_runs
httk workflow launcher add --template slurm --global arrhenius \
    --set slurm.account=<account> --set slurm.partition=<partition> \
    --set slurm.time_limit=24:00:00 --set slurm.nodes=1 \
    --set slurm.ntasks=10 --set slurm.cpus_per_task=1
httk workspace init --name my_bulk_runs \
    --setting manager.launch=arrhenius --setting manager.workers=1 \
    --setting environment.prelude="module load my_stack" .     # prelude only if needed
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

### Jobs from a directory of input files

When each run needs its own input file rather than an integer, stage the file
into the job with `--file` and refer to it in the template by the same name.

```console
for f in input_files/*; do
  httk job new --from-command 'srun --ntasks=10 --cpus-per-task=1 my_executable {input}' \
      --file input="$f" --tag "$(basename "$f" .dat)"
done
```

`--file input=PATH` copies the file into the job's payload (`files/input`), so
the job carries its own immutable copy, providing provenance for the run even
if `input_files/` changes later. At run time, `{input}` is filled with the
absolute path of that staged copy (a placeholder resolves from `--parameter`
values or `--file` names; a name given to both is an error). The program still
runs with the job's `run/` directory as its working directory, so relative
outputs land there as before — and every `--file` input is also copied into
that directory under its own name before the command starts (never overwriting
a file that is already there), so a program that reads its input from the
working directory, such as VASP reading `POSCAR`, needs no placeholder at all:
`--from-command 'srun … vasp_std' --file POSCAR=POSCAR`. `--file` is repeatable for several inputs, as in
`--file geometry=… --file settings=…`, and the wrapper it generates is the
same one shown under "Writing the workflow yourself", with the path
substituted.

### Jobs from a directory of input directories

A real VASP run needs several input files together — `INCAR`, `KPOINTS`,
`POSCAR`, `POTCAR`. Keep one directory per run and stage all of its files at
once with `--files`:

```console
for d in inputs/*/; do
  httk job new --from-command 'srun --ntasks=10 --cpus-per-task=1 vasp_std' \
      --files "$d" --tag "$(basename "$d")"
done
```

`--files DIR` stages every regular file directly inside `DIR` under its own
name, exactly as one `--file NAME=DIR/NAME` per file would: the copies live in
the job's `files/` directory, are placed in the working directory before
`vasp_std` starts, and can be referenced as `{INCAR}`-style placeholders when a
program takes paths instead. Subdirectories are skipped (with a warning), and a
name that occurs twice — across two `--files` directories, or in both `--files`
and `--file` — is an error, so no input can be silently replaced.

## Run and watch the batch

Submit 20 manager allocations and return immediately with their SLURM job
IDs:

```console
httk workflow run --count 20        # submits 20 allocations; returns at once with their SLURM job ids
squeue -u $USER                     # the httk-manager jobs
httk job list                       # ready / running / succeeded per job
httk job why jobs/n17--*            # a stuck or failed job
```

Here `--count` is the number of **managers** to start: 20 SLURM allocations
of 10 CPUs each, each running the workspace's jobs one after another.
`--workers` is how many jobs ONE manager runs concurrently inside its
allocation; it is 1 here because each `my_executable` uses all 10 CPUs.
`--count`/`manager.count` and `--workers`/`manager.workers` can also be set
once on the workspace; command-line options override those settings for one
run.

Outputs are stored in `jobs/n<N>--<uuid>/run/`, including anything that
`my_executable` writes there. Its console output is in
`jobs/n<N>--<uuid>/logs/stdio.out`, with attempt markers.

If a job is interrupted by the 24-hour limit, it returns to the queue and a
later manager retries it. Run `httk workflow run --count 20` again until
`httk job list` shows every job as succeeded. For individual records, use
`httk job show` and `httk job log`.

## More advanced steps

### Collecting results into a database

`httk workflow collect` needs the workflow to declare what its outputs are. A
`--from-command` job has no collector, so collecting it directly would produce
only generic records. To give `answer.txt` a named output, turn the one-command
job into a small workflow package:

```text
my_executable/
├── httk_workflow.toml
├── run.sh       # the same wrapper shown below
└── collect.py
```

Declare the workflow, runner, output, and collector in
`my_executable/httk_workflow.toml`:

```toml
[workflow]
id = "my_executable"
description = "Run my_executable for one integer parameter."

[workflow.runner]
entry = "run.sh"
steps = ["run"]
initial_step = "run"
data_mode = "none"
workdir_mode = "persistent"

[workflow.outputs.answer]
entry_type = "strings"
ref = "https://example.org/types/answer"
description = "The answer written by my_executable."

[workflow.collect]
file = "collect.py"
```

The executable collector runs from the package directory. It reads the
handshake line on stdin, then one `{"record": ...}` line per job. The complete
`JobRecord` mapping names the job's run directory as the workspace-relative
`workdir_path`; combine it with the record's absolute `workspace` path so the
hook can read `answer.txt` there and return one response line for each input
record:

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

handshake = json.loads(next(sys.stdin))
if handshake != {"format": "httk-workflow-collect-stream", "format_version": 2}:
    raise ValueError("unexpected collect stream")
for line in sys.stdin:
    record = json.loads(line)["record"]
    try:
        workdir = Path(record["workspace"]) / record["workdir_path"]
        value = (workdir / "answer.txt").read_text().strip()
        response = {"job_id": record["job_id"], "outputs": {"answer": {"value": value}}}
    except OSError as error:
        response = {"job_id": record["job_id"], "error": str(error)}
    print(json.dumps(response), flush=True)
```

Make `collect.py` executable. The package's `run.sh` is the same runner shown
in the next subsection. Create jobs from the package in the loop, then collect
them after the runs finish:

```console
for n in $(seq 1 1000); do
  httk job new --workflow-dir ./my_executable --parameter n=$n --tag n$n
done

httk workflow collect --into results.sqlite
```

See the {doc}`database walkthrough <walkthrough/06-database>` and the
[httk-workflow collecting documentation](https://docs.httk.org/httk-workflow/dev/main/collecting/).

### Writing the workflow yourself

The `--from-command` shortcut generates this `run.sh`, which can also be used
as the package runner above:

```{code-block} bash
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
[full workflow authoring guide](https://docs.httk.org/httk-workflow/dev/main/details/runtime_helpers/),
[workflow packages](https://docs.httk.org/httk-workflow/dev/main/workflow_packages/),
[Bash SDK](https://docs.httk.org/httk-workflow/dev/main/sdks/native_bash_api/),
[launchers](https://docs.httk.org/httk-workflow/dev/main/launchers/), and
[remotes](https://docs.httk.org/httk-workflow/dev/main/remotes/) documentation.

### Faster job creation

For very large sets, use the Python `new_jobs(...)` streaming form; see the
{doc}`bulk-runs walkthrough <walkthrough/03-bulk-runs>`.
