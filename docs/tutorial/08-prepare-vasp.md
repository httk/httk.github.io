# Prepare a VASP calculation

## Projects and workspaces

A project is the durable identity and configuration scope for one research
effort. Its `httk_project/` directory is the anchor: it contains
`project.json`, the project identity, trust anchors, and project metadata.
Commands discover the nearest anchor by walking up from the current directory.
Create one anchor once for the effort; it is not a per-run directory.

A workspace is the machine-owned working area where workflow runs happen. It
contains the workspace UUID, job payloads, state markers, journals, and runner
files. A workspace is single-user: managers claim jobs whose marker, payload,
and `job.json` belong to the manager's account. The plain workspace name is
only a command-line lookup name in the owning machine's registry; a remote
machine resolves its own names and paths.

The two layers are related but independent. A project can record a default
workspace name, and that workspace can live outside the project directory. A
project can also be detached from a workspace, which is useful for project
metadata and signed manifests; jobs and their joins still belong to a
workspace. Moving a job between machines detaches a sealed job bundle and
imports it into the destination workspace.

## Initialize the project and its first workspace

The core project command creates the anchor. The workflow command then creates
and registers the first local workspace at the project root:

```console
httk project init --name tutorial .
httk workflow workspace init --name default .
httk workflow workspace settings set --key vasp.command --value vasp_std default
httk workflow workspace settings set --key vasp.pseudo_library --value /path/to/potpaw_PBE default
```

The workspace name `default` is registered on this machine. Commands run from
this project can resolve it as the local default; a project may explicitly
record another registered name later with `httk workflow workspace default`.

## Create and run the calculation

```console
httk workflow job new --workflow vasp-static \
    --input structure=example.cif --parameter 'incar_tags={"ENCUT": 520}' --tag example
httk workflow run
```

`job new` scaffolds and submits one job from the packaged `vasp-static`
workflow (`vasp-relax` and `vasp-relax-static` work the same way). The
`structure` input is loaded from the CIF and written as `files/POSCAR`.
The runner's `prepare` step derives the k-point grid, assembles the POTCAR
from the pseudopotential library, and fills in `MAGMOM` and `NBANDS`, with any
explicit `--parameter 'incar_tags={"ENCUT": 520}'` winning over derived values. `run` executes
the manager until nothing is ready, driving the job through prepare, run, and
publish; the results and logs end up in the payload directory the `job new`
command printed.

The same job can be created in Python:

```python
from httk.core import load
from httk.workflow import Workspace, new_job

workspace = Workspace.default()
job = new_job(
    workspace,
    "vasp-static",
    inputs={"structure": load("example.cif")},
    tag="example",
)
```

Both `vasp.*` settings are stored on the workspace, so they are set once, not
per job; a real `HTTK_VASP_COMMAND` environment variable remains a deployment
override and wins over the workspace setting.

See the quickstart and the packaged VASP runner guide in the versioned
*httk-workflow* documentation listed by the {doc}`module directory <../modules>`.

See also the {doc}`/campaigns` topic page for the current workflow vocabulary.
