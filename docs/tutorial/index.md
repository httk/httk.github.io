# The *httk₂* tutorial

This tutorial showcases the current modular *httk₂* APIs through a sequence of
short, practical examples.

The examples use the same vocabulary as the reference documentation, with
deeper details linked from each page.

## Install the pieces used by the tutorial

The `httk2` metapackage installs the core, I/O, atomistic, analysis, and
workflow modules. Database examples additionally need *httk-store*'s SQL extra;
ASE is used only for the two visualization/interchange steps.

```console
python -m pip install httk2 "httk-store[db]" ase
```

## Feature map

| Step | Tutorial feature | Current route | Main module |
| ---: | --- | --- | --- |
| 1 | Load and inspect a structure | One-call loading and exact inspection | `httk-io` + `httk-atomistic` |
| 2 | Build a structure in code | Native unit-cell construction | `httk-atomistic` |
| 3 | Visualize a structure | ASE interchange; no built-in viewer | `httk-atomistic` |
| 4 | Convert to/from ASE | Structure and ASE views | `httk-atomistic` |
| 5 | Build general, orthogonal, and cubic supercells | Exact supercell operations | `httk-atomistic` |
| 6 | Store structure data in SQLite | Representation-specific Records in SQL or MongoDB stores | `httk-store` |
| 7 | Search the local database | Backend-neutral query API | `httk-store` |
| 8 | Prepare a VASP calculation | Packaged templates and POSCAR preparation | `httk-workflow` |
| 9 | Generate a batch | Instantiation parameters and campaign partitioning | `httk-workflow` |
| 10 | Send and run remotely | Remote adapters, precheck, and runner builds | `httk-workflow` |
| 11 | Read results into the database | Workflow collection or explicit record storage | `httk-workflow` + `httk-store` |
| 12 | Draw a phase diagram | Composition and convex-hull analysis | `httk-analyse` |
| 13 | Store custom data | Frozen dataclasses | `httk-store` |
| 14 | Publish a project centrally | Signed local manifests; no central publisher | `httk-workflow` |
| 15 | Query an OPTIMADE server | Generic OPTIMADE client and structure loading | `httk-serve` |

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
15-optimade
```
