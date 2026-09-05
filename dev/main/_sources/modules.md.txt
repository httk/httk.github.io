# Module directory

The six runtime modules share the `httk.*` namespace. Their aggregate API
reference is pinned to this site's submodule revisions; each module also has a
separate documentation subsite.

## Runtime modules

### httk-core

Shared contracts, exact vector and datastream models, OPTIMADE definitions,
registries, and dependency-free record models. Import path: `httk.core`.

- API reference: {doc}`httk.core </reference/autoapi/httk/core/index>`
- Module documentation: <https://docs.httk.org/httk-core/dev/main/>
- Repository: <https://github.com/httk/httk-core>

### httk-atomistic

Exact crystal-structure and symmetry representations, together with the
file-format I/O layer (CIF/mCIF, POSCAR/CONTCAR, VASP OUTCAR/XDATCAR/WAVECAR,
and trajectory JSONL) that previously lived in the retired *httk-io* module.
Import path: `httk.atomistic` (I/O under `httk.atomistic.io` and
`httk.atomistic.integrations.vasp`).

- API reference: {doc}`httk.atomistic </reference/autoapi/httk/atomistic/index>`
- Module documentation: <https://docs.httk.org/httk-atomistic/dev/main/>
- Repository: <https://github.com/httk/httk-atomistic>

### httk-analyse

Generic lower-convex-hull construction and materials-science phase-diagram
analysis. Import path: `httk.analyse`.

- API reference: {doc}`httk.analyse </reference/autoapi/httk/analyse/index>`
- Module documentation: <https://docs.httk.org/httk-analyse/dev/main/>
- Repository: <https://github.com/httk/httk-analyse>

### httk-store

Data-management capabilities and validation over core's provider and definition
contracts. Import path: `httk.store`.

- API reference: {doc}`httk.store </reference/autoapi/httk/store/index>`
- Module documentation: <https://docs.httk.org/httk-store/dev/main/>
- Repository: <https://github.com/httk/httk-store>

### httk-serve

Web-facing application serving, OPTIMADE protocol serving, and generic
HTTP/OpenAPI protocol serving (including a Data Space Protocol implementation).
Import paths: `httk.serve.web`, `httk.serve.optimade`, `httk.serve.http`, and
`httk.serve.dsp`.

- API reference: {doc}`httk.serve </reference/autoapi/httk/serve/index>`
- Module documentation: <https://docs.httk.org/httk-serve/dev/main/>
- Repository: <https://github.com/httk/httk-serve>

### httk-workflow

Workflow and calculation orchestration capabilities. Import path:
`httk.workflow`.

- API reference: {doc}`httk.workflow </reference/autoapi/httk/workflow/index>`
- Module documentation: <https://docs.httk.org/httk-workflow/dev/main/>
- Repository: <https://github.com/httk/httk-workflow>

## Selected snapshot versions

The manifest-derived table below is the authoritative documentation link for
the exact snapshot represented by this site.

```{include} _generated/module_versions.md
```
