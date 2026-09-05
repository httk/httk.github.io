# Ingesting source data

Before you can run anything you need to read source files — CIFs from a
database, POSCARs from an earlier project, outputs from a finished run. In
httk v1 loading dispatched to a patchwork of format backends, some of them
external command-line tools configured in `httk.cfg`. In *httk₂* there is one
entry point, the readers are pure Python, and dispatch is by filename.

## One entry point

`httk.core.load(path)` returns the file's native representation: a CIF loads as
an asymmetric-unit structure, a POSCAR as a unit-cell structure. Compressed
files decompress transparently, and dispatch is on the extension or exact
basename, case-insensitively.

```python
from httk.core import load

structure = load("example.cif")        # CIF -> ASUStructure
# POSCAR, CONTCAR, and "CONTCAR.bz2" work too; POSCAR -> UnitcellStructure.

print("Formula:", structure.formula)
print("Volume:", float(structure.cell.volume))
```

To expand an asymmetric unit to a full unit cell, or to get the lazy view form,
construct the view explicitly:

```python
from httk.atomistic import UnitcellStructureView

unitcell = UnitcellStructureView(load("example.cif"))
unitcell = UnitcellStructureView("example.cif")   # equivalent, lazy
```

For a remote source, `httk.core.fetch(url)` takes a plain URL string and is
itself the explicit network consent. The lazy view/loader path instead gates
remote access with a `DatastreamURL` token — for example
`UnitcellStructureView(DatastreamURL(url))`. New formats are added by
modules through `register_reader`; `httk-atomistic` registers the CIF/mCIF,
POSCAR, OUTCAR, and WAVECAR readers among others. The ASE bridge works both directions
(`UnitcellStructureView(atoms)` and `ASEAtomsView(structure)`), and a pymatgen
bridge lives in `httk.atomistic`.

```{admonition} In httk v1
:class: note

`httk.load()` existed, but it dispatched to per-format backends —
`httk.atomistic.atomisticio.cif_to_struct(filename, backends=['internal',
'cif2cell', 'ase', 'platon'])` for CIFs, `httk.iface.vasp_if.poscar_to_structure()`
for POSCARs. The pure-Python `internal` backend came first; the external tools
(`cif2cell`, `ase`, `platon`) were optional fallbacks, used only if installed
and configured in `httk.cfg` under `[paths]`. *httk₂* readers are pure Python,
registered, and chosen by filename with no external-tool configuration.
```

```{admonition} In httk v1
:class: note

You may have loaded through the class method `Structure.io.load("example.cif")`.
The *httk₂* equivalent is `UnitcellStructureView(load(path))` (or passing the
path straight to the view). See {doc}`../structures` for the current structure
vocabulary — views, asymmetric units, and where exact geometry becomes a float.
```

## Into a database

The same source directory can become a queryable DuckDB *httk-store*
database. `UnitcellStructureView` normalizes each CIF-native asymmetric unit
to the unit-cell representation declared for the `structures` entry family:

```python
from pathlib import Path

from httk.atomistic import StructureEntry, UnitcellStructureRecord, UnitcellStructureView
from httk.core import load
from httk.store import Backend, EntryIdScheme, SqlStore

db = Backend.duckdb("source.duckdb")
store = SqlStore(
    db,
    entry_records={StructureEntry: UnitcellStructureRecord},
    entry_ids=EntryIdScheme("httk.source", "1"),
)

count = 0
with store.transaction():
    for path in sorted(Path("structures").glob("*.cif")):
        structure = UnitcellStructureView(load(path))
        store.save(structure)
        count += 1

print(f"Stored {count} structures")
```

Records are content-addressed and deduplicated, so re-running the ingest is
idempotent. The same store can later receive calculation results; see
{doc}`06-database`.

```{admonition} In httk v1
:class: note

The comparable habit was `store.save(struct)` on
`httk.db.store.SqlStore`; *httk₂* keeps the save operation but declares the
durable structure representation when the store is first opened.
```

## Read next

- {doc}`../structures` — structures and file formats at ecosystem level.
- {doc}`../tutorial/01-load-structure` — load and inspect a structure in one call.
- {doc}`../tutorial/04-ase` — the ASE bridge in both directions.
- <https://docs.httk.org/httk-core/dev/main/registry/> — `register_reader` and
  the neutral registration pattern.
- <https://docs.httk.org/httk-atomistic/dev/main/structures/> — the structure
  model and views.
- <https://docs.httk.org/httk-atomistic/dev/main/poscar/> and
  <https://docs.httk.org/httk-atomistic/dev/main/vasp_outputs/> — the POSCAR and
  VASP output readers.
