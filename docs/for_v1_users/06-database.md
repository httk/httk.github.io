# Storing data in a database

Collected results (page {doc}`05-fetching-results`) become durable records in a
*httk-store* database. The easy path needs no code: collect straight into a
store.

```console
httk workflow collect WORKSPACE --into results.sqlite
```

This stores each collected job's entries plus a provenance `Run` record —
succeeded jobs by default; add `--state failed` (repeatable `--state`) to
include fetched failures. It is deduplicated on re-collection, so re-running is
always safe — a job whose records already exist is skipped rather than
duplicated.

## The direct store API

To store your own records, open a `Backend`, declare a store once, and save
inside a transaction:

```python
from httk.store import Backend, SqlStore

db = Backend.sqlite("results.sqlite")
store = SqlStore(db, entry_records={})
with store.transaction():
    sid = store.save(record)
```

Records are frozen dataclasses. Identity is content-addressed: `content_id` is
computed from the record's canonical JSON, so two records with identical
content deduplicate to one row. The returned `sid` is only the local relational
id of that row and can differ between stores. The first open of a store
declares the durable representations it may hold; reopen later with just
`SqlStore(db)`.

```{admonition} In httk v1
:class: note

The v1 store was `backend = httk.db.backend.Sqlite('example.sqlite'); store =
httk.db.store.SqlStore(backend); store.save(struct)`, and a storable result
class was declared with `@httk.httk_typed_init({...})` on an `HttkObject`
subclass. httk₂ replaces the typed-init classes with ordinary frozen
dataclass records carrying storage markers, and the store declaration happens
once, at the first open.
```

```{admonition} In httk v1
:class: note

Deduplication keyed on an object's `hexhash` (`struct.hexhash`). httk₂ uses
content ids (`content_id`) computed from canonical JSON, and you look a record
up with `store.fetch_by_content_id(cls, key)`.
```

## Backends and vocabulary

SQLite, DuckDB, and PostgreSQL sit behind one `Backend` API —
`Backend.sqlite(...)`, `Backend.duckdb(...)`, `Backend.postgresql(url)` — with
the same store surface. MongoDB is available through `httk.store.backend.mongo` when
MongoDB is already the operational data service. Property and entry-type
definitions come from the OPTIMADE definition vocabulary, so what you store is
what you can later serve.

```{admonition} In httk v1
:class: note

Querying was a `store.searcher()` DSL: bind a class to a variable, add
conditions, declare outputs, iterate. That shape survives in spirit rather
than being replaced — it moved with the store.
```

See {doc}`07-analysis` for querying the stored data with the httk₂ searcher.

If you have an existing v1 database, there is a dedicated migration guide that
walks every v1 construct beside its httk₂ replacement.

## Read next

- {doc}`../data` — storing, querying, and serving, at a glance.
- {doc}`../tutorial/06-store` — saving a structure to SQLite, worked.
- {doc}`07-analysis` — querying the stored data.
- [Database storage](https://docs.httk.org/httk-store/dev/main/db/) and
  [database details](https://docs.httk.org/httk-store/dev/main/details/db/).
- [Migrating from httk v1](https://docs.httk.org/httk-store/dev/main/migrating_from_v1/).
- [Collecting](https://docs.httk.org/httk-workflow/dev/main/collecting/) and
  [MongoDB](https://docs.httk.org/httk-store/dev/main/mongo/).
