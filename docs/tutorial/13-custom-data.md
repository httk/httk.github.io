# Store custom data

A plain frozen dataclass is enough for custom stored data:

```python
from dataclasses import dataclass

from httk.store import SqliteStore


@dataclass(frozen=True)
class StructureIsEdible:
    formula: str
    is_edible: bool


store = SqliteStore("presentation.sqlite")
store.save(StructureIsEdible("ClNa", True))
store.save(StructureIsEdible("As", False))
```

Reopening the existing presentation store loads its persisted declaration; a
custom record that is not an entry family needs no declaration of its own. A
new store holding only custom records is created with `entry_records={}`.

No ORM base class, decorator, or plugin property is required. Nested frozen
dataclasses become references; `Annotated` storage markers add indexes,
uniqueness, skipped fields, and fixed tensor shapes.

See the complete storable-record example in the versioned *httk-store*
documentation listed by the {doc}`module directory <../modules>`.
