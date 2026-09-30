# From VASP calculations

This example turns a directory tree of finished VASP calculations into an
*httk-store* database with one command, `httk collect`, and serves it over
OPTIMADE. `httk collect` walks the tree and offers each directory to the
*recognized-calculation collectors* that code packages ship. The VASP
collectors store the structures as standard `structures`, the total energies as
`_httk_records` linked to their structure, and one `_httk_runs` provenance run
per calculation. Calculations run through *httk-workflow* are collected with
the same command pointed at their workspace (see [campaigns](../campaigns.md)).

Use Python 3.12 or newer and install the modules. *httk-workflow-vasp*
provides the VASP collectors, and *httk-atomistic* the file readers they use:

```bash
python -m pip install httk-workflow-vasp 'httk-atomistic[default]' 'httk-store[db]' httk-serve
```

`httk collect` and the recognized-calculation collectors are currently
unreleased. Use matching development checkouts of `httk-core`,
`httk-atomistic`, `httk-store`, `httk-serve`, `httk-workflow` and
`httk-workflow-vasp` when trying this example.

The database's entry ids are allocated through an id ledger that is signed
with your operator identity. If you have not set one up yet, do it once:

```bash
httk init --name "Your Name" --email you@example.org
```

## Your calculations

You would normally point at your own tree. Any layout works: a calculation is
a directory with an `OUTCAR` and a `POSCAR`, and a relaxation also needs its
`CONTCAR`. Each file may be compressed. To have something runnable, save this
as `make_example_calculations.py`. It uses the standard library to write a
small stand-in tree with **invented numbers**, not real calculations. It holds
relaxations of NaCl, MgO and spin-polarized Fe, a static Si run, a molecular
dynamics run of Al, and a KCl relaxation that failed before its first energy.
The MgO files are bz2-compressed. Each OUTCAR echoes `NSW` and `IBRION` the way
VASP does, which is what the collectors classify a calculation by.

```python
import bz2
from pathlib import Path


def poscar(symbols, counts, a, positions):
    return (
        f"{' '.join(symbols)}\n1.0\n{a} 0 0\n0 {a} 0\n0 0 {a}\n"
        f"{' '.join(symbols)}\n{' '.join(map(str, counts))}\nDirect\n"
        + "".join(f"{x} {y} {z}\n" for x, y, z in positions)
    )


def outcar(nsw, ibrion, energy):
    text = (
        " vasp.6.4.1 18Apr23 (build Jan 01 2024) complex\n"
        "   ENCUT  =  520.0 eV\n"
        f"   NSW    = {nsw:6d}    number of steps for IOM\n"
        f"   IBRION = {ibrion:6d}    ionic relax: 0-MD 1-quasi-New 2-CG\n"
    )
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


# directory: symbols, counts, lattice parameter before and after, positions,
# NSW, IBRION, energy, mag
RS = [(0, 0, 0), (0.5, 0.5, 0.5)]
CALCULATIONS = {
    "NaCl/relax": (["Na", "Cl"], [1, 1], 3.99, 4.02, RS, 99, 2, -6.83, None),
    "MgO/relax": (["Mg", "O"], [1, 1], 3.00, 3.03, RS, 99, 2, -11.93, None),
    "Fe/relax": (["Fe"], [1], 2.83, 2.84, [(0, 0, 0)], 99, 2, -8.31, 2.214),
    "Si/static": (["Si"], [2], 3.10, 3.10, RS, 0, -1, -10.84, None),
    "Al/md": (["Al"], [1], 4.05, 4.05, [(0, 0, 0)], 500, 0, -3.74, None),
}
for name, (symbols, counts, a0, a1, positions, nsw, ibrion, energy, mag) in CALCULATIONS.items():
    directory = Path("calculations", name)
    directory.mkdir(parents=True, exist_ok=True)
    files = {
        "POSCAR": poscar(symbols, counts, a0, positions),
        "CONTCAR": poscar(symbols, counts, a1, positions),
        "OUTCAR": outcar(nsw, ibrion, energy),
        "OSZICAR": oszicar(energy, mag),
    }
    for filename, text in files.items():
        if name == "MgO/relax":
            (directory / f"{filename}.bz2").write_bytes(bz2.compress(text.encode()))
        else:
            (directory / filename).write_text(text)

# A relaxation that failed before its first energy: no CONTCAR, no energy.
failed = Path("calculations", "KCl/relax")
failed.mkdir(parents=True, exist_ok=True)
(failed / "POSCAR").write_text(poscar(["K", "Cl"], [1, 1], 3.15, RS))
(failed / "OUTCAR").write_text(outcar(99, 2, None))
```

