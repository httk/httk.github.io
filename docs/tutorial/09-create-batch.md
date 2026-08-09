# Generate a batch of jobs

In Python, database results can stream directly into job creation, which is
how a batch of any size is built:

```python
from httk.workflow import Workspace, new_jobs

workspace = Workspace.default()
items = (
    {"inputs": {"structure": row.structure}}
    for row in results.cursor()
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

The generator and cursor keep memory usage O(1): jobs are created as rows are
read, without materializing the batch.

The CLI accepts a directory as well. Every readable structure file becomes one
job, tagged after its file:

```console
httk workflow job new --workflow vasp-relax \
    --input-from structure structures/ --parameter kpoint_density=30.0 \
    --placement batch
```

Because the flag accepts multiple source files, shell globs work too.

For a campaign larger than one workspace, define a partition map and submit
roots through it; child jobs inherit their root's workspace:

```console
httk workflow workspace init screening-a --name screening-a
httk workflow workspace init screening-b --name screening-b
httk workflow campaign init \
    --partition north=screening-a \
    --partition south=screening-b \
    --assignment hash
httk workflow campaign submit --workflow vasp-relax --key silicon \
    --input structure=structures/Si.vasp --tag silicon
```

See the quickstart and the workflow CLI guide in the versioned *httk-workflow*
documentation listed by the {doc}`module directory <../modules>`.

See also the {doc}`/campaigns` topic page for the current workflow vocabulary.
