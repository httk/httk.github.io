# Generate a batch of jobs

Point `job new` at a *directory* and every `POSCAR*` or `*.vasp` file in it
becomes one job, each tagged after its file. The runner is published once for
the whole set:

```console
httk workflow job new --template vasp-relax --from structures/ \
    --input kpoint_density=30.0 --placement batch
```

In Python the same thing streams, which is how a batch of any size is built —
neither side of the loop is ever materialized, and each job costs one payload
directory and one state marker:

```python
from pathlib import Path

from httk.workflow import Workspace, new_jobs
from httk.workflow.registry import default_workspace
from httk.workflow.scaffold import structure_tag

workspace = Workspace(default_workspace().path)
items = (
    {"files": {"POSCAR": path}, "tag": structure_tag(path)}
    for path in sorted(Path("structures").glob("POSCAR.*"))
)
for job in new_jobs(workspace, "vasp-relax", items, inputs={"kpoint_density": 30.0}):
    print(job.job_key)
```

```{admonition} Status
:class: caution

v1 fed a database search directly into batch creation
(`create_batch_task(..., {"structure": struct})`). The v2 equivalent —
streaming the structures found in step 7 into `new_jobs` — waits on the
POSCAR writer noted in step 8; today the batch starts from structure files
on disk.
```

See the quickstart and the workflow CLI guide in the versioned *httk-workflow*
documentation listed by the {doc}`module directory <../modules>`.
