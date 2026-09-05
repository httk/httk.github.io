# Query an OPTIMADE server

OPTIMADE is the generic HTTP interface for materials data. The client below
uses a plain `base_url`, so the same code works with any compatible provider.
Use [providers.optimade.org](https://providers.optimade.org/) to discover
provider endpoints, then assign the selected OPTIMADE base URL to `base_url`.

For the captured output below, `base_url` points at a local *httk₂*
OPTIMADE server backed by the `presentation.sqlite` store from the earlier
tutorial sequence. The client does not depend on that server implementation;
replace the URL with any provider endpoint.

## Discover and filter structures

`OptimadeStore` is the synchronous, read-only OPTIMADE client. It discovers the
service schema first, then exposes one portable search root. The element filter
is an OPTIMADE list query; it selects the Ca–Ti–O structure without relying on a
provider-specific endpoint name or database API.

```python
from httk.atomistic import OptimadeStructure, UnitcellStructureView
from httk.serve.optimade import OptimadeStore

base_url = "http://127.0.0.1:18770"

with OptimadeStore(base_url) as store:
    print("entry types", [entry_type.name for entry_type in store.entry_types])

    search = store.searcher()
    structure = search.variable(OptimadeStructure)
    search.add(
        structure.elements.has("Ca")
        & structure.elements.has("Ti")
        & structure.elements.has("O")
    )
    rows = [row for row in search.results(structure=structure)]
    print("matches", len(rows))

    for row in rows:
        remote = row.structure
        loaded = UnitcellStructureView(remote)
        print("loaded", type(remote).__name__, remote.id, loaded.elements, loaded.nsites)
```

```text
entry types ['structures']
matches 1
loaded OptimadeStructure d68ac9ddb91b3bee269a37683a3541bb3dddcc4a2784861cbdcbc06c17067e8b ('Ca', 'O', 'Ti') 5
```

The result is an `OptimadeStructure`, which retains the exact remote
OPTIMADE resource. `UnitcellStructureView` loads its structural data into the
ordinary httk atomistic interface; the conversion happens only when the view's
properties are requested. No remote write occurs. For one known entry URL,
`httk.core.fetch(url, kind="optimade")` is also available, but filtered
queries use `OptimadeStore` as shown here.

This is the same read-only interoperability boundary as the old OMDB example,
without an OMDB-specific singleton: providers publish OPTIMADE, and httk
consumes the standard service.
