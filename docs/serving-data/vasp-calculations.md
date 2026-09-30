# From VASP calculations

This example reads a directory tree of finished VASP calculations with the
*httk₂* VASP readers, stores the results in SQLite, and serves them over
OPTIMADE. It uses the same entry layout as
[altermagnets](https://github.com/Anyterial/altermagnets): standard
`structures`, typed results at `_httk_records` linked to their relaxed
structure, one `_httk_runs` provenance run per calculation, and `files` entries
for the OUTCARs. For calculations run through *httk-workflow*, use
`httk workflow collect --into` instead (see [campaigns](../campaigns.md)).

Use Python 3.12 or newer and install the modules (also included in the `httk2`
metapackage):

```bash
python -m pip install 'httk-atomistic[default]' 'httk-store[db]' httk-serve
```

Curated result properties and serving core `Run` and `FileRecord` entries next
to your own records are currently unreleased. Use matching development
checkouts of `httk-core`, `httk-store`, `httk-atomistic` and `httk-serve` when
trying this example.

## Your calculations

You would normally point at your own tree: any layout works, as long as each
calculation directory has an `OUTCAR` (possibly compressed), a `POSCAR`, a
`CONTCAR` and, for the magnetization, an `OSZICAR`. To have something
runnable, save this as
`make_example_calculations.py`. It uses the standard library to write a small
stand-in tree with **invented numbers**, not real calculations: relaxations of
NaCl, MgO and spin-polarized Fe, a static Si run whose CONTCAR equals its
POSCAR, and a failed KCl run without a final energy. The MgO files are
bz2-compressed.

```python
import bz2
from pathlib import Path


def poscar(symbols, counts, a, positions):
    return (
        f"{' '.join(symbols)}\n1.0\n{a} 0 0\n0 {a} 0\n0 0 {a}\n"
        f"{' '.join(symbols)}\n{' '.join(map(str, counts))}\nDirect\n"
        + "".join(f"{x} {y} {z}\n" for x, y, z in positions)
    )


def outcar(energy):
    text = " vasp.6.4.1 18Apr23 (build Jan 01 2024) complex\n   ENCUT  =  520.0 eV\n"
    if energy is not None:
        text += (
            "   FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)\n"
            f"   free  energy   TOTEN  =  {energy:.8f} eV\n"
            f"   energy  without entropy=  {energy:.8f}  energy(sigma->0) =  {energy:.8f}\n"
            " General timing and accounting informations for this job:\n"
        )
    return text


def oszicar(energy, mag):
    line = f"   1 F= {energy:.8E} E0= {energy:.8E}  d E =0.000000E+00"
    return line + (f"  mag=     {mag:.4f}\n" if mag is not None else "\n")


# directory: symbols, counts, lattice parameter before and after, positions, energy, mag
CALCULATIONS = {
    "NaCl/relax": (["Na", "Cl"], [1, 1], 3.99, 4.02, [(0, 0, 0), (0.5, 0.5, 0.5)], -6.83, None),
    "MgO/relax": (["Mg", "O"], [1, 1], 3.00, 3.03, [(0, 0, 0), (0.5, 0.5, 0.5)], -11.93, None),
    "Fe/relax": (["Fe"], [1], 2.83, 2.84, [(0, 0, 0)], -8.31, 2.214),
    "Si/static": (["Si"], [2], 3.10, 3.10, [(0, 0, 0), (0.5, 0.5, 0.5)], -10.84, None),
}
for name, (symbols, counts, a0, a1, positions, energy, mag) in CALCULATIONS.items():
    directory = Path("calculations", name)
    directory.mkdir(parents=True, exist_ok=True)
    files = {
        "POSCAR": poscar(symbols, counts, a0, positions),
        "CONTCAR": poscar(symbols, counts, a1, positions),
        "OUTCAR": outcar(energy),
        "OSZICAR": oszicar(energy, mag),
    }
    for filename, text in files.items():
        if name == "MgO/relax":
            (directory / f"{filename}.bz2").write_bytes(bz2.compress(text.encode()))
        else:
            (directory / filename).write_text(text)

# A calculation that failed before its first energy: no CONTCAR, no energy.
failed = Path("calculations", "KCl/relax")
failed.mkdir(parents=True, exist_ok=True)
(failed / "POSCAR").write_text(poscar(["K", "Cl"], [1, 1], 3.15, [(0, 0, 0), (0.5, 0.5, 0.5)]))
(failed / "OUTCAR").write_text(outcar(None))
```

## The data model

Save this as `vasp_records.py`. The result record says what a calculation
produced. Its `total_energy` uses *httk₂*'s curated definition and is served as
`_httk_total_energy`; the other properties are served as `_httk_custom_*`. The
`structure` field links the result to its relaxed structure, served as
`relationships.structures`. `Indexed()` speeds up the ingest's lookups by
`source_path`.

```python
from typing import Annotated

from httk.atomistic import UnitcellStructureRecord
from httk.core import DataEntryRecord, Indexed, Property, entry_record, load_property_definition

TOTAL_ENERGY = "https://schemas.httk.org/defs/v0.1/properties/core/total_energy"


@entry_record("example.vasp_result")
class VaspResult(DataEntryRecord):
    total_energy: Annotated[float, load_property_definition(TOTAL_ENERGY)]
    total_magnetization: Annotated[
        float | None,
        Property(
            unit="mu_B",
            description="Cell magnetization of the last ionic step in OSZICAR, "
            "or null when the calculation is not collinear spin-polarized.",
        ),
    ]
    completed: Annotated[
        bool, Property(description="Whether OUTCAR ends with VASP's completion footer.")
    ]
    source_path: Annotated[
        str,
        Property(description="Calculation directory relative to the ingested tree."),
        Indexed(),
    ]
    structure: UnitcellStructureRecord
```

The ingest stores four kinds of entries per calculation:

- the initial (POSCAR) and relaxed (CONTCAR) structures as standard
  `structures`. They are stored by content, so identical cells share one entry;
- the result, linked to the relaxed structure;
- a `files` entry for the OUTCAR with its URL, name, size and media type
  (`text/plain`, left unset for a compressed OUTCAR). The SHA-256 checksum is
  stored to detect changed files, but not served;
- a run that links the initial structure as input to the relaxed structure,
  the result and the OUTCAR as outputs. The structures, results and files
  then show the run under `_httk_is_input` or `_httk_is_output`.

OPTIMADE serves metadata, not file contents: set `DATA_URL` to wherever you
host the calculation tree, so that each file `url` downloads the file.

## Ingest

Save this as `ingest_vasp.py`:

```python
import logging
from pathlib import Path

from httk.atomistic import UnitcellStructureRecord, UnitcellStructureView
from httk.atomistic.integrations.vasp import VASPStructure
from httk.atomistic.integrations.vasp.io import VASPOutputs
from httk.core import FileRecord, Run, RunEdge
from httk.core.digests import sha256_file
from httk.store import EntryIdScheme, SqliteStore
from vasp_records import VaspResult

TREE = "calculations"
DATA_URL = "https://data.example.org/calculations"  # where TREE is published
PRECISION = 5e-4  # Å; CONTCAR prints full doubles, so give the real precision


def upsert(store, cls, key, value, obj):
    """Save obj, or store it as the next revision of the latest cls entry whose key equals value."""
    search = store.searcher(only_latest=True)
    entry = search.variable(cls)
    search.add(getattr(entry, key) == value)
    previous = search.results(entry=entry).first()
    sid = store.save(obj) if previous is None else store.replace(previous.entry, obj)
    return store.fetch(cls, sid)


def save_structure(store, payload):
    sid = store.save(UnitcellStructureView(VASPStructure(payload)))
    return store.fetch(UnitcellStructureRecord, sid)


def magnetization(outputs):
    outcar = outputs.outcar
    noncollinear = outcar.parameters.get("LNONCOLLINEAR") == "T"
    steps = outputs.oszicar["ionic_steps"] if outputs.oszicar else []
    if noncollinear or outcar.noncollinear_magnetization or not steps:
        return None  # a noncollinear mag= is a vector
    if steps[-1]["mag"] is None:
        return None
    return float(steps[-1]["mag"])


def ingest(store, relative, outputs):
    """Store one calculation; return False when it did not finish."""
    outcar = outputs.outcar
    energies = outcar.final_energies
    if None in (outputs.poscar, outputs.contcar, energies.energy_sigma0) or not energies.final:
        logging.warning("skipping %s: the calculation did not finish", relative)
        return False
    initial = save_structure(store, outputs.poscar)
    relaxed = save_structure(store, outputs.contcar)
    result = VaspResult(
        total_energy=float(energies.energy_sigma0),
        total_magnetization=magnetization(outputs),
        completed=outcar.completed,
        source_path=relative,
        structure=relaxed,
    )
    result = upsert(store, VaspResult, "source_path", relative, result)
    path = Path(outcar.path)
    url = f"{DATA_URL}/{relative}/{path.name}"
    size, sha256 = path.stat().st_size, sha256_file(path)
    media_type = "text/plain" if path.name == "OUTCAR" else None  # compressed: unset
    file = FileRecord(url=url, name=path.name, size=size, media_type=media_type, sha256=sha256)
    file = upsert(store, FileRecord, "url", url, file)
    produced = [RunEdge("result", "records", result.id), RunEdge("outcar", "files", file.id)]
    if relaxed.id != initial.id:  # a static run leaves the structure unchanged
        produced.insert(0, RunEdge("relaxed_structure", "structures", relaxed.id))
    run = Run(
        source_id=f"{TREE}:{relative}",
        inputs=(RunEdge("initial_structure", "structures", initial.id),),
        outputs=tuple(produced),
    )
    upsert(store, Run, "source_id", run.source_id, run)
    return True


root = Path(TREE)
store = SqliteStore(
    "vasp.sqlite",
    records=[VaspResult, Run, FileRecord],
    entry_ids=EntryIdScheme("example", "1", type_in_base=True),
)
ingested = skipped = 0
for directory in sorted({p.parent for p in root.rglob("OUTCAR*") if p.is_file()}):
    relative = directory.relative_to(root).as_posix()
    try:
        with store.transaction(), VASPOutputs(directory, precision=PRECISION) as outputs:
            if outputs.outcar is None:  # e.g. only an OUTCAR.bak
                continue
            stored = ingest(store, relative, outputs)
    except ValueError as error:  # e.g. a malformed POSCAR
        logging.warning("skipping %s: %s", relative, error)
        stored = False
    if stored:
        ingested += 1
    else:
        skipped += 1
store.close()
print(f"ingested {ingested} calculations, skipped {skipped}")
```

A calculation is every directory with an `OUTCAR`, compressed or not. Each
one is stored in its own transaction, so an unreadable file skips only its
calculation. The
`upsert` helper finds a result by `source_path`, a file by `url` and a run by
`source_id`. It stores a new entry the first time, and afterwards a new
revision of the same entry; an unchanged calculation adds nothing. With
`type_in_base=True` the ids name their entry type, such as
`example.records-1-1` and `example.structures-1-1`.

Save this as `serve_vasp.py`:

```python
from httk.core import FileRecord, Run
from httk.serve.optimade import serve
from httk.store import SqliteStore
from vasp_records import VaspResult

store = SqliteStore("vasp.sqlite", records=[VaspResult, Run, FileRecord])
serve(store, port=8080)
store.close()
```

Create the tree, ingest it twice, and start the API:

```bash
python make_example_calculations.py
python ingest_vasp.py
python ingest_vasp.py
python serve_vasp.py
```

Each ingest warns that it skips `KCl/relax` and prints
`ingested 4 calculations, skipped 1`. The second ingest adds nothing.

## Query it

In another terminal:

```bash
curl http://127.0.0.1:8080/v1/info/_httk_records
curl --get http://127.0.0.1:8080/v1/_httk_records \
  --data-urlencode 'include=structures'
curl --get http://127.0.0.1:8080/v1/_httk_records \
  --data-urlencode 'filter=_httk_total_energy < -10'
curl http://127.0.0.1:8080/v1/_httk_runs
curl http://127.0.0.1:8080/v1/structures/example.structures-1-2
curl http://127.0.0.1:8080/v1/files
```

The first request shows `_httk_total_energy` with its curated definition and
unit `eV`, and the three `_httk_custom_*` properties. The second returns the
four results, each with `relationships.structures`, and the relaxed structures
in `included`. Fe's `_httk_custom_total_magnetization` is `2.214`. For the
others it is null and therefore omitted from the default response; request it
with `response_fields=_httk_custom_total_magnetization`. The filter returns
the MgO and Si results, `example.records-1-2` and `example.records-1-4`. The runs list has one run per calculation, with
`_httk_has_input` and `_httk_has_output` relationships; the static Si run has
no relaxed structure output. Structure `example.structures-1-2`, the relaxed
Fe cell, names its run `example.runs-1-1` under `_httk_is_output`. The files
list has the four OUTCARs, including `OUTCAR.bz2`, with URLs under `DATA_URL`;
the compressed file's null `media_type` is likewise omitted.

## Re-running a calculation

Suppose you re-run `NaCl/relax` and it ends at a new energy and cell. To try
it, stop the server, change `-6.83000000` to `-6.85000000` in
`calculations/NaCl/relax/OUTCAR` and `4.02` to `4.03` in its `CONTCAR`, then
ingest and serve again:

```bash
python ingest_vasp.py
python serve_vasp.py
curl http://127.0.0.1:8080/v1/_httk_records/example.records-1-3/_httk_revs
```

The NaCl result keeps its id `example.records-1-3` and now has
`_httk_total_energy` `-6.85`. Its two revisions are listed under `_httk_revs`.
The OUTCAR file gets a second revision as well. The new relaxed cell is a new
structure, `example.structures-1-8`, and the old one stays. The run gets a
second revision because its relaxed-structure edge changed. A run's edges name
the result and file by their stable ids, so a re-run that changes only the
energy revises the result and the file, not the run.

## Limitations and next steps

- Re-ingesting only adds. Deleted or renamed directories are not retracted,
  changing `DATA_URL` turns the files into new entries, renaming `TREE`
  likewise re-identifies the runs (their `source_id` contains it), and
  reverting a calculation to the exact content of an older revision leaves the newer
  revision as the latest. Rebuild the database from scratch in those cases.
  Calculations run through *httk-workflow* get stable ids from
  `httk workflow collect --into` and its id ledger (see
  [campaigns](../campaigns.md)).
- The total energy is VASP's `energy(sigma->0)`. With finite-temperature
  smearing, the free energy `TOTEN` is the variational quantity. Energies are
  comparable only within one computational setup.
- The magnetization is OSZICAR's `mag=` of the last ionic step, and `null` when
  OSZICAR is absent or the run is not spin-polarized. Noncollinear runs are
  recognised from OUTCAR's `LNONCOLLINEAR` flag (or its LORBIT magnetization
  blocks) and served with `null` magnetization.
- The readers assume VASP 5 or newer POSCAR files, with an element line.
- Directories that only have a `vasprun.xml` are not found. Symlinked
  directories are followed by `rglob` on Python 3.12, but not on 3.13 and
  newer.
- Failed or unfinished calculations are skipped and counted.
- Next steps: add fields from the OUTCAR prologue, such as `ENCUT`
  (`outcar.parameters`) or the functional (`outcar.xc`), and record more
  files, such as `vasprun.xml`, the same way as the OUTCAR.

See the [VASP outputs guide](https://docs.httk.org/httk-atomistic/dev/main/vasp_outputs.html)
for everything the readers provide, and [Building a new database](new-database.md)
and [From an existing database](existing-database.md) for the other ways to
serve data.
