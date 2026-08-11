# Visualize a structure

```{admonition} Visualization boundary
:class: note

httk does not provide a built-in interactive viewer. Use the generic primitive
view and an external viewer such as ASE instead.
```

```python
from ase import Atoms
from ase.visualize import view
from httk.atomistic import PlainStructureView
from httk.core import load

lattice, positions, numbers = PlainStructureView(load("POSCAR"))
view(Atoms(numbers=numbers, cell=lattice, scaled_positions=positions, pbc=True))
```

`PlainStructureView` is an immutable, float-valued
`(lattice, positions, atomic_numbers)` tuple. It is the intended interoperability
boundary for libraries that use the common spglib-style representation.

See also the {doc}`/structures` topic page for the current structure vocabulary.
