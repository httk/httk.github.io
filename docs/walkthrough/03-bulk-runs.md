# Generating a bulk set of runs

High-throughput work means turning a query over stored structures into many
jobs. In httk v1 you wrote a Python loop that called
`httk.task.create_batch_task` once per structure and left a differently-named
directory behind for each. In *httk₂* the query results stream into a workspace
with durable job records, and creation-time parameters are validated as they
are made.

## From Python, streaming a query

Open the DuckDB store from page 02, select the structures whose formula
contains silicon, and stream those records into `new_jobs`. The
`species_at_sites.has_any("Si")` predicate is the portable stored-record
selector for this composition query:

```python
from pathlib import Path

from httk.atomistic import UnitcellStructureRecord, UnitcellStructureView
from httk.store import Backend, SqlStore
from httk.workflow import Workspace, new_jobs
import httk.workflow.vasp  # registers the packaged vasp-relax workflow

store = SqlStore(Backend.duckdb("source.duckdb"))
search = store.searcher()
record = search.variable(UnitcellStructureRecord)
search.add(record.species_at_sites.has_any("Si"))
results = search.results(structure=record)

workspace = Workspace.initialize(Path("runs"))
items = (
    {
        "inputs": {
            "structure": UnitcellStructureView(row.structure).without_charges(),
        },
        "tag": row.structure.id[:12],
    }
    for row in results
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

The query is evaluated as the result stream is consumed, so neither the
matching records nor the jobs have to be materialized in memory. The
`UnitcellStructureView` turns each stored record back into the structure object
the VASP workflow consumes, while `without_charges()` makes the VASP boundary
explicit.

## From the CLI

The CLI `--input-from` form accepts a file or a directory, not a store query;
use it as the file-based alternative when the inputs are already on disk:

```console
$ httk job new --workflow vasp-relax \
      --input-from structure charge-free-structures/ \
      --parameter kpoint_density=30.0 --placement batch
```

The query-driven path is the Python form above. A directory batch derives one
job tag from each readable input; the runner is published once for the set and
jobs are submitted as they are generated.

Creation-time parameterization goes through `[workflow.parameters.*]` in the
manifest, validated at job creation and applied by the runner's
`@run.instantiate` hook. A `placement` string organizes the batch, and — for
truly large sets — a *campaign* partitions the work across several workspaces
with `campaign init`, `campaign submit`, `workflow run`, and `campaign collect`.

```{admonition} In httk v1
:class: note

The pattern was a hand-written loop calling
`httk.task.create_batch_task('Runs/', 't:vasp/batch/vasp-relax-two',
{"structure": struct}, name=struct.hexhash)`. Each call applied the template,
ran its `ht.instantiate.py`, and left a directory whose name encoded the state
(`ht.task.<computer>.<taskid>.<step>...waitstart`). *httk₂* replaces that
file-and-directory batch path with a store query feeding durable workspace
jobs.
```

```{admonition} In httk v1
:class: note

Template variables were passed to `ht.instantiate.py` as globals with no
schema. In *httk₂* they are declared `[workflow.parameters.*]`: a declared
parameter given a value of the wrong type fails at job creation; an undeclared
name is kept with a warning, because parameters are deliberately open.
```

## Read next

- {doc}`02-ingesting-data` — load source files and place them in the DuckDB
  store queried above.
- {doc}`04-remote-execution` — send the generated jobs to a remote manager.
- {doc}`../tutorial/09-create-batch` — a concrete file-based batch, with the
  Python and CLI forms.
- {doc}`../campaigns` — the four-command cycle and how a large campaign
  partitions.
- <https://docs.httk.org/httk-workflow/dev/main/details/workflow_cli/> — the
  complete `httk workflow` command tree.
- <https://docs.httk.org/httk-workflow/dev/main/details/runtime_helpers/> —
  authoring a runner and its instantiate hook.
