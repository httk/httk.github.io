# Read results into the database

Result extraction and persistence are explicit capabilities in separate
modules. A frozen record makes the relationship searchable:

For the standard workflow collector, the one-command path is:

```console
httk workflow collect --into presentation.sqlite
```

It stores collected entries, runs, and products through *httk-data*. Use an
explicit extractor when a result needs a custom record or a non-standard file
interpretation:

```python
from dataclasses import dataclass

from httk.data.db import Database, SqlStore
from httk.workflow.vasp import last_oszicar_energy


@dataclass(frozen=True)
class TotalEnergyResult:
    structure_id: str
    total_energy: float


energy = last_oszicar_energy("Runs/CaTiO3/OSZICAR")
if energy is None:
    raise ValueError("OSZICAR contains no completed ionic-step energy")

store = SqlStore(Database.sqlite("presentation.sqlite"))
store.save(TotalEnergyResult("CaTiO3", energy))
```

`last_oszicar_energy` is a small file extractor. A workflow can
also publish OUTCAR, OSZICAR, and other artifacts transactionally before this
ingestion step.

See also the {doc}`/campaigns` topic page for the current workflow vocabulary.
