# *httk₂*

*httk₂* is a modular high-throughput toolkit for computational materials science.
It is not a single package: the `httk.*` import namespace is a PEP 420 native
namespace shared by a set of independently developed and released module repositories.
Installing the `httk` namespace by itself provides no functionality; you install the
modules you need — starting with {moduledocs}`httk-core <httk-core>`, which supplies
the shared primitives (type dispatch, datastreams, the `DataLoader`), and adding domain
modules such as {moduledocs}`httk-atomistic <httk-atomistic>` for crystal-structure
representations.

This site is the top-level documentation for *httk₂*. It carries an aggregate
{doc}`API reference <reference/index>` covering the published modules (pinned to the
submodule revisions this site is built against), and each module additionally
publishes its own subsite under [docs.httk.org](https://docs.httk.org); the
{doc}`module directory <modules>` links to each one.

```{admonition} Quick links
:class: tip

- **Module directory**: {doc}`modules` — every *httk₂* module and where its docs live.
- **API reference**: {doc}`reference/index` — the aggregate reference for the published modules on this site.
- **Example notebooks**: {doc}`notebooks/index` — runnable tours of the core and cross-module APIs.
```

## Install

Preferably work in a Python virtual environment. Install {moduledocs}`httk-core <httk-core>`
first — it brings in the `httk` namespace and the shared primitives:

```bash
git clone https://github.com/httk/httk-core
cd httk-core
python -m pip install -e .
```

Then add whichever further modules you need, each the same way. For example, to add
crystal-structure support from {moduledocs}`httk-atomistic <httk-atomistic>`:

```bash
git clone https://github.com/httk/httk-atomistic
cd httk-atomistic
python -m pip install -e .
```

Each module is its own repository and can be installed independently; the shared
`httk.*` namespace lets them compose at import time.

## Small usage example

```python
from httk.core import subpackages

# The httk.* subpackages discovered in the current environment.
print(subpackages)
```

```{toctree}
:maxdepth: 2
:hidden:

modules
reference/index
notebooks/index
```
