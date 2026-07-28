# Store data in SQLite

```python
from httk.atomistic import StructureRecord, load_structure
from httk.data.db import Database, SqlStore

structure = load_structure("example.cif")
record = StructureRecord.from_structure(structure)

store = SqlStore(Database.sqlite("presentation.sqlite"))
sid = store.save(record)
fetched = store.fetch(StructureRecord, sid)
restored = fetched.to_structure()
print("Saved row", sid)
```

`Database.sqlite()` without a filename creates an in-memory database. Rationals,
surd bases, precisions, and periodicity are stored exactly. Species float fields
round-trip at IEEE-double fidelity; the SQL layer may normalize `-0.0` to `+0.0`.
`StructureRecord` is a snapshot; user-defined frozen dataclasses remain the model
for custom data.

See the database guide in the versioned *httk-data* documentation listed by the
{doc}`module directory <../modules>`.