```bash
python make_example_calculations.py
```

## See what will be collected

A dry run lists how each directory would be claimed, and collects nothing:

```console
$ httk collect calculations --dry-run
{"also_matched":[],"collector":"vasp.calculation.relax","directory":"Al/md","duplicate_of":null,"format":"httk-collect-claim","format_version":1,"identity":null,"kind":"unclaimed","priority":null,"reason":"molecular dynamics (IBRION = 0) is not collected yet"}
{"also_matched":[],"collector":"vasp.calculation.relax","directory":"Fe/relax","duplicate_of":null,"format":"httk-collect-claim","format_version":1,"identity":"0c110c39f7a9c5109a5adf9f6869464e2543b20ed53eb2a0856d1eada493496f","kind":"claimed","priority":10,"reason":null}
{"also_matched":[],"collector":"vasp.calculation.relax","directory":"KCl/relax","duplicate_of":null,"format":"httk-collect-claim","format_version":1,"identity":"0b9429efca48b6ce6c331568d07e6cc7bea881939f1799935f20c2018c029fce","kind":"claimed","priority":10,"reason":null}
{"also_matched":[],"collector":"vasp.calculation.relax","directory":"MgO/relax","duplicate_of":null,"format":"httk-collect-claim","format_version":1,"identity":"7553e5eb09258f6319bdf2a2dc7caaed7cb2ce0b4230a4e8d349588243d69d27","kind":"claimed","priority":10,"reason":null}
{"also_matched":[],"collector":"vasp.calculation.relax","directory":"NaCl/relax","duplicate_of":null,"format":"httk-collect-claim","format_version":1,"identity":"eac3f541d30691e845b748ee105f18576cc5f5a73b63215cd175dde561799c3a","kind":"claimed","priority":10,"reason":null}
{"also_matched":[],"collector":"vasp.calculation.static","directory":"Si/static","duplicate_of":null,"format":"httk-collect-claim","format_version":1,"identity":"578eb95dba076c0d5348ede253f883fbe88711d2115708ff13db1f3268a80501","kind":"claimed","priority":10,"reason":null}
```

Two collectors from *httk-workflow-vasp* take part: `vasp.calculation.relax`
claims the directories whose OUTCAR echoes a relaxation (`NSW > 0` and
`IBRION` 1, 2 or 3), and `vasp.calculation.static` those with `NSW = 0` or
`IBRION = -1`. `Al/md` is *unclaimed*: it is recognizably a VASP run, but
molecular dynamics is not collected yet, and the line gives that reason.
Directories that are not VASP runs at all are not listed.

The `identity` of a claimed calculation is a digest of its input files,
`INCAR`, `POSCAR`, `KPOINTS` and `POTCAR` (those present), decompressed. It
does not depend on where the directory is, so moving or renaming it keeps the
calculation's identity. A copy of a calculation elsewhere in the tree is listed
with `duplicate_of` and collected once. Two directories with the same inputs
but different OUTCARs stop the sweep with an error naming both; skip one of
them with `--exclude PATTERN`, a glob on the path relative to the tree.

`KCl/relax` is claimed although it failed: it is clearly a VASP relaxation, so
its failure is reported when it is collected rather than hidden.

## Collect into a database

```console
$ httk collect calculations --into vasp.sqlite --id-base example
Al/md: not collected by vasp.calculation.relax: molecular dynamics (IBRION = 0) is not collected yet
creating id ledger vasp.sqlite.ids.sqlite: entry ids for this store are now allocated through it and stay stable across rebuilds. Keep this file with the store (commit it alongside it) — deleting it re-mints every id.
{"directory":"Fe/relax","format":"httk-workflow-collected",...,"stored":{"entries":["example-1-5","example-1-8","example.records-1-1"],"run":"example.runs-1-1"},"unfulfilled":[],"workflow":"vasp.calculation.relax"}
...
{"collected":4,"degraded":1,"format":"httk-workflow-collect-summary","format_version":2,"revised":0,"skipped_unreadable":0,"storage_errors":0,"unclaimed":1,"unfulfilled_roles":2}
```

