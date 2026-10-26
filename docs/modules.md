# Module directory

The six runtime modules share the `httk.*` namespace. Their aggregate API
reference is pinned to this site's submodule revisions; each module also has a
separate documentation subsite.

## Runtime modules

### httk-core

Shared contracts, exact vector and datastream models, OPTIMADE definitions,
registries, dependency-free record models, and the unified diagnostics
reporting channel (`httk.core.report`). Import path: `httk.core`.

- API reference: {doc}`httk.core </reference/autoapi/httk/core/index>`
- Module documentation: <https://docs.httk.org/httk-core/dev/main/>
- Repository: <https://github.com/httk/httk-core>

### httk-atomistic

Exact crystal-structure and symmetry representations, together with the
file-format I/O layer (CIF/mCIF, POSCAR/CONTCAR, VASP OUTCAR/XDATCAR/WAVECAR,
Quantum ESPRESSO, ABINIT and CP2K structure files, LAMMPS dumps and data
files, and trajectory JSONL) that previously lived in the retired *httk-io*
module. Import path: `httk.atomistic` (I/O under `httk.atomistic.io` and
`httk.atomistic.integrations.<code>`).

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

## Simulation-code support

Support for each simulation code is a separate distribution (repository
`https://github.com/httk/httk-workflow-<code>`) providing the namespace
`httk.codes.<code>` (library, collectors, packaged workflows) and a
`httk.registry.codes.<code>` registration:

- [*httk-workflow-abinit*](https://github.com/httk/httk-workflow-abinit): `httk.codes.abinit`, ABINIT inputs, output parsing and supervised runs.
- [*httk-workflow-cp2k*](https://github.com/httk/httk-workflow-cp2k): `httk.codes.cp2k`, CP2K Quickstep inputs, output parsing and supervised runs.
- [*httk-workflow-gromacs*](https://github.com/httk/httk-workflow-gromacs): `httk.codes.gromacs`, `mdrun` log parsing and supervised `grompp` + `mdrun`.
- [*httk-workflow-lammps*](https://github.com/httk/httk-workflow-lammps): `httk.codes.lammps`, LAMMPS data files, log parsing and supervised runs.
- [*httk-workflow-orca*](https://github.com/httk/httk-workflow-orca): `httk.codes.orca`, molecular ORCA inputs, output parsing and supervised runs.
- [*httk-workflow-phonopy*](https://github.com/httk/httk-workflow-phonopy): `httk.codes.phonopy`, finite-displacement phonons and a collector (depends on *httk-workflow-vasp*).
- [*httk-workflow-qe*](https://github.com/httk/httk-workflow-qe): `httk.codes.qe`, Quantum ESPRESSO `pw.x` inputs, output parsing and supervised runs.
- [*httk-workflow-vasp*](https://github.com/httk/httk-workflow-vasp): `httk.codes.vasp`, VASP input preparation, supervised runs, diagnosis and collection.

Install one with `pip install httk-workflow-<code>` or through the
metapackage: `pip install "httk2[vasp]"` (extras `abinit`, `cp2k`, `gromacs`,
`lammps`, `orca`, `phonopy`, `qe`, `vasp`) or `pip install "httk2[codes]"` for
all eight. Plain `pip install httk2` installs only the six runtime modules. In
development checkouts, `make install_<code>` and `make install_codes` in the
`httk2` repository clone missing `httk-workflow-<code>` checkouts and install
them; `make checkout` does not. See the
[code-support guide](https://docs.httk.org/httk-workflow/dev/main/code_support.html).

## Selected snapshot versions

The manifest-derived table below is the authoritative documentation link for
the exact snapshot represented by this site.

```{include} _generated/module_versions.md
```
