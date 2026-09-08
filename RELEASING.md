# Releasing `httk.github.io`

The top-site release is an ecosystem snapshot. First release each runtime module
and make sure its exact release tag is available. In this repository, update all
six submodule pointers to those tags, then run and commit both generated
inputs:

```console
make ecosystem-manifest
make docs-lock
make release-check
```

`make release-check` uses `make docs-full` for the clean, forced aggregate docs
build; use `make docs-full` directly when that release-style docs build is needed
without the other release checks.

The top-site `pyproject.toml` version and the tag must match. After the checks
pass, tag `v<version>` and push the tag. The release workflow checks the tag and
lock headers, verifies `docs/ecosystem.json` against the pinned release-tagged
submodules, builds the aggregate docs, and publishes the immutable release
directory.

For the shared **v2.1.0** release, publish packages and their versioned docs in
dependency order: *httk-core* first; then *httk-atomistic*, *httk-store*, and
*httk-workflow*; then *httk-analyse* and *httk-serve*. Before tagging each
dependent module, refresh its committed inventories from the already published
dependency release docs with `make docs-inventories`, and run
`python -m httk.core.docs check-release --tag v2.1.0` and `make docs-lock-check`.
Locally built wheels can verify a candidate installation, but do not satisfy
these public-index and published-inventory prerequisites.

Once the six modules are released, pin this site's submodules to their exact
`v2.1.0` tags and regenerate the manifest. Release the aggregate documentation,
the *httk-web.github.io* website, and the refreshed *agent-httk-skill* packages
against that snapshot. The website's package dependency also requires
*httk-serve* 2.1.0 to be available first.

If a published release needs a known repair, use the approval-gated repair
workflow. It replaces only the explicitly selected release tree and leaves
other release snapshots untouched.

Development builds are different: a push to this repository's `main` workflow
updates every submodule to its remote `main`, builds `dev:main`, and publishes
the replaceable development snapshot. The site does not rebuild from module
pushes alone; module changes enter the development snapshot on the next top-site
push.
