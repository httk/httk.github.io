# Store custom data

V1 required an `HttkObject` subclass and a decorated initializer. V2 stores a
plain frozen dataclass:

```python
from dataclasses import dataclass

from httk.store.db import Database, SqlStore


@dataclass(frozen=True)
class StructureIsEdible:
    formula: str
    is_edible: bool


store = SqlStore(Database.sqlite("presentation.sqlite"), entry_records={})
store.save(StructureIsEdible("ClNa", True))
store.save(StructureIsEdible("As", False))
```

No ORM base class, decorator, or plugin property is required. Nested frozen
dataclasses become references; `Annotated` storage markers add indexes,
uniqueness, skipped fields, and fixed tensor shapes.

See the complete storable-record example in the versioned *httk-store*
documentation listed by the {doc}`module directory <../modules>`.
