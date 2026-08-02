# Store data in SQLite

```python
from httk.atomistic import (
    StructureEntry,
    UnitcellStructureRecord,
    UnitcellStructureView,
    load_structure,
)
from httk.data.db import Database, SqlStore

structure = load_structure("example.cif")

store = SqlStore(
    Database.sqlite("presentation.sqlite"),
    entry_backings={StructureEntry: UnitcellStructureRecord},
)
sid = store.save(structure)
fetched = store.fetch(UnitcellStructureRecord, sid)
restored = UnitcellStructureView(fetched)
print("Saved row", sid, "with stable structure id", restored.id)
```

The first opening of an entry store declares the durable representations it may
contain. Here every stored `StructureEntry` uses the concrete, normalized
`UnitcellStructureRecord` layout. `save()` accepts the natural `Structure` and
projects its nested cell, sites, species, composition, and metadata recursively;
there is no manual record-conversion step and no temporary record graph.

Most httk APIs accept the appropriate `*Like` source or construct a View
automatically. Storage asks for an explicit Record representation because that
choice fixes a durable database layout and should never be surprising.
`UnitcellStructureView(fetched)` exposes the exact fetched Record as a normal
unit-cell structure while retaining that Record as its backend.

The hexadecimal `.id` is structural and stable across equivalent objects and
stores. The integer `sid` is only a local relational identifier: the same Record
may have a different SID in another store without changing its `.id`.

`Database.sqlite()` without a filename creates an in-memory database. Rationals,
surd bases, precisions, and periodicity are stored exactly. Species float fields
round-trip at IEEE-double fidelity; the SQL layer may normalize `-0.0` to `+0.0`.
User-defined frozen dataclasses remain the model for custom data.

See the database guide in the versioned *httk-data* documentation listed by the
{doc}`module directory <../modules>`.
