# Draw the Ca–Ti–O phase diagram

The collected store contains the relaxed structure entries, total-energy
records, and product links from page 11. The `Run.outputs` edges provide the
same honest loose-reference join without assuming a SQL table layout; fetch the
two entry types and pass the resulting structures and energies to the
materials-science constructor:

```python
from math import gcd

from httk.analyse.matsci import PhaseDiagram
from httk.atomistic import StructureEntry, UnitcellStructureView
from httk.core import DataRecord, Run
from httk.store.db import Database, SqlStore

store = SqlStore(Database.sqlite("presentation.sqlite"))
structures, energies, ids = [], [], []
search = store.searcher()
run = search.variable(Run)
for item in search.results(run=run).scalars():
    structure_edge = next(edge for edge in item.outputs if edge.entry_type == "structures")
    energy_edge = next(edge for edge in item.outputs if edge.entry_type == "_httk_records")
    structure = store.fetch_entry(StructureEntry, structure_edge.entry_id)
    energy = store.fetch_by_content_id(DataRecord, energy_edge.entry_id)
    assert structure is not None and energy is not None
    structures.append(structure)
    energies.append(energy.value)
    ids.append(structure_edge.entry_id)

pd = PhaseDiagram.from_structures(structures, energies, ids=ids)
views = [UnitcellStructureView(structure) for structure in structures]

def label(structure):
    amounts = structure.composition.amount_mapping
    divisor = 0
    for amount in amounts.values():
        divisor = gcd(divisor, int(amount))
    order = sorted(amounts, key=lambda element: (element == "O", element))
    return "".join(
        element + (str(int(amounts[element]) // divisor) if int(amounts[element]) // divisor != 1 else "")
        for element in order
    )

labels = [label(structure) for structure in views]
stable = {labels[index] for index in pd.hull_indices}
print("stable", sorted(stable))
print("energy above hull", dict(zip(
    labels,
    pd.energy_above_hull,
)))
print("TiO stable", "TiO" in stable)
assert len(structures) == 6
assert stable == {"Ca", "Ti", "O", "CaO", "CaTiO3"}
assert "TiO" not in stable
```

The identifiers are content IDs, so the code does not assume filenames or
hard-code compositions or energies. To make the result readable, map the
stable IDs back to the six page-09 tags in the surrounding application; the
expected stable set is Ca, Ti, O, CaO, and CaTiO3, with TiO above the hull.

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
