# Search the local database

Continuing with the `UnitcellStructureRecord` and `store` from the previous
step, build a query with `searcher()`, then freeze it into a reusable result
set with `results()`. The query vocabulary is shared by SQL and MongoDB stores.

## Bind a variable and freeze a query

Bind a record class to a variable, add conditions, and declare the output when
the query is ready:

```python
from httk.atomistic import UnitcellStructureRecord

search = store.searcher()
structure = search.variable(UnitcellStructureRecord)
search.add(structure.species_at_sites.has_any("O"))
results = search.results(structure=structure)

for row in results:
    print("Found", len(row.structure.species_at_sites), "sites")
```

Result rows are lazy `UnitcellStructureRecord` instances. Calling `results()`
freezes the query plan; later changes to `search` do not change this result set.

By default `store.searcher()` returns every row of every lineage but only main
entries — `only_main_alt=True` hides named alternatives. Pass `only_latest=True`
to restrict root variables to each lineage's latest revision, and
`only_main_alt=False` to include alternatives.

## Reuse, slice, and inspect result sets

Result sets can be iterated again, sliced, and indexed. Add a few distinct
structures here so the slice has its own positions:

```python
from httk.atomistic import UnitcellStructure

for element in ("Xe", "Kr", "Ar"):
    store.save(
        UnitcellStructure(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [[0, 0, 0]],
            species_at_sites=[element],
        )
    )

search = store.searcher()
structure = search.variable(UnitcellStructureRecord)
search.add(structure.species_at_sites.has_any("Xe", "Kr", "Ar"))
results = search.results(structure=structure)
tail = results[1:]
print("sizes", len(results), len(tail))
print("reuse", len(results), len(list(results)))
print("positions", results[1].structure.species_at_sites, tail[0].structure.species_at_sites)
print("first", results.first().structure.species_at_sites)

one_search = store.searcher()
one_structure = one_search.variable(UnitcellStructureRecord)
one_search.add(one_structure.species_at_sites.has_any("Xe"))
one = one_search.results(structure=one_structure).one()
print("one", one.structure.species_at_sites)
```

The slice has its own positions for iteration, `len()`, indexing, `first()`,
`one()`, and `column()`. It does not re-query the database. `one()` requires
exactly one result; it raises `NoResultError` or `MultipleResultsError`
otherwise.

## Stream a single output with `scalars()`

When a result has one output, `scalars()` yields that output directly:

```python
search = store.searcher()
structure = search.variable(UnitcellStructureRecord)
search.add(structure.species_at_sites.has_any("Xe"))
results = search.results(structure=structure)

for record in results.scalars():
    print("scalar", record.species_at_sites)
```

With multiple outputs, pass the output name to `scalars(name)` to select one
column explicitly.

## Read exact columns or explicit floats

`column(name)` exposes scalar projections without hydrating whole records. A
column of integers, `Fraction` values, or `FracScalar` values supports exact
`to_fracvector()`; `.floats()` is the explicit approximate view. Floats,
surds, strings, datetimes, and other non-rational projections are rejected by
`to_fracvector()`.

```python
from fractions import Fraction

for charge in (Fraction(1, 2), Fraction(-1, 3)):
    store.save(
        UnitcellStructure(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [[0, 0, 0]],
            species_at_sites=["Xe"],
            charge=charge,
        )
    )

search = store.searcher()
structure = search.variable(UnitcellStructureRecord)
search.add(structure.charge.is_in(Fraction(1, 2), Fraction(-1, 3)))
results = search.results(charge=structure.charge)
charges = results.column("charge")
print("exact", list(charges))
print("floats", list(charges.floats()))
print("fracvector", charges.to_fracvector())
```

Variable-length child projections are rejected when `results()` is declared;
reference-path projections are supported.

## Process rows with `cursor()`

`cursor()` bounds hydrated record/proxy objects, not the raw result values
retained by the result set. It reuses an unhashable record proxy, so a cursor
row expires when the cursor advances. Build views while the row is live, and
fill any component you will need before advancing:

```python
from httk.atomistic import UnitcellStructureView
from httk.store.backend.sql import ExpiredCursorRowError

search = store.searcher()
structure = search.variable(UnitcellStructureRecord)
search.add(structure.species_at_sites.has_any("Xe", "Kr"))
results = search.results(structure=structure)

reuse = results.cursor()
first = next(reuse).structure
second = next(reuse).structure
print("proxy reused", first is second)

cursor = results.cursor()
live = next(cursor).structure
view = UnitcellStructureView(live)
filled_before_advance = view.species_at_sites
next(cursor)
print("filled view", filled_before_advance)
try:
    live.cell
except ExpiredCursorRowError:
    print("later fill: expired")
```

