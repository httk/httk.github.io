# *httk₂*

*httk₂* is a modular high-throughput toolkit for computational materials science.
It is not a single package: the `httk.*` import namespace is a PEP 420 native
namespace shared by a set of independently developed and released module repositories.
Installing the `httk` namespace by itself provides no functionality; you install the
modules you need — starting with `httk-core`, which supplies the shared primitives
(type dispatch, datastreams, the `DataLoader`), and adding domain modules such as
`httk-atomistic` for crystal-structure representations. See the
{doc}`versioned module directory <modules>` for snapshot-specific documentation links.

## Core design decisions

The modules in *httk₂* are independent packages, but they follow the same small set
of design contracts. These contracts are what let data move between modules,
representations, and storage systems without silently changing its meaning.

### Backends own data; views expose representations

Data-representation classes consistently follow the **Backend/View pattern**. A
backend owns the original representation and its data, while views expose that
backend through another public interface. This separates what an object *is* from
how a caller needs to work with it and allows new representations to be added
without pairwise conversion code between every class.

### Exact by default

*httk₂* does not perform lossy conversions behind the user's back. Exact values and
the original backend remain the source of truth; data is approximated or otherwise
modified only when the caller explicitly requests a lossy operation or
presentation. View round-trips retain the backend object, so constructing View B
from View A and then returning to View A recovers the original backend and preserves
its data exactly—even if View B presented an approximation.

### Immutable by default

Data-representation objects are to be treated as immutable unless their class name
starts with `Mutable`. Python cannot enforce this contract in every case, so callers
must not mutate internal data merely because an implementation detail happens to be
reachable. Immutability makes shared backends, safe views, exact round-trips, hashing,
and deduplication dependable.

### Semantic properties through OPTIMADE definitions

OPTIMADE property and entry-type definitions are central to *httk₂*. They give data
fields machine-readable identity, type, shape, units, and meaning, allowing modules,
databases, and protocol adapters to exchange semantically described records rather
than unrelated dictionaries with coincidentally similar keys.

### Storage independent of the database backend

The *httk₂* ORM stores and reconstructs ordinary frozen dataclasses through a
database-backend-agnostic API. The same domain objects and query expressions work
across supported databases; SQL generation and dialect details remain behind the
storage backend instead of leaking into the models or their callers.

This site is the top-level documentation for *httk₂*. It carries an aggregate
{doc}`API reference <reference/index>` covering the published modules (pinned to the
submodule revisions this site is built against), and each module additionally
publishes its own subsite under [docs.httk.org](https://docs.httk.org); the
{doc}`module directory <modules>` links to each one.

```{admonition} Quick links
:class: tip

- **Module directory**: {doc}`modules` — every *httk₂* module and where its docs live.
- **API reference**: {doc}`reference/index` — the aggregate reference for the published modules on this site.
- **The v1 presentation, in v2**: {doc}`presentation/index` — the original short
  example sequence translated to current APIs, including the remaining gaps.
- **Example notebooks**: {doc}`notebooks/index` — runnable tours of the core and cross-module APIs.
```

## Install

Preferably work in a Python virtual environment. Install `httk-core` first — it
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
architecture
authoring
presentation/index
reference/index
notebooks/index
```
