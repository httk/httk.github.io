# The *httk₂* tutorial, based on the original *httk* v1 presentation

The original *httk* v1 presentation introduced the toolkit through a sequence
of short examples. This tutorial keeps the same order and translates each example
to the current modular *httk₂* APIs.

“Available” means the result has a current v2 route. “Partial” means useful
lower-level pieces exist but the one-call v1 integration does not. “Gap” means
there is no v2 replacement yet. Together, the gap pages form a concrete porting
checklist.

## Install the pieces used by the tutorial

The `httk2` metapackage installs the core, I/O, atomistic, analysis, and
workflow modules. Database examples additionally need *httk-store*'s SQL extra;
ASE is used only for the two visualization/interchange steps.

```console
python -m pip install httk2 "httk-store[db]" ase
```

## Porting map

| Step | v1 result | v2 status | Main v2 module |
| ---: | --- | --- | --- |
| 1 | Load and inspect a structure | Available | `httk-io` + `httk-atomistic` |
| 2 | Build a structure in code | Available | `httk-atomistic` |
| 3 | Visualize a structure | Available through ASE; no built-in viewer | `httk-atomistic` |
| 4 | Convert to/from ASE | Available through structure/ASE views | `httk-atomistic` |
| 5 | Build general, orthogonal, and cubic supercells | Available | `httk-atomistic` |
| 6 | Store structure data in SQLite | Available through representation-specific Records in SQL or MongoDB stores | `httk-store` |
| 7 | Search the local database | Available through the backend-neutral query API | `httk-store` |
| 8 | Prepare a VASP calculation | Available through packaged templates and the POSCAR writer | `httk-workflow` |
| 9 | Generate a batch | Available through instantiation parameters and campaign partitioning | `httk-workflow` |
| 10 | Send and run remotely | Available through remote adapters, precheck, and per-machine runner builds | `httk-workflow` |
| 11 | Read results into the database | Available through workflow collection or explicit extraction + record storage | `httk-workflow` + `httk-store` |
| 12 | Draw a phase diagram | Available | `httk-analyse` |
| 13 | Store custom data | Available with frozen dataclasses | `httk-store` |
| 14 | Publish a project centrally | Gap; signed local manifests are available | `httk-workflow` |
| 15 | Query OMDB directly | Partial; generic OPTIMADE clients and serving are available, but no OMDB-specific client | `httk-serve` |

```{toctree}
:maxdepth: 1
:numbered:

01-load-structure
02-create-structure
03-visualize
04-ase
05-supercells
06-store
07-search
08-prepare-vasp
09-create-batch
10-run-remotely
11-collect-results
12-phase-diagram
13-custom-data
14-publish
15-omdb
```
