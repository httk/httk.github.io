# High-throughput on HPC systems

For jobs sent through an SSHFS-mounted exchange directory with signed file
commands and a destination daemon, follow {doc}`workspace-daemon`. It covers
public keys, approved confined Slurm launchers and parallel launches. The commands below use the
ordinary Slurm launcher.

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
cd ~
httk launcher add --template slurm --global arrhenius \
    --set slurm.account=<account> --set slurm.partition=<partition> \
    --set slurm.time_limit=24:00:00 --set slurm.nodes=1 \
    --set slurm.ntasks=10 --set slurm.cpus_per_task=1
httk workspace init --name my_bulk_runs \
    --setting manager.launch=arrhenius --setting manager.workers=1 \
    --setting environment.prelude="module load my_stack" \
    ~/my_bulk_runs     # prelude only if needed; the directory must be absent or empty
cd ~/my_bulk_runs
```

## Create the jobs

Run this from the command line where you normally launch the program. The
`{n}` parameter is filled for each job; httk generates the one-step workflow
wrapper and installs it in the workspace once:

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
`--from-command 'srun … vasp_std' --file POSCAR=POSCAR`. These examples use the generic `--from-command` path (like `httk_workflow_run`), which never adds a launch prefix, unlike the code run helpers, whose commands name only the program. `--file` is repeatable for several inputs, as in
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

As above, this is the generic `--from-command` path with no automatic launch prefix, so the command carries its own `srun`.

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
httk job why n17--                  # a stuck or failed job
```

`httk workflow run --count 20 --time-limit 12:00:00` submits the same
allocations with a shorter SLURM `--time`. A longer one needs
`slurm.time_limit_max` set on the launcher.

Here `--count` is the number of **managers** to start: 20 SLURM allocations
of 10 CPUs each, each running the workspace's jobs one after another.
`--workers` is how many jobs ONE manager runs concurrently inside its
allocation; it is 1 here because each `my_executable` uses all 10 CPUs.
`--count`/`manager.count` and `--workers`/`manager.workers` can also be set
once on the workspace; command-line options override those settings for one
run.

Outputs are stored in the job directory's `run/`, including anything that
`my_executable` writes there. A job directory moves with its state, for example
to `jobs/succeeded/n<N>--<uuid>~…` (relative to the workspace root; jobs created
with a `placement` live under `jobs/<state>/<placement>/`), so `httk job show`
prints where it is. Its console output is in the job directory's
`logs/stdio.out`, between attempt marker lines.

If the 24-hour limit interrupts a job, its manager drains and the attempt
fails with `owner_lost`, which a later manager retries only when the job's
`retry_policy.retry_on` lists it (and only while its retry budget lasts; see
[Fix and resume a failed job](#fix-and-resume-a-failed-job) to raise it). Run
`httk workflow run --count 20` again until `httk job list` shows no job left to
run. For individual records, use `httk job show` and `httk job log`.

## Fix and resume a failed job

A failed job is not lost: it stays under `jobs/failed/<placement>/…` with all
of its files. `httk job show JOB` prints where, `httk job why JOB` explains the
failure and names the remedy, and `httk job log JOB` prints the run log. While
the job is `failed` or `paused`, everything in its directory except `job.json`
may be edited; edit first, then post a request. A revived step reruns from its
top, so if the step regenerates a file (for example copies an `INCAR` template),
it overwrites your hand edit at that layer. Edit the file the step reads from.

Three requests revive a job, each as `httk job request ACTION --reason TEXT JOB`:

- `continue`: a parent that failed because a child failed
  (`dependency_failure`) goes back to waiting on its children, with no new
  attempt and no budget counted. Any other failed or paused job reruns its
  current step as a new attempt, bound by the retry budget.
- `restart`: always reruns the current step as a new attempt, bound by the
  budget. On a parent the rerun step reuses the children that still exist,
  matched by their labels, so `restart` refuses (posting nothing) while the
  parent has a failed or cancelled child: `continue --tree` it, or delete the
  child with `httk job delete` so the step creates a fresh one; `--force`
  restarts anyway.
- `override_step --override-step STEP`: a new activation at the named step.

To fix a failed child and let its parent proceed:

```console
httk job why PARENT                                           # names the failed child
httk job request continue --reason "fixed INCAR" CHILD       # edit its files first
httk job show CHILD                                           # or: httk job log CHILD
httk job request continue --reason "child done" PARENT
```

`httk job request continue --tree --reason TEXT PARENT` resumes the failed
descendants deepest first and then the parent, also on a workspace reached
over ssh (not through a workspace daemon). When
`job why` reports `retry_exhausted`, `restart` alone suffices: revivals (`restart`, `continue`, `override_step`)
automatically restore the declared retry allowance (`--keep-budget` opts out).
To go beyond the declared limits, raise the budget first; the override is kept
in the job's `state.json` and `job.json` stays untouched.

```console
httk job request set_budget --max-attempts-per-activation 3 --reason "flaky node" JOB
httk job request restart --reason "retry" JOB
```

`set_budget` also takes `--max-total-attempts` and `--max-activations`
(a number or `unlimited`; give at least one option). Cancelled jobs cannot be
revived, and a succeeded job is never changed. The full rules are in the
[httk-workflow restarting jobs documentation](https://docs.httk.org/httk-workflow/dev/main/restarting_jobs.html).

## More advanced steps

### Collecting results into a database

`httk collect` needs the workflow to declare what its outputs are. A
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
name = "my_executable"
description = "Run my_executable for one integer parameter."

[workflow.runner]
entry = "run.sh"
steps = ["run"]
initial_step = "run"

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
in the next subsection. Install the package in the workspace once, create jobs
from it in the loop, then collect them after the runs finish:

```console
httk workflow install --workspace my_bulk_runs ./my_executable
for n in $(seq 1 1000); do
  httk job new --workflow my_executable --parameter n=$n --tag n$n
done

httk collect --into results.sqlite --id-base example
```

See the {doc}`database walkthrough <walkthrough/06-database>` and the
[httk-workflow collecting documentation](https://docs.httk.org/httk-workflow/dev/main/collecting.html).

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
commit data transactionally, and be packaged and versioned. See the
[full workflow authoring guide](https://docs.httk.org/httk-workflow/dev/main/details/runtime_helpers.html),
[workflow packages](https://docs.httk.org/httk-workflow/dev/main/workflow_packages.html),
[Bash SDK](https://docs.httk.org/httk-workflow/dev/main/sdks/bash_api.html),
[launchers](https://docs.httk.org/httk-workflow/dev/main/details/launchers.html), and
[remotes](https://docs.httk.org/httk-workflow/dev/main/details/remotes.html) documentation.

### Faster job creation

For very large sets, use the Python `new_jobs(...)` streaming form; see the
{doc}`bulk-runs walkthrough <walkthrough/03-bulk-runs>`.
