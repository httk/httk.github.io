# Build a structure in code

The v2 constructor takes the canonical quartet directly: cell, reduced sites,
species, and the species name at each site.

```python
from httk.atomistic import Species, Structure

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
        Species("Pb", ("Pb",), (1.0,)),
        Species("Ti", ("Ti",), (1.0,)),
        Species("O", ("O",), (1.0,)),
    ],
    species_at_sites=["Pb", "Ti", "O", "O", "O"],
)
```

Rational strings such as `"1/2"` are exact. Cell parameters can be supplied as
`(a, b, c, alpha, beta, gamma)` instead of a matrix when orientation is not
important.

See [the complete construction
example](https://docs.httk.org/httk-atomistic/examples/build_a_structure.html).
