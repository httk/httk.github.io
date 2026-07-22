# Module directory

*httk₂* is delivered as a set of independent module repositories that share the
`httk.*` namespace. Published modules are documented both here — in this site's
aggregate {doc}`API reference <reference/index>`, pinned to the submodule revisions
this site is built against — and on their own documentation subsite (both linked
below); the remaining modules are under active development and do not yet publish
docs.

## Published modules

### httk-core

Shared core primitives for *httk₂*: type dispatch and the view/backend pattern,
datastreams, and the `DataLoader` for reading httk dataset files. Every other module
builds on it. Import path: `httk.core`.

- API reference on this site: {doc}`httk.core </reference/autoapi/httk/core/index>`
- Documentation subsite: {moduledocs}`httk-core`
- Repository: <https://github.com/httk/httk-core>

### httk-atomistic

Crystal-structure representations — the `Structure` domain (Simple and primitive
views, `Species`) built on the httk-core view/backend pattern. Import path:
`httk.atomistic`.

- API reference on this site: {doc}`httk.atomistic </reference/autoapi/httk/atomistic/index>`
- Documentation subsite: {moduledocs}`httk-atomistic`
- Repository: <https://github.com/httk/httk-atomistic>

## In development

These modules are planned or in progress; their APIs and documentation are not yet
published.

### httk-io

File I/O for *httk₂*, including the CIF reader/writer stack, registered as httk-core
loaders. Import path: `httk.io`.

- Repository: <https://github.com/httk/httk-io>
- Status: in development.

### httk-symgen

Symmetry-based crystal-structure generation. Import path: `httk.symgen`.

- Repository: <https://github.com/httk/httk-symgen>
- Status: in development.

### httk-ml

Tooling for machine-learned interatomic potentials. Import path: `httk.ml`.

- Repository: <https://github.com/httk/httk-ml>
- Status: in development.

### httk-optimade

OPTIMADE serving and client tooling. Import path: `httk.optimade`.

- Repository: <https://github.com/httk/httk-optimade>
- Status: in development.

### httk-web

The web and OPTIMADE serving stack. Import path: `httk.web`.

- Repository: <https://github.com/httk/httk-web>
- Status: in development.

### httk-magnetism

Magnetism workflows. Import path: `httk.magnetism`.

- Repository: <https://github.com/httk/httk-magnetism>
- Status: in development.