Components filled into a view before advancing remain readable. A later fill
through the expired cursor row raises `ExpiredCursorRowError`.

## Use the backend-neutral low-level form

The portable protocol declares an output with `search.output(...)` and yields
plain values plus output names. SQL code will usually prefer `results()`, but
this form works across `Searcher` implementations:

```python
search = store.searcher()
structure = search.variable(UnitcellStructureRecord)
search.add(structure.species_at_sites.has_any("Xe"))
search.output(structure, "structure")

for (values,), names in search:
    print(names, values.species_at_sites)
```

See the complete low-level protocol and `cursor()` contract in the versioned
*httk-store* database guide.

## Query list fields as sets

List fields use explicit set operations. This record has two site species, so
the three predicates make their meanings visible:

```python
from httk.atomistic import UnitcellStructure

set_record = UnitcellStructure(
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    [[0, 0, 0], [1 / 2, 1 / 2, 1 / 2]],
    species_at_sites=["Xe", "O"],
)
store.save(set_record)

for operation in ("has_any", "has_only", "is_in"):
    search = store.searcher()
    structure = search.variable(UnitcellStructureRecord)
    expression = getattr(structure.species_at_sites, operation)("Xe", "O")
    search.add(expression)
    print(operation, len(search.results(structure=structure)))
```

`has_any` means at least one child value is in the set. `has_only` means every
child value is in it, and `is_in` has that same for-all meaning on a child
field. On a root field, `is_in` is ordinary membership. Negating a set
expression negates the set statement, not the whole row.

## Chain references and make self-joins

A reference path creates its join automatically. Two variables of one class
can be compared to make a self-join:

```python
from httk.atomistic import UnitcellStructure
from httk.atomistic.models.structure.semantics import StructureSymmetry

for element, spacegroup in (("Rn", 225), ("Og", 225), ("He", 62)):
    store.save(
        UnitcellStructure(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            [[0, 0, 0]],
            species_at_sites=[element],
            symmetry=StructureSymmetry(spacegroup),
        )
    )

search = store.searcher()
structure = search.variable(UnitcellStructureRecord)
search.add(structure.symmetry.space_group_it_number == 225)
print("automatic join", len(search.results(structure=structure)))

search = store.searcher()
left = search.variable(UnitcellStructureRecord)
right = search.variable(UnitcellStructureRecord)
search.add(left.species_at_sites.has_any("Rn"))
search.add(left.symmetry.space_group_it_number == right.symmetry.space_group_it_number)
search.add(right.species_at_sites.has_any("Og"))
search.output(right, "other")
print("self join", [row.other.species_at_sites for row in search.results()])
```

The first condition follows `symmetry` into its record automatically. The
second query joins two `UnitcellStructureRecord` variables through their shared
space-group value.

## Fetch an entry family through `StructureEntry`

`StructureEntry` is a logical, non-instantiable family key rather than the
concrete record class. Fetch with the family key and the stable content ID:

```python
from httk.atomistic import StructureEntry

record = store.fetch_entry(StructureEntry, restored.id)
print(type(record).__name__, record.id == restored.id)
```

An entry store can register unit-cell, fundamental-domain, and asymmetric-unit
records under the same family. `fetch_entry(StructureEntry, id)` then returns
whichever concrete record owns that structural ID, so callers need not choose a
representation-specific fetch method.

## Declare custom-record stores explicitly

A first-time store containing only private custom dataclasses declares the
empty mapping explicitly. Reopening the database loads that persisted
declaration:

```python
from httk.store import Backend, SqlStore

custom_store = SqlStore(Backend.sqlite("custom.sqlite"), entry_records={})
reopened_store = SqlStore(Backend.sqlite("custom.sqlite"))
print("custom store reopened", reopened_store is not custom_store)
```

The explicit `entry_records={}` declaration says that this is a private store
with no queryable entry families; it prevents an old or unversioned database
from being silently treated as the current storage protocol.

See the complete query DSL example in the versioned *httk-store* documentation
listed by the {doc}`module directory <../modules>`.

See also the {doc}`/data` topic page for the current storage and querying vocabulary.
