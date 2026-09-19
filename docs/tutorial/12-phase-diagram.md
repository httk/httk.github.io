# Draw the Ca–Ti–O phase diagram

The collected store holds the relaxed structures and their total-energy
records, joined by the records' `product_of` edges. One query returns the
structure and energy pairs; the materials-science constructor takes them
directly, with the OPTIMADE reduced formulas (elements in alphabetical order,
so CaTiO3 reads `CaO3Ti`) as phase labels:

```python
from httk.analyse.matsci import PhaseDiagram
from httk.atomistic import UnitcellStructureView
from httk.atomistic.storage.records import UnitcellStructureRecord
from httk.core import DataRecord
from httk.store import SqliteStore

store = SqliteStore("presentation.sqlite")
search = store.searcher(only_latest=True)
structure = search.variable(UnitcellStructureRecord)
record = search.variable(DataRecord)
search.add(record.links.product_of == structure)

structures, energies = [], []
for row in search.results(structure=structure, record=record):
    structures.append(row.structure)
    energies.append(row.record.value)

labels = [UnitcellStructureView(structure).chemical_formula_reduced for structure in structures]
pd = PhaseDiagram.from_structures(structures, energies, ids=labels)
stable = {labels[index] for index in pd.hull_indices}
print("stable", sorted(stable))
print("energy above hull", dict(zip(labels, pd.energy_above_hull)))
assert stable == {"Ca", "O", "Ti", "CaO", "CaO3Ti"}
assert "OTi" not in stable
```

The join is exact provenance, not a filename convention: the edge on each
record was written by the collector from the workflow's `product_of`
curation and holds the structure's store id. The expected stable set is Ca,
O, Ti, CaO, and CaO3Ti (CaTiO3), with OTi (TiO) above the hull.

Plotting is an explicit presentation step:

```python
ax = pd.plot()
ax.figure.savefig("catio3-phase-diagram.png", dpi=160, bbox_inches="tight")
print("saved catio3-phase-diagram.png")
```

The mock values are demonstration numbers, not physics. The solver uses
`numpy.float64` linear programming for the hull; `from_structures` derives the
compositions from the collected structures and normalizes the total energies
per atom before solving.

See the materials phase-diagram API in the versioned *httk-analyse*
documentation for more analysis options.
