# Storing, querying, and serving data

*httk₂* keeps data models separate from storage. Plain frozen dataclasses can
be stored in SQLite or DuckDB through `SqlStore`, or in MongoDB through
`MongoStore`; the same records and neutral query protocols travel across those
backends. Content addressing deduplicates equal records while a local `sid`
identifies a row in one store.

```python
from dataclasses import dataclass
from tempfile import TemporaryDirectory

from httk.store.db import Database, SqlStore

@dataclass(frozen=True)
class Result:
    formula: str

record = Result("NaCl")
with TemporaryDirectory() as directory:
    db = Database.sqlite(f"{directory}/results.sqlite")
    store = SqlStore(db, entry_records={})
    with store.transaction():
        sid = store.save(record)
    assert store.fetch(type(record), sid) == record
```

The search DSL binds a record class to a variable, adds comparisons or
collection predicates such as `has`, `has_any`, and `has_only`, then returns a
lazy result set. `bulk_ingest(workers=N)` is the faster path for building a
large store; use ordinary `save()` for a small increment.

MongoDB uses the same model and store surface when MongoDB is already the
operational data service:

```python
from httk.store.mongo import MongoDatabase, MongoStore

with MongoDatabase.connect(uri, database="materials") as database:
    store = MongoStore(database, entry_records={})
```

Federation presents existing stores as one read-only, source-major union. A
provider turns a store or in-memory records into the neutral entry-provider
contract, and *httk-serve* can expose one or more providers through OPTIMADE:

```python
from httk.serve.optimade import adapter_from_providers, serve

serve(adapter_from_providers([provider]), port=8080)
```

Construct `adapter_from_providers([provider])` first when testing or embedding the adapter; `serve(...)` is the quick development-server path.
For deployment, use `create_asgi_app` as the interface to any ASGI server.

Serving is not limited to OPTIMADE. *httk-serve* can also turn a caller-owned
OpenAPI 3.1 contract into a running application: you supply the JSON Schemas and
one handler per operation, and the adapter derives the routes, validation, and
responses from the contract. This is the mechanism behind its Data Space
Protocol (DSP) support and the way to serve a custom or standardized protocol
from *httk₂* data.

## Read next

- [Data management](https://docs.httk.org/httk-store/dev/main/data/), [database storage](https://docs.httk.org/httk-store/dev/main/db/), [MongoDB](https://docs.httk.org/httk-store/dev/main/mongo/), and [federation](https://docs.httk.org/httk-store/dev/main/federation/).
- [Database details](https://docs.httk.org/httk-store/dev/main/details/db/) and [MongoDB details](https://docs.httk.org/httk-store/dev/main/details/mongo/).
- [OPTIMADE serving](https://docs.httk.org/httk-serve/dev/main/optimade/serving_providers/) and [core definition details](https://docs.httk.org/httk-core/dev/main/details/optimade_definitions/).
- [Serving an OpenAPI contract](https://docs.httk.org/httk-serve/dev/main/http/openapi/) turns a JSON schema into an API server (with [details](https://docs.httk.org/httk-serve/dev/main/http/openapi-details/)).
