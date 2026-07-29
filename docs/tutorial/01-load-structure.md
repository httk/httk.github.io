# Load and inspect a structure

In v1, `httk.load()` returned an atomistic structure directly. With
*httk-atomistic* installed, v2 provides the same one-call experience through a
format adapter registered during handler discovery:

```python
from httk.core import load
from httk.atomistic import StructureEntryProvider

structure = load("example.cif")
# POSCAR, CONTCAR, and compressed variants such as "CONTCAR.bz2" work too.
record = next(iter(StructureEntryProvider({"example": structure}).records("structures")))

print("Formula:", record["chemical_formula_reduced"])
print("Volume:", float(structure.cell.volume))
print("Species at sites:", structure.species_at_sites)
print("Reduced coordinates:", structure.sites.reduced_coords)
```

The split is architectural: *httk-io* parses file formats and returns neutral
payloads, *httk-atomistic* owns `Structure`, and *httk-core* dispatches between
them. The adapter registration makes the one-call domain-loading experience
work when *httk-atomistic* is installed. Code that needs the neutral reader
result can use the explicit escape hatch `load("example.cif", raw=True)`.
Composition fields live at the OPTIMADE/provider boundary, which is why the
short formula is obtained from `StructureEntryProvider`. Geometry remains exact
until the explicit `float(...)` used for display.

See the full *httk-atomistic* loading example in the versioned module
documentation listed by the {doc}`module directory <../modules>`.
