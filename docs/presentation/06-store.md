# Store data in SQLite

```{admonition} Status
:class: caution

The SQL capability is ported, but `httk.atomistic.Structure` is not itself a
storable frozen dataclass. Define the persistent record your application needs.
The example below stores a searchable structure summary; a lossless,
first-class storage mapping for the complete atomistic model remains a gap.
```

```python
from dataclasses import dataclass

from httk.atomistic import StructureEntryProvider, load_structure
from httk.data.db import Database, SqlStore


@dataclass(frozen=True)
class StructureSummary:
    formula: str
    nsites: int
    elements: list[str]


structure = load_structure("example.cif")
record = next(iter(StructureEntryProvider({"example": structure}).records("structures")))
summary = StructureSummary(
    record["chemical_formula_reduced"],
    record["nsites"],
    record["elements"],
)

store = SqlStore(Database.sqlite("presentation.sqlite"))
sid = store.save(summary)
print("Saved row", sid)
```

`Database.sqlite()` without a filename creates an in-memory database. Storage
is exact for supported rational scalar and `FracVector` fields.

See the [database guide](https://docs.httk.org/httk-data/db.html).
