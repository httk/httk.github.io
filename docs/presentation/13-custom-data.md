# Store custom data

V1 required an `HttkObject` subclass and a decorated initializer. V2 stores a
plain frozen dataclass:

```python
from dataclasses import dataclass

from httk.data.db import Database, SqlStore


@dataclass(frozen=True)
class StructureIsEdible:
    formula: str
    is_edible: bool


store = SqlStore(Database.sqlite("presentation.sqlite"))
store.save(StructureIsEdible("ClNa", True))
store.save(StructureIsEdible("As", False))
```

No ORM base class, decorator, or plugin property is required. Nested frozen
dataclasses become references; `Annotated` storage markers add indexes,
uniqueness, skipped fields, and fixed tensor shapes.

See the [complete storable-record
example](https://docs.httk.org/httk-data/examples/storable_records.html).
