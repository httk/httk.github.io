# Search the local database

Continuing with the `StructureSummary` class and `store` from the previous
step, the v2 search DSL keeps the v1 shape: bind a variable, add conditions,
declare outputs, and iterate.

```python
search = store.searcher()
structure = search.variable(StructureSummary)
search.add(structure.nsites < 40)
search.add(structure.elements.has_any("O"))
search.output(structure, "structure")

for values, names in search:
    print("Found:", values[0].formula)
```

List fields have explicit set operations: `has_any`, `has_only`, and `is_in`.
References chain into automatic joins, and two variables of the same class form
a self-join.

See the [complete query DSL
example](https://docs.httk.org/httk-data/examples/searching.html).
