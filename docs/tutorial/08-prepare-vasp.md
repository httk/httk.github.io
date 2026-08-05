# Prepare a VASP calculation

In v1 this was a Python call (`prepare_single_run`) followed by running
`vasp` by hand. In v2 the packaged VASP runners do both halves: preparation
derives every input you do not supply, and the workflow manager runs the
calculation.

```console
httk project init --name tutorial
httk workflow workspace settings set vasp.command vasp_std
httk workflow workspace settings set vasp.pseudo_library /path/to/potpaw_PBE
```

Create and run the calculation:

```console
httk workflow job new --template vasp-static \
    --parameter-from structure example.cif --tag example
httk workflow run
```

`job new` scaffolds and submits one job from the packaged `vasp-static`
template (`vasp-relax` and `vasp-relax-static` work the same way). The
`structure` parameter is loaded from the CIF and written as `files/POSCAR`.
The runner's `prepare` step derives the k-point grid, assembles the POTCAR
from the pseudopotential library, and fills in `MAGMOM` and `NBANDS`, with any
explicit `--input incar_tags=...` winning over derived values. `run` executes
the manager until nothing is ready, driving the job through prepare, run, and
collect; the results and logs end up in the payload directory the `job new`
command printed.

The same job can be created in Python:

```python
from httk.core import load
from httk.workflow import Workspace, new_job

workspace = Workspace.default()
job = new_job(
    workspace,
    "vasp-static",
    parameters={"structure": load("example.cif")},
    tag="example",
)
```

Both `vasp.*` settings are stored on the workspace, so they are set once, not
per job; a real `HTTK_VASP_COMMAND` environment variable remains a deployment
override and wins over the workspace setting.

See the quickstart and the packaged VASP runner guide in the versioned
*httk-workflow* documentation listed by the {doc}`module directory <../modules>`.
