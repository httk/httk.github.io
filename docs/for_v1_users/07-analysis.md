# Analyzing the data

With runs collected into a store (see {doc}`06-database`), analysis is the step
that turns records into results. In httk₂ this splits cleanly into two halves:
curated scripts that a workflow package ships alongside its runs, and your own
queries against the store using the search DSL and *httk-analyse*.

## Workflow-provided analysis

A workflow package can declare curated postprocess scripts in its
`httk_workflow.toml` under `[workflow.postprocess.<NAME>]` tables. Each names a
provider-owned executable that runs once per selected collected job. You invoke
one by its declared name:

```console
$ httk workflow postprocess WORKSPACE --script relaxation-report
```

For example, a relaxation package might declare:

```toml
[workflow.postprocess.relaxation-report]
file = "scripts/relaxation_report"
description = "write a text and JSON relaxation summary"
```

```{admonition} In httk v1
:class: note

Nothing like curated per-workflow postprocess scripts existed. Analysis code
was shipped ad hoc next to the project — a loose script the author remembered
to keep near the runs. In httk₂ the package that defines the runs also owns
its standard summaries, so they travel with it.
```

## Querying a store yourself

For your own analysis, open a store and build a query with `store.searcher()`.
The DSL binds a record class to a variable with `variable()`, adds conditions
with `add()`, names outputs in `results()`, and runs on iteration:

```python
from httk.atomistic import UnitcellStructureRecord
from httk.store.db import Database, SqlStore

store = SqlStore(Database.sqlite("presentation.sqlite"))

search = store.searcher()
structure = search.variable(UnitcellStructureRecord)
search.add(structure.species_at_sites.has_any("Ca", "Ti"))

for row in search.results(structure=structure):
    print(len(row.structure.species_at_sites), "sites")
```

`has_any` / `has_only` express set membership on variable-length fields such as
`species_at_sites`, and two variables of the same class self-join, so "another
record with the same spacegroup" is expressible directly.

```{admonition} In httk v1
:class: note

Analysis was always a hand-written script re-querying `httk.db`, with searcher
joins like `search.add(search_total_energy.structure == search_struct)` and
`search.add_all(search_struct.formula_symbols.is_in('O', 'Ca', 'Ti'))`, feeding
the result into matplotlib. The searcher DSL survives in httk-store in
recognizable form — `variable`/`add`/`output` — so this is the most familiar
corner of httk₂ for a v1 user.
```

If you would rather write a query as an OPTIMADE filter string — the same text
a remote client sends in a URL — `httk.store.query.optimade_filters` translates
one against a store's schema, so `_httk_custom_symbols HAS "O"` runs as an
ordinary search with no HTTP server in sight.

## Phase diagrams and hulls

*httk-analyse* provides the materials-science `PhaseDiagram`. Build it from
compositions or from collected structures, then read the stable set and the
per-atom energy above the hull:

```python
from httk.analyse.matsci import PhaseDiagram

diagram = PhaseDiagram.from_compositions(
    [{"A": 1}, {"B": 1}, {"A": 1, "B": 1}],
    [0.0, 0.0, -2.0],
    ids=["A", "B", "AB"],
)
assert tuple(diagram.hull_indices) == (0, 1, 2)
assert diagram.energy_above_hull[2] == 0.0

ax = diagram.plot()
```

`from_structures` derives compositions from collected structures instead.
Plotting is an explicit step: `plot()` returns a Matplotlib axes you extend or
save. For non-composition problems, `httk.analyse.generic.LowerConvexHull` is
the underlying dimension-agnostic hull, exposing `hull_indices` and
`value_above_hull`.

```{admonition} In httk v1
:class: note

The phase diagram was `httk.atomistic.StructurePhaseDiagram.create(structures,
energies)`, and you displayed it with `pd.vis.show()` — visualization lived
inside the structure classes (`httk.atomistic.vis`). In httk₂ it is
`httk.analyse.matsci.PhaseDiagram` with a plain `.plot()`; visualization no
longer lives inside the structure classes.
```

## Read next

- {doc}`../analysis` and {doc}`../tutorial/12-phase-diagram`.
- [Materials phase diagrams](https://docs.httk.org/httk-analyse/dev/main/phase-diagrams/)
  and [generic lower hulls](https://docs.httk.org/httk-analyse/dev/main/generic-hulls/).
- [Searching a store](https://docs.httk.org/httk-store/dev/main/examples/searching/)
  and [OPTIMADE filter strings](https://docs.httk.org/httk-store/dev/main/examples/optimade_filters/).
- [Workflow packages](https://docs.httk.org/httk-workflow/dev/main/details/workflow_packages/).
