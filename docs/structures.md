# Structures and file formats

Load a structure in one call with `UnitcellStructureView("file.cif")`. The
registered *httk-atomistic* readers cover CIF, POSCAR/CONTCAR, OUTCAR, and
WAVECAR; use the neutral `httk.atomistic.io` reader when you need format-level
data instead of an atomistic structure.

Views are immutable, multi-format access to one backend, so a structure can be
read as a unit cell or as a plain `(lattice, positions, numbers)` triple. The
unit-cell backend stays exact by default; `PlainStructureView` eagerly converts
to a lossy float triple for interoperability, while other numeric views are
chosen explicitly when that presentation is wanted.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from httk.atomistic import PlainStructureView, UnitcellStructureView

cif = """data_nacl
_cell_length_a 5.64
_cell_length_b 5.64
_cell_length_c 5.64
_cell_angle_alpha 90
_cell_angle_beta 90
_cell_angle_gamma 90
loop_
_space_group_symop_operation_xyz
'x, y, z'
loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Na1 Na 0 0 0
Cl1 Cl 0.5 0.5 0.5
"""

with TemporaryDirectory() as directory:
    path = Path(directory) / "NaCl.cif"
    path.write_text(cif)
    unitcell = UnitcellStructureView(path)
    lattice, positions, numbers = PlainStructureView(unitcell)
```

An asymmetric unit records a space group and one representative per symmetry
orbit; expand it to a full unit cell only when the calculation needs it.
Precision is a recorded claim from the source digits or stated uncertainties,
not a universal tolerance. Use exact integer supercell transformations when a
larger cell is needed. Bridges expose the same data to ASE and pymatgen without
making either library the structure model.

## Read next

- [Core views](https://docs.httk.org/httk-core/dev/main/view_backend_pattern/) and [view details](https://docs.httk.org/httk-core/dev/main/details/view_backend_pattern/); [datastreams](https://docs.httk.org/httk-core/dev/main/datastreams/) and [details](https://docs.httk.org/httk-core/dev/main/details/datastreams/).
- [Atomistic structures](https://docs.httk.org/httk-atomistic/dev/main/structures/), [asymmetric units](https://docs.httk.org/httk-atomistic/dev/main/asu/), [precision](https://docs.httk.org/httk-atomistic/dev/main/precision/), and [periodicity](https://docs.httk.org/httk-atomistic/dev/main/periodicity/).
- [Structure details](https://docs.httk.org/httk-atomistic/dev/main/details/structures/), [ASU details](https://docs.httk.org/httk-atomistic/dev/main/details/asu/), [precision details](https://docs.httk.org/httk-atomistic/dev/main/details/precision/), and [periodicity details](https://docs.httk.org/httk-atomistic/dev/main/details/periodicity/).
- [CIF](https://docs.httk.org/httk-atomistic/dev/main/cif/), [POSCAR](https://docs.httk.org/httk-atomistic/dev/main/poscar/), [VASP outputs](https://docs.httk.org/httk-atomistic/dev/main/vasp_outputs/), and [WAVECAR](https://docs.httk.org/httk-atomistic/dev/main/wavecar/) readers.
