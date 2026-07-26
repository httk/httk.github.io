# Generate a batch of jobs

V2 replaces implicit task directories with explicit immutable job payloads.
This small example creates and submits one payload per name:

```python
from pathlib import Path

from httk.workflow import JobSpec, WorkflowWorkspace, prepare_job_payload

workspace = WorkflowWorkspace.initialize("Runs")

for name in ("CaTiO3", "TiO2", "CaO"):
    payload = Path("payloads") / name
    payload.mkdir(parents=True)
    runner = payload / "run.sh"
    runner.write_text("#!/bin/sh\nexec vasp_std\n", encoding="utf-8")
    runner.chmod(0o755)

    prepare_job_payload(
        payload,
        JobSpec(
            name=name,
            workflow="presentation.vasp-static",
            runner_path="run.sh",
            claim_pool="vasp",
        ),
    )
    workspace.submit(payload, f"batch/{name}")
```

A real payload also carries immutable POSCAR, INCAR, and other inputs. The
runner should publish a structured success, failure, retry, or next-step
outcome; see the
[*httk-workflow* native APIs](https://docs.httk.org/httk-workflow/native_bash_api.html).
