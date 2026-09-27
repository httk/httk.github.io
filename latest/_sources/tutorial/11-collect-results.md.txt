# Collect the results

The standard VASP collector reads each published `CONTCAR` and `OUTCAR`.
Collecting into SQLite stores the relaxed structures, the total-energy
`DataRecord`s, and the provenance `Run`s. Each energy record carries a
`product_of` edge naming the relaxed structure it describes, and each run
carries its input and output edges:

```console
httk workflow collect --into presentation.sqlite
```

The custom extractor detour is intentionally omitted here. The standard
collector already publishes the records needed for the phase diagram; custom
file formats belong in the dedicated workflow and store guides.

Here is a short store query showing what landed. Relationships are searched
through the `links` namespace: `record.links.product_of == structure` joins
every energy record to the structure it is a product of. Edges name a
structure by its store id, which all its revisions share, so `only_latest=True`
keeps one row per current pair when a later sweep revises a structure:

```python
from httk.atomistic import UnitcellStructureView
from httk.atomistic.storage.records import UnitcellStructureRecord
from httk.core import DataRecord, Run
from httk.store import SqliteStore

store = SqliteStore("presentation.sqlite")

search = store.searcher(only_latest=True)
structure = search.variable(UnitcellStructureRecord)
record = search.variable(DataRecord)
search.add(record.links.product_of == structure)
pairs = list(search.results(structure=structure, record=record))
for row in pairs:
    print(UnitcellStructureView(row.structure).chemical_formula_reduced, row.record.value)

search = store.searcher(only_latest=True)
run = search.variable(Run)
print("structures with energies", len(pairs), "runs", len(search.results(run=run)))
```

Page 12 feeds those same pairs to `PhaseDiagram.from_structures`.
