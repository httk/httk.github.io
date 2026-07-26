# Load and inspect a structure

In v1, `httk.load()` returned an atomistic structure directly. In v2 the
registered reader first produces a neutral mapping and
`httk.atomistic.load_structure()` performs the domain conversion. The one-call
user experience remains:

```python
from httk.atomistic import StructureEntryProvider, load_structure

structure = load_structure("example.cif")  # POSCAR and compressed files work too
record = next(iter(StructureEntryProvider({"example": structure}).records("structures")))

print("Formula:", record["chemical_formula_reduced"])
print("Volume:", float(structure.cell.volume))
print("Species at sites:", structure.species_at_sites)
print("Reduced coordinates:", structure.sites.reduced_coords)
```

The split is architectural: *httk-io* parses file formats,
*httk-atomistic* owns `Structure`, and *httk-core* dispatches between them.
Composition fields live at the OPTIMADE/provider boundary, which is why the
short formula is obtained from `StructureEntryProvider`. Geometry remains exact
until the explicit `float(...)` used for display.

See the full
[*httk-atomistic* loading example](https://docs.httk.org/httk-atomistic/examples/load_from_poscar.html).
