# Draw a phase diagram

`PhaseDiagram` accepts the compositions and total formula-unit energies that a
query or stored calculation record produced. Counts and energies are normalized
to per-atom values before the convex hull is built.

```python
from httk.analyse.matsci import PhaseDiagram

# These could equally be assembled from queried httk-data records.
compositions = [
    {"Li": 1},
    {"O": 1},
    {"Li": 1, "O": 1},
    {"Li": 1, "O": 3},
]
total_energies = [0.0, 0.0, -2.0, -1.0]

pd = PhaseDiagram.from_compositions(
    compositions,
    total_energies,
    ids=["Li", "O", "LiO", "LiO3"],
)

print(pd.hull_indices)
print(pd.energy_above_hull)
print(pd.phase_lines)
```

When structures themselves are already in hand, the equivalent constructor
derives each composition from `species_at_sites`. Disordered species are
weighted by concentration and vacancies do not contribute atoms.

```python
pd = PhaseDiagram.from_structures(structures, total_cell_energies)
```

Plotting is an explicit presentation boundary and needs matplotlib:

```python
ax = pd.plot()
```

Binary systems are drawn as composition--energy hulls (formation energies when
both pure endpoints exist). Systems with three or more elements use a regular
composition polygon.

The solver uses numpy `float64` linear programming for speed; the
exact arithmetic model remains in the structure layer. The equality-constrained
simplex enforces both composition and sum-of-weights normalization. Its
`phase_lines` are the complete midpoint-supported stable tie-lines, which the
v1 renderer could omit. With four or more exactly coplanar stable phases, all
supported pairs are reported, so crossing diagonals may represent more than one
equally valid triangulation.

See the materials phase-diagram API in the versioned *httk-analyse*
documentation listed by the {doc}`module directory <../modules>`.

See also the {doc}`/analysis` topic page for the current analysis vocabulary.
