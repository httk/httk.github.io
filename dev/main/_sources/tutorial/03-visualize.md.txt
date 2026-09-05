# Visualize a structure

The recommended viewer for httk structures is [CrysViz](https://github.com/CrysViz/crysviz),
a light-weight browser-based crystal structure viewer with on-device rendering.
The *httk-analyse* module provides a one-call interface to it:

```bash
python -m pip install "httk-analyse[crysviz]"
```

CrysViz opens its window through pywebview; if your platform needs a GUI
backend, install `crysviz[gtk]` or `crysviz[qt]` as well.

```python
from httk.analyse.crysviz import show
from httk.core import load

viewer = show(load("POSCAR"))
viewer.wait()
```

`show()` accepts any httk structure (or several, mixed with file paths and
`crysviz.Payload` objects), serializes each structure in memory, and returns the
started `crysviz.Viewer` as soon as its window is ready. Nothing is written to
disk and the call does not block; `viewer.wait()` blocks until the window is
closed, and the viewer also works as a context manager.

The returned viewer exposes the full CrysViz Python API, for example:

```python
with show(structure) as viewer:
    info = viewer.list_structures()[0]
    viewer.select(info.id, frame=0)
    viewer.rotate_camera(30, axis="y")
    viewer.save_image("structure.png")
```

For advanced control, `to_payload(structure, format="vasp-poscar")` (or
`format="cif"`) returns the in-memory `crysviz.Payload` to pass to
`crysviz.Viewer` yourself.

## Alternative: an external viewer through ASE

httk has no built-in viewer of its own. Any other viewer can be reached through
the generic primitive view, e.g. ASE's:

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
