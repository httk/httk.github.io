# Generating a bulk set of runs

High-throughput work means turning a directory of structures — or a search
result — into many jobs. In httk v1 you wrote a Python loop that called
`httk.task.create_batch_task` once per structure and left a differently-named
directory behind for each. In *httk₂* the jobs stream into a workspace with
durable records, and creation-time parameters are validated as they are made.

## From the CLI

Point `--input-from NAME DIR` at a directory and every readable file becomes
one job, tagged after its filename:

```console
$ httk workflow job new --workflow vasp-relax \
      --input-from structure charge-free-structures/ \
      --parameter kpoint_density=30.0 --placement batch
```

The runner is published once for the whole set, and jobs are submitted as they
are generated.

## From Python, streaming

The Python form streams, so neither the input set nor the batch is materialized
in memory. Each item declares its inputs and a tag:

```python
from pathlib import Path

from httk.core import load
from httk.workflow import Workspace, new_jobs
import httk.workflow.vasp  # registers the packaged vasp-relax workflow

workspace = Workspace.default()
items = (
    {
        "inputs": {"structure": load(path).without_charges()},
        "tag": path.stem.lower(),
    }
    for path in sorted(Path("structures").glob("*.cif"))
)
for job in new_jobs(
    workspace,
    "vasp-relax",
    items,
    parameters={"kpoint_density": 30.0},
    placement="batch",
):
    print(job.job_key)
```

Creation-time parameterization goes through `[workflow.parameters.*]` in the
manifest, validated at job creation and applied by the runner's
`@run.instantiate` hook. A `placement` string organizes the batch, and — for
truly large sets — a *campaign* partitions the work across several workspaces
with `campaign init`, `campaign submit`, `campaign start-managers`, and
`campaign collect`.

```{admonition} In httk v1
:class: note

The pattern was a hand-written loop calling
`httk.task.create_batch_task('Runs/', 't:vasp/batch/vasp-relax-two',
{"structure": struct}, name=struct.hexhash)`. Each call applied the template,
ran its `ht.instantiate.py`, and left a directory whose name encoded the state
(`ht.task.<computer>.<taskid>.<step>...waitstart`). *httk₂* jobs live in a
workspace with durable records instead of state-encoding directory names.
```

```{admonition} In httk v1
:class: note

Template variables were passed to `ht.instantiate.py` as globals with no
schema. In *httk₂* they are declared `[workflow.parameters.*]`: a declared parameter
given a value of the wrong type fails at job creation; an undeclared name is
kept with a warning, because parameters are deliberately open.
```

## Read next

- {doc}`../tutorial/09-create-batch` — a concrete six-structure batch, both the
  Python and CLI forms.
- {doc}`../campaigns` — the four-command cycle and how a large campaign
  partitions.
- <https://docs.httk.org/httk-workflow/dev/main/campaigns/> — partitioning a
  large run across workspaces.
- <https://docs.httk.org/httk-workflow/dev/main/details/workflow_cli/> — the
  complete `httk workflow` command tree.
- <https://docs.httk.org/httk-workflow/dev/main/details/runtime_helpers/> —
  authoring a runner and its instantiate hook.
