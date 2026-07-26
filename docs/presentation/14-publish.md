# Publish a project

```{admonition} Porting gap
:class: warning

V2 does not currently submit a project to a central httk/OMDB service, update a
published record, or withdraw one. Do not interpret the commands below as
publication.
```

The local, cryptographic half of that workflow is available: initialize
project metadata and create or verify a deterministic signed manifest.

```console
httk workflow config init --name "A User" --email user@example.org
httk workflow project init . --name presentation --default-queue default
httk workflow project manifest create
httk workflow project manifest verify
```

The manifest records paths, sizes, hashes, empty directories, and symlink
targets, then signs the canonical body with the project's Ed25519 key. A future
publisher can consume this artifact without redefining project identity.
