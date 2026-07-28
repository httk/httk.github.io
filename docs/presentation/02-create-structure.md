# Build a structure in code

The v2 constructor takes the canonical quartet directly: cell, reduced sites,
species, and the species name at each site.

```python
from httk.atomistic import Structure

structure = Structure(
    cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    sites=[
        ["1/2", "1/2", "1/2"],
        [0, 0, 0],
        ["1/2", 0, 0],
        [0, "1/2", 0],
        [0, 0, "1/2"],
    ],
    species=["Pb", "Ti", "O"],
    species_at_sites=["Pb", "Ti", "O", "O", "O"],
)
```

Bare atomic numbers are equivalent:

```python
structure = Structure(
    cell=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    sites=[["1/2", "1/2", "1/2"], [0, 0, 0], ["1/2", 0, 0], [0, "1/2", 0], [0, 0, "1/2"]],
    species=[82, 22, 8],
    species_at_sites=["Pb", "Ti", "O", "O", "O"],
)
```

Use full `Species` objects when occupancies or disorder need to be expressed:

```python
from httk.atomistic import Species

structure = Structure(
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
`(a, b, c, alpha, beta, gamma)` instead of a matrix when orientation is not
important.

See [the complete construction
example](https://docs.httk.org/httk-atomistic/examples/build_a_structure.html).
