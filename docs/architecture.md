# Architecture

httk₂ is a PEP 420 native namespace package. The top-level `httk` package has no
implementation of its own; independently released repositories contribute
subpackages such as `httk.core`, `httk.io`, and `httk.atomistic`.

The layering rule is simple: contracts and models belong in `httk-core`, while
capabilities belong in the modules that implement them. Core therefore provides
the shared vocabulary used in signatures — vectors, datastreams, OPTIMADE
definitions, entry-provider contracts, record models, and `DataLoader` — without
external dependencies. Parsing, data management, protocol serving, and workflow
execution remain capabilities in other repositories.

Modules expose capabilities through handler packages such as
`httk.handlers.io`. Import-time discovery finds these packages and lets them
register loaders or entry providers with core. A feature module and its handler
registration package can consequently remain separate while sharing the core
registry contracts.

One typical integration path is `httk-io` → `httk-atomistic` → `httk-optimade`:
the I/O module reads a neutral file-format mapping, atomistic turns it into an
exact structure model, and an OPTIMADE adapter serves described records through
the provider contract. The layers communicate through stable core types rather
than importing one another's implementation details.
