# Publish a dataset or project

There are two local redistribution formats. Export the database when the
recipient needs the tutorial's data, or seal the raw-data project when the
recipient needs the project files and their signed provenance.

## Export the presentation store

The `presentation.sqlite` store from the earlier tutorial steps can be
distributed as a WAL-safe, snapshot-consistent database plus the definitions
needed to read it. The archived database is the SQLite backup snapshot, not a
byte-for-byte copy of a live database file:

```console
$ httk store export presentation.sqlite presentation-dataset.zip
exported dataset to .../presentation-dataset.zip
```

The ZIP contains:

```text
store/presentation.sqlite
definitions/entry-type-<id>.json
definitions/property-<id>.json
manifest.json
```

The manifest is canonical JSON. Its definition entries record each definition
IRI, archive path, and SHA-256; it also records the store hash, the persisted
entry-record declaration, package versions, and the snapshot timestamp. An
abbreviated real export looks like this:

```console
$ unzip -p presentation-dataset.zip manifest.json | python -m json.tool
{
    "created_at_ns": 1786483194324005731,
    "definitions": [
        {
            "id": "https://schemas.optimade.org/defs/v1.2/entrytypes/optimade/files",
            "kind": "entry_type",
            "path": "definitions/entry-type-a058ad6ffcb58e43.json",
            "sha256": "19e134bf48e786ff9b221187b5cad6f3da04a110ab77349a29d0d6ecb135ffaa"
        },
        ...
    ]
}
```

Bundling the definitions makes the dataset self-describing: a consumer does
not need the original Python environment, a running OPTIMADE service, or a
network lookup to know what each served property means, what type it has, and
which entry type it belongs to. The database remains the source of truth; the
definition files describe its declared records.

The Python API is the same operation:

```python
from httk.store import export_dataset

export_dataset("presentation.sqlite", "presentation-dataset.zip")
```

## Seal the raw-data project

To redistribute the raw inputs and project metadata, initialize the raw-data
directory as an httk project if that was not done earlier, then seal it from
inside the project:

```console
$ httk project init --name raw-data raw-data
Initialized httk project 'raw-data' in .../raw-data/httk_project
$ (cd raw-data && httk project seal ../raw-data-sealed.zip)
sealed project to .../raw-data-sealed.zip
$ httk project verify-seal raw-data-sealed.zip
self-consistent but UNAUTHENTICATED (trust-on-first-use)
public_key: ed25519:Rl+4BdLm5jyGGYiz42zchS1rWewkinzz3LJSI2Tw6lc=
fingerprint: sha256:1153e1fc042cc6f1d197e8ee5e17ee7163512aeb8bd3aa366bb846b6c448a06d
$ httk project verify-seal --expect-key sha256:1153e1fc042cc6f1d197e8ee5e17ee7163512aeb8bd3aa366bb846b6c448a06d raw-data-sealed.zip
authenticated
```

The seal contains ordinary project files, `httk_project/project.json`, the
project public key, `seal/manifest.json`, and `seal/signature`. The manifest
lists every included file and its SHA-256 plus the deterministic tree digest;
the signature is Ed25519 and carries the public key used for verification.

Private keys never leave the machine. The known identity file
`httk_project/keys/project.seed` is excluded, VCS directories are excluded,
and the defense-in-depth guard aborts if a staged path looks like private-key
material (`*.key`, `*.priv`, or `*.seed`), including imported-v1
`ht.project/keys/*.priv` paths. It also compares staged file content with the
known project seed and imported-v1 private files, catching exact and
re-encoded copies under innocent names. Arbitrarily transformed or truncated
secrets are out of scope; path and pattern exclusion is the primary
protection. The public key is safe to redistribute and lets a recipient verify
the signer and fingerprint without receiving signing authority. Verification
against only the bundled key is self-consistency/TOFU; use `--expect-key` or a
trusted key for authentication.

The Python API is available when a caller needs the report directly:

```python
from httk.core.project import seal_project, verify_seal

seal_project("raw-data-sealed.zip")
print(verify_seal("raw-data-sealed.zip"))
```

Neither operation uploads data or publishes to a central service. Upload the
resulting ZIP through the distribution channel chosen for the project.
