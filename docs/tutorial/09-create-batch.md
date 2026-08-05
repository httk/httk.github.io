# Generate a batch of jobs

In Python, database results can stream directly into job creation, which is
how a batch of any size is built:

```python
from httk.workflow import Workspace, new_jobs

workspace = Workspace.default()
items = (
    {"parameters": {"structure": row.structure}}
    for row in results.cursor()
)
for job in new_jobs(
    workspace,
    "vasp-relax",
    items,
    inputs={"kpoint_density": 30.0},
    placement="batch",
):
    print(job.job_key)
```

The generator and cursor keep memory usage O(1): jobs are created as rows are
read, without materializing the batch.

The CLI accepts a directory as well. Every readable structure file becomes one
job, tagged after its file:

```console
httk workflow job new --template vasp-relax \
    --parameter-from structure structures/ --input kpoint_density=30.0 \
    --placement batch
```

Because the flag accepts multiple source files, shell globs work too.

See the quickstart and the workflow CLI guide in the versioned *httk-workflow*
documentation listed by the {doc}`module directory <../modules>`.
