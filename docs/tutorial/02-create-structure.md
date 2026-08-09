# Build a structure in code

The v2 constructor takes a cell, reduced sites, and the species at each site.
The distinct species are inferred in first-occurrence order.

```python
from httk.atomistic import UnitcellStructure

structure = UnitcellStructure(
    cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    sites=[
        ["1/2", "1/2", "1/2"],
        [0, 0, 0],
        ["1/2", 0, 0],
        [0, "1/2", 0],
        [0, 0, "1/2"],
    ],
    species_at_sites=["Pb", "Ti", "O", "O", "O"],
)
```

Bare atomic numbers are equivalent:

```python
structure = UnitcellStructure(
    cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    sites=[["1/2", "1/2", "1/2"], [0, 0, 0], ["1/2", 0, 0], [0, "1/2", 0], [0, 0, "1/2"]],
    species_at_sites=[82, 22, 8, 8, 8],
)
```

Use full `Species` objects when occupancies or disorder need to be expressed:

```python
from httk.atomistic import Species, UnitcellStructure

structure = UnitcellStructure(
    cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    sites=[
        ["1/2", "1/2", "1/2"],
        [0, 0, 0],
        ["1/2", 0, 0],
        [0, "1/2", 0],
        [0, 0, "1/2"],
    ],
    species=[
        Species(name="Pb", chemical_symbols=("Pb",), concentration=(1.0,)),
        Species(name="Ti", chemical_symbols=("Ti",), concentration=(1.0,)),
        Species(name="O", chemical_symbols=("O", "vacancy"), concentration=(0.9, 0.1)),
    ],
    species_at_sites=["Pb", "Ti", "O", "O", "O"],
)
```

Rational strings such as `"1/2"` are exact. Cell parameters can be supplied as
`(a, b, c, alpha, beta, gamma)` instead of a matrix, following the CIF
crystallographic convention: `alpha` is the angle between `b` and `c`, `beta`
between `a` and `c`, and `gamma` between `a` and `b`. httk converts the
parameters to the same right-handed Cartesian basis used by its CIF loader:
`a` points along positive x, `b` lies in the xy-plane with positive y, and `c`
has positive z. Reduced site coordinates refer to these basis vectors.

See the complete construction example in the versioned *httk-atomistic*
documentation listed by the {doc}`module directory <../modules>`.

`httk.core.load("example.cif")` returns an `ASUStructure`, the native
fundamental-domain representation of a CIF.

See also the {doc}`/structures` topic page for the current structure vocabulary.
