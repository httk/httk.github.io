# Visualize a structure

```{admonition} Status
:class: note

There is no v2 replacement for `structure.vis.show()` or the old Jmol plugin.
The same result is available through the generic primitive view and an external
viewer such as ASE.
```

```python
from ase import Atoms
from ase.visualize import view
from httk.atomistic import StructurePrimitiveView, load_structure

lattice, positions, numbers = StructurePrimitiveView(load_structure("POSCAR"))
view(Atoms(numbers=numbers, cell=lattice, scaled_positions=positions, pbc=True))
```

`StructurePrimitiveView` is an immutable, float-valued
`(lattice, positions, atomic_numbers)` tuple. It is the intended interoperability
boundary for libraries that use the common spglib-style representation.
