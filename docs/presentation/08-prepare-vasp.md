# Prepare a VASP calculation

```{admonition} Status
:class: caution

V2 has dependency-free VASP work-directory preparation, but not yet the v1
one-call path from `Structure` to a complete run directory. In particular,
*httk-io* currently reads POSCAR but does not write it. Supply `Run/POSCAR` and
`Run/INCAR`, then prepare the remaining inputs explicitly.
```

```python
from httk.workflow import VaspPreparationOptions, prepare_vasp_inputs

choices = prepare_vasp_inputs(
    VaspPreparationOptions(
        pseudopotential_library="/path/to/potpaw_PBE",
        kpoint_density=40,
    ),
    directory="Run",
)
print(choices)
```

This normalizes POSCAR handedness, assembles POTCAR, writes KPOINTS, and updates
INCAR with recorded choices. Execution is separately available through
`run_vasp` or the native workflow runner API.

See the [workflow runner helpers](https://docs.httk.org/httk-workflow/runtime_helpers.html).
