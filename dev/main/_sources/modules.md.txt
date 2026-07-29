# Module directory

The seven runtime modules share the `httk.*` namespace. Their aggregate API
reference is pinned to this site's submodule revisions; each module also has a
separate documentation subsite.

## Runtime modules

### httk-core

Shared contracts, exact vector and datastream models, OPTIMADE definitions,
registries, and dependency-free record models. Import path: `httk.core`.

- API reference: {doc}`httk.core </reference/autoapi/httk/core/index>`
- Repository: <https://github.com/httk/httk-core>

### httk-atomistic

Exact crystal-structure and symmetry representations. Import path:
`httk.atomistic`.

- API reference: {doc}`httk.atomistic </reference/autoapi/httk/atomistic/index>`
- Repository: <https://github.com/httk/httk-atomistic>

### httk-io

File-format parsing and writing capabilities, including CIF and POSCAR. Import
path: `httk.io`.

- API reference: {doc}`httk.io </reference/autoapi/httk/io/index>`
- Repository: <https://github.com/httk/httk-io>

### httk-data

Data-management capabilities and validation over core's provider and definition
contracts. Import path: `httk.data`.

- API reference: {doc}`httk.data </reference/autoapi/httk/data/index>`
- Repository: <https://github.com/httk/httk-data>

### httk-optimade

OPTIMADE protocol serving and adaptation capabilities. Import path:
`httk.optimade`.

- API reference: {doc}`httk.optimade </reference/autoapi/httk/optimade/index>`
- Repository: <https://github.com/httk/httk-optimade>

### httk-web

Web-facing application capabilities built around the httk module ecosystem.
Import path: `httk.web`.

- API reference: {doc}`httk.web </reference/autoapi/httk/web/index>`
- Repository: <https://github.com/httk/httk-web>

### httk-workflow

Workflow and calculation orchestration capabilities. Import path:
`httk.workflow`.

- API reference: {doc}`httk.workflow </reference/autoapi/httk/workflow/index>`
- Repository: <https://github.com/httk/httk-workflow>

## Selected snapshot versions

The manifest-derived table below is the authoritative documentation link for
the exact snapshot represented by this site.

```{include} _generated/module_versions.md
```