The command prints one JSON line per claimed calculation, named by its
`directory`, and a summary line at the end; the plain-text messages go to
standard error. The summary counts four calculations `collected` and stored,
one `degraded`, one `unclaimed` (`Al/md`), and none `revised`. The degraded one
is `KCl/relax`: its line says `"skipped":"degraded"`, nothing of it is stored,
and its `missing_collector` gives the reason, `expected workdir file
.../calculations/KCl/relax/CONTCAR`. Its two output roles, the relaxed
structure and the energy, are the two `unfulfilled_roles`. Because a
calculation was degraded, the command exits with status 1.

The first collect also creates `vasp.sqlite.ids.sqlite`, the id ledger. It
records which id each calculation's records and run were given, and keeps
those ids when you collect again or rebuild the database from scratch. Keep it
next to the database, and back it up or commit it with it: deleting it
re-numbers every entry.

Per calculation, the database now holds:

- the initial structure (POSCAR) and, for a relaxation, the relaxed structure
  (CONTCAR), as standard `structures`. They are read at a precision taken from
  the OUTCAR's echo: the magnitude of `EDIFFG` for a relaxation (or of
  `EDIFF` when `EDIFFG` is zero or absent), else of `EDIFF`; 0.001 Å when
  neither is echoed, as here. They are stored by content, so identical cells
  share one entry. The store numbers them, as in `example-1-5`;
- the total energy in eV as a record, `example.records-1-1` for Fe, linked to
  the structure it was computed for by a `product_of` edge. For a relaxation
  that is the relaxed structure, for the static Si run the initial one;
- one run, `example.runs-1-1` for Fe, with the initial structure as its input
  and the relaxed structure and the energy as its outputs. It is identified
  as `vasp.calculation.relax:<identity>`.

Collecting again adds nothing. Run the same command a second time: it prints
the same ids and the same summary, with `"revised":0`, and the database is
unchanged.

## Serve and query

The database remembers what it holds, so serving it needs no record classes.
Save this as `serve_vasp.py`:

```python
from httk.serve.optimade import serve
from httk.store import SqliteStore

store = SqliteStore("vasp.sqlite")
serve(store, port=8080)
store.close()
```

```bash
python serve_vasp.py
```

In another terminal:

```bash
curl http://127.0.0.1:8080/v1/info
curl http://127.0.0.1:8080/v1/info/_httk_records
curl --get http://127.0.0.1:8080/v1/_httk_records \
  --data-urlencode 'filter=_httk_total_energy < -10'
curl --get http://127.0.0.1:8080/v1/_httk_records \
  --data-urlencode 'sort=_httk_total_energy' --data-urlencode 'include=structures'
curl --get http://127.0.0.1:8080/v1/structures \
  --data-urlencode 'filter=elements HAS "Na"'
curl http://127.0.0.1:8080/v1/_httk_runs/example.runs-1-3
curl --get http://127.0.0.1:8080/v1/_httk_runs \
  --data-urlencode 'filter=_httk_source_id STARTS "vasp.calculation.static"'
```

The first request lists the entry types `structures`, `_httk_records` and
`_httk_runs`, and the endpoints for their revisions and alternatives. The
second describes the records. Their value property is `_httk_total_energy`,
served under *httk₂*'s curated definition
`https://schemas.httk.org/defs/v0.1/properties/core/total_energy`, with unit
`eV` and `sortable: true`. The definition says what the number means: the
total energy as produced by a calculation, whose zero is method- and
code-specific.

The filter returns the two records below -10 eV, `example.records-1-2`
(-11.93, MgO) and `example.records-1-4` (-10.84, Si). The sorted request
returns all four from the lowest energy up: `example.records-1-2` (-11.93),
`example.records-1-4` (-10.84), `example.records-1-1` (-8.31, Fe) and
`example.records-1-3` (-6.83, NaCl). Each names its structure under
`_httk_product_of`, and `include=structures` puts those four structures in
`included`.

