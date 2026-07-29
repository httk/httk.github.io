# Build supercells

The three v1 operations are direct `Structure` methods in v2. Each returns a
`SupercellResult`; its `.structure` is the expanded cell and the result also
records the selected integer transform and exact shape scores.

```python
from httk.atomistic import load_structure

structure = load_structure("POSCAR")

general = structure.supercell([[2, 0, 0], [0, 2, 0], [0, 0, 1]])
orthogonal = structure.orthogonal_supercell(multiplier=4)
cubic = structure.cubic_supercell(multiplier=8)

print(len(general.structure.sites), general.transformation)
print(orthogonal.orthogonality_score)
print(cubic.cubicity_score)
```

The automatic search accepts either an exact site/cell multiplier or a shape
`tolerance`: it scales up until the cell is at least that close to the target
shape. For example, `structure.orthogonal_supercell(tolerance="1/100")`
bounds the exact sum of squared pairwise cosines between the cell vectors. The
search is deterministic and bounded; coordinates and cell algebra remain
exact.

See the full supercell example in the versioned *httk-atomistic* documentation
listed by the {doc}`module directory <../modules>`.
