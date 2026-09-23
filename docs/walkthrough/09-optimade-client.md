# Using published data from httk as a client

This closes the loop. Once data is published (see {doc}`08-publishing`), someone
external — or future you — consumes it with *httk₂* itself. *httk₂* ships a
read-only OPTIMADE client that presents a remote service through exactly the
same search DSL you use on a local store. Remote queries support one root and
the filters, sorting, and relationship traversals advertised by the service;
local multi-root joins are not portable to every endpoint.

## A remote store you can search

`OptimadeStore(base_url)` is the synchronous, read-only client. It discovers the
service schema, then hands you the ordinary `store.searcher()` interface:

```python
from httk.atomistic import UnitcellStructureView
from httk.store.optimade import OptimadeStore

with OptimadeStore(base_url) as store:
    search = store.searcher()
    structure = search.variable(store.entry_type("structures"))
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
Selecting the entry type explicitly also works when multiple endpoints share
one backend class; binding by class alone would then be ambiguous.
The default request timeout is 120 seconds; pass `timeout=300` to allow longer
queries. A supplied `client=` keeps its own timeout settings.

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

Standard endpoints can be recognized from their declared OPTIMADE version and
standard property names even without property-definition IDs. Provider-prefixed
fields retain their wire names. Set `infer_standard_definitions=False` when
you need definition-only discovery; unrecognized endpoints remain generic
`OptimadeResource` records.

Build queries with `variable` and `add`, then consume named rows from
`results(structure=structure)`, just as for a local store. Follow relationships
through `structure.links.<name>` where the provider exposes them.

## Federating and caching

To search several endpoints at once, `httk.store.FederatedStore({...})` combines
already-open stores into one read-only, source-major union under a single
searcher. Manage the connections yourself — the federation borrows them.

Remote reads never write local state. To keep a fetched entry for offline work,
save it into your own store explicitly:

```python
from httk.store import SqliteStore

cache = SqliteStore("optimade-cache.sqlite", entry_records={})
sid = cache.save(remote)
offline = cache.fetch(type(remote), sid, eager=True)
cache.close()
```

Caching is an explicit local operation, never an implicit OPTIMADE writeback.

## Read next

- {doc}`../tutorial/15-optimade`.
- [The OPTIMADE client](https://docs.httk.org/httk-store/dev/main/details/db-optimade-client.html).
- [Federation](https://docs.httk.org/httk-store/dev/main/federation.html).