The structure filter returns the two NaCl cells: `example-1-20`, the POSCAR
cell with lattice parameter 3.99, which names the NaCl run under
`_httk_is_input`, and `example-1-17`, the CONTCAR cell with 4.02, which names
it under `_httk_is_output` and names the energy record `example.records-1-3`
under `_httk_has_product`. The next request is that run. Its `_httk_source_id`
is `vasp.calculation.relax:eac3f541…`, its `_httk_has_input` is `example-1-20`
labelled `initial_structure`, and its `_httk_has_output` is `example-1-17`
(`relaxed_structure`) and `example.records-1-3` (`total_energy`). The last
filter returns the one static run, `example.runs-1-4`.

## Re-running a calculation

Suppose you re-run `NaCl/relax` in place and it ends at a new energy and cell.
To try it, change `-6.83000000` to `-6.85000000` in
`calculations/NaCl/relax/OUTCAR` and `4.02` to `4.03` in its `CONTCAR`. The
inputs are unchanged, so it is the same calculation. Collect again; the server
can keep running:

```console
$ httk collect calculations --into vasp.sqlite --id-base example
...
{"collected":4,"degraded":1,"format":"httk-workflow-collect-summary","format_version":2,"revised":1,"skipped_unreadable":0,"storage_errors":0,"unclaimed":1,"unfulfilled_roles":2}
$ curl http://127.0.0.1:8080/v1/_httk_records/example.records-1-3/_httk_revs
```

One calculation was `revised`: the `NaCl/relax` line carries `"revised":true`.
Its energy record keeps the id `example.records-1-3` and gains a second
revision, and the revisions request lists both: `example.records-1-3~1` with
`_httk_total_energy` -6.83 and `_httk_product_of` `example-1-17`, and
`example.records-1-3~2` with -6.85 and `example-1-26`. The new relaxed cell is
a new structure, `example-1-26`, and the old one stays. The run keeps the id
`example.runs-1-3` and gains a second revision whose output is the new cell. A
re-run that changes only the energy revises the record, but not the run, whose
edges name the record by its id.

Changing an input is different: `cp CONTCAR POSCAR` followed by a new run
gives the directory a new identity, so it is collected as a new calculation.

## Collecting more than the standard collector does

A collector is a small package directory: a manifest, `httk_workflow.toml`, a
`recognize.py` hook that claims directories and a `collect.py` hook that reads
them. To collect more, copy the installed relaxation collector and extend it:

```bash
cp -r "$(python -c 'from httk.core.register import collector_support; print(collector_support("vasp.calculation.relax").path())')" my-vasp-relax
```

The manifest declares the collector's name, `vasp.calculation.relax`, its
markers and priority under `[workflow.recognize]`, the input role
`initial_structure`, and the outputs `relaxed_structure` and `total_energy`.
Add a third output at the end of `my-vasp-relax/httk_workflow.toml`:

```toml
[workflow.outputs.total_magnetization]
entry_type = "records"
role = "total_magnetization"
description = "The cell magnetization of the last ionic step in OSZICAR, in Bohr magnetons."
product_of = "relaxed_structure"
```

and replace `my-vasp-relax/collect.py` with this version. It reads the three
standard outputs exactly as the shipped hook does, and adds the magnetization,
OSZICAR's `mag=` of the last ionic step:

```python
"""Collect a finished VASP relaxation, with the magnetization from OSZICAR."""

import httk.core
from httk.codes.vasp.collect import read_structure, read_total_energy, structure_precision
from httk.core import DataRecord

MAGNETIZATION = "https://example.org/properties/total_magnetization"


def collect(record):
    precision = structure_precision(record.result_file("OUTCAR").parent)
    outputs = {
        "initial_structure": read_structure(record.result_file("POSCAR"), precision=precision),
        "relaxed_structure": read_structure(record.result_file("CONTCAR"), precision=precision),
        "total_energy": read_total_energy(record.result_file("OUTCAR")),
    }
    steps = httk.core.load(record.result_file("OSZICAR"), raw=True)["ionic_steps"]
    if steps and steps[-1]["mag"] is not None:  # no mag= unless spin-polarized
        outputs["total_magnetization"] = DataRecord.from_value(
            MAGNETIZATION, "_example_total_magnetization", float(steps[-1]["mag"])
        )
    return outputs
```

