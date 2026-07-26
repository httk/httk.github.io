# Build with ASE and convert to *httk₂*

The v1-specific `Structure.ase.from_Atoms` glue is gone. ASE already exposes the
three values understood by `StructureSimpleView`, so no pairwise adapter is
needed:

```python
from ase.build import fcc111
from httk.atomistic import StructureSimpleView

slab = fcc111("Al", size=(2, 2, 10), vacuum=10.0)
structure = StructureSimpleView(
    (
        slab.cell.array.tolist(),
        slab.get_scaled_positions().tolist(),
        slab.numbers.tolist(),
    )
)
```

The primitive triple contains only the lattice, reduced coordinates, and atomic
numbers. ASE constraints, calculators, tags, and other `Atoms` metadata are not
part of this conversion.

Conversion in the other direction is shown in the
{doc}`visualization step <03-visualize>`.
