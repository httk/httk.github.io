# Operate on Open Materials Database data

```{admonition} Porting gap
:class: warning

There is no v2 equivalent of
`httk.db.open_materials_database_store`, and no OMDB-specific client. The v1
presentation itself marked this example as unavailable in its then-current
release.
```

What v2 does provide is the opposite side of the standard interface:
*httk-atomistic* and *httk-data* expose `EntryProvider`s, and
*httk-serve* turns them into an OPTIMADE HTTP service.

```python
from httk.atomistic import StructureEntryProvider
from httk.serve.optimade import OptimadeConfig, adapter_from_providers, serve

provider = StructureEntryProvider({"example": structure})
serve(adapter_from_providers([provider]), OptimadeConfig(), port=8080)
```

Generic OPTIMADE clients are the interoperability path for remote data; v2 does
not provide a database-specific store singleton.
