# Using published data from httk as a client

This closes the loop. Once data is published (see {doc}`08-publishing`), someone
external — or future you — consumes it with httk₂ itself. httk₂ ships a
read-only OPTIMADE client that presents a remote service through exactly the
same search DSL you use on a local store, so a query you already wrote works
unchanged against a published endpoint.

## A remote store you can search

`OptimadeStore(base_url)` is the synchronous, read-only client. It discovers the
service schema, then hands you the ordinary `store.searcher()` interface:

```python
from httk.atomistic import OptimadeStructure, UnitcellStructureView
from httk.serve.optimade import OptimadeStore

with OptimadeStore(base_url) as store:
    search = store.searcher()
    structure = search.variable(OptimadeStructure)
    search.add(
        structure.elements.has("Ca")
        & structure.elements.has("Ti")
        & structure.elements.has("O")
    )
    for row in search.results(structure=structure):
        remote = row.structure
        loaded = UnitcellStructureView(remote)
        print(remote.id, loaded.elements, loaded.nsites)
```

The element filter is an OPTIMADE list query, so the same code works against any
compatible provider — just point `base_url` elsewhere. Use
[providers.optimade.org](https://providers.optimade.org/) to discover endpoints.

```{admonition} In httk v1
:class: note

httk v1 had no OPTIMADE client at all — `httk.optimade` was server-side only.
Consuming someone else's database meant downloading files and re-ingesting them
by hand. This whole page describes a capability that did not exist in v1.
```

## Recognized rows are typed

A recognized structures endpoint yields typed `OptimadeStructure` rows that
retain the exact remote resource. `UnitcellStructureView(optimade_structure)`
expands one lazily into the ordinary httk atomistic interface — the conversion
happens only when a structural property is requested. For a single known entry
URL, `httk.core.fetch(url, kind="optimade")` grabs it directly.

The searcher DSL you knew from v1's `httk.db` is exactly what runs against the
remote endpoint. A `variable`/`add`/`output` query you wrote for your own store
works against a published one; only the store you open is different.

## Federating and caching

To search several endpoints at once, `httk.store.FederatedStore({...})` combines
already-open stores into one read-only, source-major union under a single
searcher. Manage the connections yourself — the federation borrows them.

Remote reads never write local state. To keep a fetched entry for offline work,
save it into your own store explicitly:

```python
from httk.store.db import Database, SqlStore

cache = SqlStore(Database.sqlite("optimade-cache.sqlite"), entry_records={})
sid = cache.save(remote)
offline = cache.fetch(type(remote), sid)
```

Caching is an explicit local operation, never an implicit OPTIMADE writeback.

## Read next

- {doc}`../tutorial/15-optimade`.
- [The OPTIMADE client](https://docs.httk.org/httk-serve/dev/main/optimade/client/)
  and [how it works](https://docs.httk.org/httk-serve/dev/main/optimade/how_it_works/).
- [Federation](https://docs.httk.org/httk-store/dev/main/federation/).
