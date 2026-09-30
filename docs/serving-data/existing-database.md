# From an existing database

If you already have a SQL database, *httk₂* can serve it over OPTIMADE in
place. Nothing is copied or re-ingested: the tables are queried read-only, and
what you write is a map from your columns to OPTIMADE properties.

Use Python 3.12 or newer and install the modules (also included in the `httk2`
metapackage):

```bash
python -m pip install 'httk-atomistic[default]' 'httk-store[db]' httk-serve
```

`TableStore`, `MappedSource` and `adapter_from_sources` are currently
unreleased. Use matching development checkouts of `httk-core`, `httk-store`
and `httk-serve` when trying this example.

## Your database

You would normally point at your own database. To have something runnable, save
this as `make_example_db.py`; it uses the standard library to create a small
SQLite file standing in for yours. The values are **invented demonstration
values**, not real data.

```python
import sqlite3

with sqlite3.connect("materials.sqlite") as db:
    db.executescript(
        """
        CREATE TABLE materials (
            mat_id INTEGER PRIMARY KEY, formula TEXT, nsites INTEGER, band_gap REAL);
        CREATE TABLE material_elements (mat_id INTEGER, element TEXT);
        INSERT INTO materials VALUES
            (1, 'NaCl', 2, 5.0), (2, 'MgO', 2, 7.8), (3, 'NaSi', 8, 0.4),
            (4, 'GaAs', 4, 1.4), (5, 'Fe', 1, 0.0);
        INSERT INTO material_elements VALUES
            (1, 'Na'), (1, 'Cl'), (2, 'Mg'), (2, 'O'), (3, 'Na'), (3, 'Si'),
            (4, 'Ga'), (4, 'As'), (5, 'Fe');
        """
    )
```

## Map and serve

Save this as `serve_db.py`:

```python
from httk.core import PropertyDefinition, register_definition_prefix, standard_entry_type
from httk.store import ListTable, TableSource, TableStore

from httk.serve.optimade import MappedSource, adapter_from_sources, serve

store = TableStore(
    "sqlite:///materials.sqlite",
    {
        "materials": TableSource(
            "materials",
            lists={"elements": ListTable("material_elements", "mat_id", "element")},
        )
    },
)

# Custom properties need a registered prefix and a definition.
register_definition_prefix("_example_", "https://example.org/optimade/properties")
structures = standard_entry_type("structures").extended(
    {
        "_example_band_gap": PropertyDefinition.from_simple(
            "_example_band_gap",
            description="Band gap (invented demonstration value).",
            fulltype="float",
            unit="eV",
        )
    }
)

adapter = adapter_from_sources(
    store,
    {
        "structures": MappedSource(
            "materials",
            {
                "id": "mat_id",
                "chemical_formula_descriptive": "formula",
                "nsites": "nsites",
                "elements": "elements",
                "_example_band_gap": "band_gap",
            },
            fields={"nelements": lambda row: len(row["elements"])},
        )
    },
    definitions={"structures": structures},
)
serve(adapter, port=8080)
store.close()
```

The `TableStore` names the `materials` table and the child table that holds
each material's `elements`. The
`MappedSource` then has two kinds of entries. *Keys* name a column for each
served property; keyed properties are filterable and sortable (list
properties, such as `elements`, are not sortable). *Fields* are functions of a
row, for values that are computed or need overriding; here `nelements` is
derived from the element list. Fields are served but not filterable. A free-form formula column maps to `chemical_formula_descriptive`;
`chemical_formula_reduced` has a strict normalized form. The `id`
is always served as a string, and the standard OPTIMADE definitions describe
the properties. The band gap is published as the custom property
`_example_band_gap`, which is why it needs a registered prefix and an extended
definition.

Create the database and start the API:

```bash
python make_example_db.py
python serve_db.py
```

## Query it

In another terminal:

```bash
curl http://127.0.0.1:8080/v1/info/structures
curl --get http://127.0.0.1:8080/v1/structures \
  --data-urlencode 'filter=elements HAS "Na"'
curl http://127.0.0.1:8080/v1/structures/3
curl --get http://127.0.0.1:8080/v1/structures \
  --data-urlencode 'sort=-nsites' --data-urlencode 'page_limit=2'
curl --get http://127.0.0.1:8080/v1/structures \
  --data-urlencode 'filter=_example_band_gap < 1'
```

The first request lists the served properties, including `nelements` and
`elements`. The second returns the two materials containing sodium, the third
the material with id `3`, and the fourth the two largest structures with a link
to the next page. A filter such as `nelements=2` returns HTTP 501, because
`nelements` is computed and cannot be filtered in SQL.

## Limitations and next steps

- There are no revisions, alternatives or `as_of` queries.
- Computed (`fields`) properties are served but not filterable.
- Relationships and `include` need a `relationships` extractor on the
  `MappedSource`.
- Each request runs `COUNT` queries; on large tables, index the filtered
  columns.
- SQLite `LIKE` is ASCII case-insensitive.

See the [serving existing databases](https://docs.httk.org/httk-serve/dev/main/optimade/serving_existing_databases.html)
page of the serve documentation and the
[TableStore guide](https://docs.httk.org/httk-store/dev/main/details/db-tables.html)
for the details. When you want revisions, alternatives or an *httk-store*
managed database, see [Building a new database](new-database.md).
