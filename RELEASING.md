# Releasing `httk.github.io`

The top-site release is an ecosystem snapshot. First release each runtime module
and make sure its exact release tag is available. In this repository, update all
seven submodule pointers to those tags, then run and commit both generated
inputs:

```console
make ecosystem-manifest
make docs-lock
make release-check
```

The top-site `pyproject.toml` version and the tag must match. After the checks
pass, tag `v<version>` and push the tag. The release workflow checks the tag and
lock headers, verifies `docs/ecosystem.json` against the pinned release-tagged
submodules, builds the aggregate docs, and publishes the immutable release
directory.

If a published release needs a known repair, use the approval-gated repair
workflow. It replaces only the explicitly selected release tree and leaves
other release snapshots untouched.

Development builds are different: a push to this repository's `main` workflow
updates every submodule to its remote `main`, builds `dev:main`, and publishes
the replaceable development snapshot. The site does not rebuild from module
pushes alone; module changes enter the development snapshot on the next top-site
push.
