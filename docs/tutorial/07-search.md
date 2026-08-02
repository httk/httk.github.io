# Search the local database

Continuing with the concrete `UnitcellStructureRecord` and `store` from the previous
step, bind a variable and add conditions, then freeze the query with
`results()`:

```python
from httk.atomistic import UnitcellStructureRecord

search = store.searcher()
structure = search.variable(UnitcellStructureRecord)
search.add(structure.species_at_sites.has_any("O"))
results = search.results(structure=structure)

for row in results:
    print("Found:", len(row.structure.species_at_sites), "sites")
```

Rows are lazy instances of `UnitcellStructureRecord`, and the result set can be
reused or sliced. A slice has its own positions for iteration, length,
indexing, `first()`, `one()`, and `column()`, without re-querying. With one
output, `results.scalars()` is a compact object stream. Integer, fraction, and
fracscalar columns support exact `results.column(name).to_fracvector()`;
`.floats()` is the explicit approximate view, while floats, surds, strings,
and datetimes are not accepted by `to_fracvector()`. Variable-length child
projections are rejected when `results()` is declared. Use `first()` or
`one()` when the query should return one row.

For row-by-row processing, `cursor()` reuses unhashable record-class proxy
instances that expire when advanced; views can be built from a live cursor
row. A view component filled before advancing remains readable, while later
fills raise `ExpiredCursorRowError`. The cursor limits hydrated objects, not
the raw result values retained by the result set.

The backend-neutral low-level form still supports `search.output(...)` and
`for (values,), names in search`; see the complete *httk-data* database guide
for that portable protocol and for `cursor()`'s expiry contract.

List fields have explicit set operations: `has_any`, `has_only`, and `is_in`.
References chain into automatic joins, and two variables of the same class form
a self-join.

That concrete class is the natural key for low-level searches in this
single-backing store. `StructureEntry` is different: it is a non-instantiable
logical query/fetch key for an entry family. A store configured with unit-cell,
fundamental-domain, and ASU backings can use
`store.fetch_entry(StructureEntry, structure_id)` and returns whichever concrete
Record actually owns that structural ID.

A first-time store containing only private custom dataclasses must say so
explicitly; reopening it later loads the persisted declaration:

```python
custom_store = SqlStore(Database.sqlite("custom.sqlite"), entry_backings={})
```

The explicit empty mapping prevents an old or unversioned database from being
silently mistaken for the current storage protocol.

See the complete query DSL example in the versioned *httk-data* documentation
listed by the {doc}`module directory <../modules>`.
