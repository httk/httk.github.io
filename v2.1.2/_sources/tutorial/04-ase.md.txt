# Build with ASE and convert to *httk₂*

ASE `Atoms` objects are directly accepted anywhere a `StructureLike` is expected.
The interoperability layer uses a small runtime-checkable protocol, so any
Atoms-like object with the same four methods works too:

```python
from ase.build import fcc111
from httk.atomistic import UnitcellStructureView

slab = fcc111("Al", size=(2, 2, 3), vacuum=10.0)
structure = UnitcellStructureView(slab)
```

The conversion carries the cell, reduced coordinates, atomic numbers, and periodicity.
ASE constraints, calculators, tags, and other `Atoms` metadata are not part of the
conversion.

The reverse direction presents any httk structure as an ASE `Atoms` object (and
requires ASE to be installed):

```python
from httk.atomistic import ASEAtomsView

atoms = ASEAtomsView(structure)
```

For a visualization workflow, see the
{doc}`visualization step <03-visualize>`.

See also the {doc}`/structures` topic page for the current structure vocabulary.
