# *httk₂*

*httk₂* is a modular high-throughput toolkit for computational materials science.
It is not a single package: the `httk.*` import namespace is a PEP 420 native
namespace shared by a set of independently developed and released module repositories.
Installing the `httk` namespace by itself provides no functionality; you install the
modules you need — starting with `httk-core`, which supplies the shared primitives
(type dispatch, datastreams, the `DatasetLoader`), and adding domain modules such as
`httk-atomistic` for crystal-structure representations. See the
{doc}`versioned module directory <modules>` for snapshot-specific documentation links.

More about the {doc}`architectural design decisions <architecture>` of *httk₂*.

This site is the top-level documentation for *httk₂*. It carries an aggregate
{doc}`API reference <reference/index>` covering the published modules (pinned to the
submodule revisions this site is built against), and each module additionally
publishes its own subsite under [docs.httk.org](https://docs.httk.org); the
{doc}`module directory <modules>` links to each one.

```{admonition} Quick links
:class: tip

- **Working with *httk₂***:
  {doc}`structures`, {doc}`data`, {doc}`campaigns`, and {doc}`analysis` — the
  ecosystem-level path from input files to results and analysis.
- **Module directory**: {doc}`modules` — every *httk₂* module and where its docs live.
- **API reference**: {doc}`reference/index` — the aggregate reference for the published modules on this site.
- **Tutorial**: {doc}`tutorial/index` — the original short
  example sequence translated to current APIs, including the remaining gaps.
- **Walkthrough**: {doc}`walkthrough/index` — the calculation lifecycle end to end, with notes for users coming from httk v1.
- **HPC**: {doc}`hpc` — run high-throughput jobs through SLURM with *httk₂*.
- **Example notebooks**: {doc}`notebooks/index` — runnable tours of the core and cross-module APIs.
```

The topic pages are short and practical; they link onward to the module
documentation for the complete guides and API details.

## Install

Preferably work in a Python virtual environment.

The quickest route is the [`httk2` metapackage](https://github.com/httk/httk2),
which installs the complete standard module set (`httk-core`,
`httk-atomistic`, `httk-store`, `httk-serve`, `httk-analyse`, `httk-workflow`),
each with its recommended `default` feature extras:

```bash
pip install httk2
```

The metapackage repository also serves the development workflow: its `dev-main`
branch installs the latest `main` state of every module directly from GitHub,
and its `Makefile` can check out all module repositories, run `fetch`/`pull`/`push`
across them, and editable-install them into your virtual environment in one step.
See the [`httk2` README](https://github.com/httk/httk2#readme) for the details.

Alternatively, install modules individually. Install `httk-core` first — it
brings in the `httk` namespace and the shared primitives:

```bash
git clone https://github.com/httk/httk-core
cd httk-core
python -m pip install -e .
```

Then add whichever further modules you need, each the same way. For example, to add
crystal-structure support from `httk-atomistic`:

```bash
git clone https://github.com/httk/httk-atomistic
cd httk-atomistic
python -m pip install -e .
```

Each module is its own repository and can be installed independently; the shared
`httk.*` namespace lets them compose at import time.

## Module layout

The public namespace is split across independently installable distributions:
`httk-core` (`httk.core`), `httk-store` (`httk.store`),
`httk-atomistic` (`httk.atomistic`, which now also provides the file-format
I/O layer), `httk-serve` (`httk.serve`), `httk-analyse` (`httk.analyse`), and
`httk-workflow` (`httk.workflow`).

```{toctree}
:maxdepth: 2
:hidden:

modules
architecture
structures
data
campaigns
analysis
authoring
tutorial/index
walkthrough/index
hpc
reference/index
notebooks/index
```
