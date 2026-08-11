# Create a Ca–Ti–O batch

The batch is the six structures bundled with this tutorial. The Python form is
the primary path because the COD CIFs declare oxidation states. VASP POSCAR
inputs cannot carry those decorations, and httk never drops them silently, so
we project them away explicitly at the VASP boundary.

```python
from pathlib import Path

from httk.atomistic import UnitcellStructureView
from httk.core import load
from httk.workflow import Workspace, new_jobs
import httk.workflow.vasp  # registers the packaged vasp-relax workflow

workspace = Workspace.default()
items = (
    {
        "inputs": {"structure": load(path).without_charges()},
        "tag": path.stem.lower(),
    }
    for path in sorted(Path("docs/tutorial/data/catio3").glob("*.cif"))
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

`without_charges()` is an explicit lossy presentation for this VASP input;
the original loaded structure remains untouched. The six files are copied from
the Crystallography Open Database and their attribution is in
`data/catio3/LICENSE.txt`.

For a directory containing already charge-free inputs, the CLI can create the
same kind of batch without the Python projection:

```console
httk workflow job new --workflow vasp-relax \
    --input-from structure charge-free-structures/ \
    --parameter kpoint_density=30.0 --placement batch
```

If a charge-bearing file is passed to `--input-from`, the command stops with a
clear error explaining that POSCAR cannot represent species charges and that
`structure.without_charges()` is the explicit projection to use.

The store-driven alternative is useful when page 07 already supplied a
search result cursor. It keeps the same projection at the job boundary:

```python
items = (
    {"inputs": {"structure": UnitcellStructureView(row.structure).without_charges()}, "tag": row.structure.id[:12]}
    for row in results.cursor()
)
for job in new_jobs(workspace, "vasp-relax", items, placement="batch"):
    print(job.job_key)
```

The generator streams rows into jobs, so neither the search result nor the
batch has to be materialized in memory. Continue with the local run in the
next step.