`record.result_file` finds a file in the calculation directory, compressed or
not. Keep the structures read at the same precision as the shipped collector:
a structure read differently is different content, so every relaxation would
get new structure entries and a revised run. The magnetization is a
`DataRecord` under a definition IRI and property name of your own. Collect
with your collector:

```console
$ httk collect calculations --into vasp.sqlite --id-base example --collector ./my-vasp-relax
...
{"collected":4,"degraded":1,"format":"httk-workflow-collect-summary","format_version":2,"revised":1,"skipped_unreadable":0,"storage_errors":0,"unclaimed":1,"unfulfilled_roles":5}
```

Your collector has the same name as the shipped one, so it replaces it for
this sweep, and every relaxation keeps its identity and ids: the name is part
of each calculation's key. Fe gains the magnetization record
`example.records-1-5`, and its run `example.runs-1-1` a second revision with
that record as a third output. NaCl and MgO print no `mag=`, so their
`total_magnetization` role stays unfulfilled, which the summary counts but
does not treat as a failure.

The magnetization is stored, but it is not served: unlike
`_httk_total_energy`, its definition is not registered with *httk₂*. The
served `/info/_httk_records` has no `_example_total_magnetization`, and the
record itself is served with its id and relationships only; sorted by
`_httk_total_energy`, it comes last, after the four energies. Serving it takes a
typed record class for the property, registered for the `records` family the
way *httk₂*'s own `TotalEnergyRecord` is; there is no shortcut for that yet.
Read it from the database instead. Save this as `show_magnetization.py`:

```python
from httk.atomistic import UnitcellStructureRecord, UnitcellStructureView
from httk.core import DataRecord
from httk.store import SqliteStore

with SqliteStore("vasp.sqlite") as store:
    search = store.searcher(only_latest=True)
    structure = search.variable(UnitcellStructureRecord)
    record = search.variable(DataRecord)
    search.add(record.name == "_example_total_magnetization")
    search.add(record.links.product_of == structure)
    for row in search.results(structure=structure, record=record):
        formula = UnitcellStructureView(row.structure).chemical_formula_reduced
        print(formula, row.structure.id, row.record.id, row.record.value)
```

```console
$ python show_magnetization.py
Fe example-1-5 example.records-1-5 2.214
```

Pass `--collector` on every later collect. A collect without it uses the
shipped collector again, which stores nothing new for Fe: its run's older
revision, without the magnetization, is not restored (see the limitations
below). A collector with a different name would claim the same directories at
the same priority, which stops the sweep unless `--prefer NAME` picks one. It
would also give the calculations new keys, so they would get new runs.

## Limitations and next steps

- Re-collecting only adds. A calculation directory deleted since the last
  collect is not retracted, and a calculation whose files return to the exact
  content of an older revision keeps the newer revision as the latest. Rebuild
  the database in those cases: delete `vasp.sqlite`, keep
  `vasp.sqlite.ids.sqlite`, and collect again. Records and runs keep their ids
  through the ledger; structures are numbered by the store as they are stored,
  so their ids can change.
- A database collected by a development version from before total energies
  were typed records is refused with "predates typed records"; rebuild it the
  same way.
- A calculation's identity comes from its inputs. `cp CONTCAR POSCAR` and a
  new run make a new calculation, and two directories with the same inputs
  but different OUTCARs stop the sweep until one is excluded.
- The total energy is VASP's `energy(sigma->0)`. With finite-temperature
  smearing, the free energy `TOTEN` is the variational quantity. Energies are
  comparable only within one computational setup.
- Files are read by their exact names, apart from a compression suffix: a
  directory with `outcar` instead of `OUTCAR` is reported as unclaimed, "no
  OUTCAR".
- Molecular dynamics (`IBRION = 0`) and other `IBRION` values are not
  collected yet, and neither are directories with only a `vasprun.xml`.
  Directories whose names start with `.` and symlinked directories are not
  visited.
- Properties of your own are stored and readable from Python, but served only
  once a typed record class is registered for them.
- The readers assume VASP 5 or newer POSCAR files, with an element line.

See [collecting recognized calculations](https://docs.httk.org/httk-workflow/dev/main/collecting.html#recognized-calculations)
for the collector package format and the Python API, and
[Building a new database](new-database.md) and
[From an existing database](existing-database.md) for the other ways to serve
data.
