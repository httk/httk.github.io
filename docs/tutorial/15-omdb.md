# Operate on Open Materials Database data

```{admonition} Partial port
:class: warning

There is no v2 equivalent of
`httk.db.open_materials_database_store`, and no OMDB-specific client. A generic
OPTIMADE client is available for compatible remote services.
```

What v2 does provide is the opposite side of the standard interface:
*httk-atomistic* and *httk-store* expose `EntryProvider`s, and
*httk-serve* turns them into an OPTIMADE HTTP service.

```python
from httk.atomistic import StructureEntryProvider
from httk.serve.optimade import adapter_from_providers, serve

provider = StructureEntryProvider({"example": structure})
serve(adapter_from_providers([provider]), port=8080)
```

For remote reads, use the generic client:

```python
from httk.serve.optimade import OptimadeStore

with OptimadeStore("https://example.org/optimade") as store:
    for entry_type in store.entry_types:
        print(entry_type.name, entry_type.definition_id)
```

Generic OPTIMADE clients are the interoperability path for remote data; v2 does
not provide a database-specific OMDB store singleton.

See also the {doc}`/data` topic page for the current data workflow vocabulary.
