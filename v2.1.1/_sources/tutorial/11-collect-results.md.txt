# Collect the results

The standard VASP collector reads each published `CONTCAR` and `OUTCAR`.
Collecting into SQLite stores the relaxed structures, total-energy
`DataRecord`s, provenance `Run`s, and `ProductLink`s that connect each output
to the structure it describes:

```console
httk workflow collect --into presentation.sqlite
```

The custom extractor detour is intentionally omitted here. The standard
collector already publishes the records needed for the phase diagram; custom
file formats belong in the dedicated workflow and store guides.

Here is a short store query showing what landed. Each collected `Run` carries
loose output references to its relaxed structure and total-energy record. The
SQLite table count confirms the `ProductLink`s written alongside them.

```python
import sqlite3

from httk.atomistic import StructureEntry
from httk.core import DataRecord, Run
from httk.store import Backend, SqlStore

store = SqlStore(Backend.sqlite("presentation.sqlite"))
rows = []
search = store.searcher()
run = search.variable(Run)
runs = list(search.results(run=run).scalars())
for item in runs:
    structure_edge = next(edge for edge in item.outputs if edge.entry_type == "structures")
    energy_edge = next(edge for edge in item.outputs if edge.entry_type == "_httk_records")
    structure = store.fetch_entry(StructureEntry, structure_edge.entry_id)
    record = store.fetch_by_content_id(DataRecord, energy_edge.entry_id)
    assert structure is not None and record is not None
    rows.append((structure_edge.entry_id, structure, record.value))
with sqlite3.connect("presentation.sqlite") as database:
    product_links = database.execute("SELECT COUNT(*) FROM core_product_link").fetchone()[0]
print("structures", len(rows), "energy records", len(rows))
print("runs", len(runs), "product links", product_links)
```

The `rows` values are the exact relaxed structures and the canned total-cell
energies. Page 12 joins those same identifiers and feeds them to
`PhaseDiagram.from_structures`.
