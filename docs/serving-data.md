# Serve data over OPTIMADE

To publish data that is not yet in a database, import it into an *httk-store*
database and serve that. This gives the full feature set, including revisions,
alternatives and typed relationships. The walkthrough starts from CIF files and
a JSON table of results.

If you already have a SQL database, serve its tables in place instead: nothing
is copied or re-ingested, and you only write a map from columns to OPTIMADE
properties.

If you have a directory tree of finished VASP calculations, read them with the
*httk₂* VASP readers and import the structures, results, provenance runs and
output files into a new database. Re-running the import stores changed
calculations as new revisions.

```{toctree}
:maxdepth: 1

serving-data/new-database
serving-data/existing-database
serving-data/vasp-calculations
```

