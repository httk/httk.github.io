# httk.github.io

The top-level documentation site for *httk₂*, published to the root of
[docs.httk.org](https://docs.httk.org). It introduces the toolkit and links to each
module; the detailed API reference for every module lives on its own per-module
subsite (e.g. `docs.httk.org/httk-core/`, `docs.httk.org/httk-atomistic/`).

Build the documentation incrementally with `make docs`. For a clean, forced
rebuild, use `make docs-full`. The incremental build skips the per-module
source pages (`sphinx.ext.viewcode`, which re-highlights every module on every
build); `make docs-full` — the published form — includes them
(`HTTK_DOCS_VIEWCODE=1`).
