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

Modules expose capabilities through registry packages such as
`httk.registry.io`. Import-time discovery finds these packages and lets them
register loaders or entry providers with core. A feature module and its registry
package can consequently remain separate while sharing the core
registry contracts.

One typical integration path is `httk-io` → `httk-atomistic` → `httk-optimade`:
the I/O module reads a neutral file-format mapping, atomistic turns it into an
exact structure model, and an OPTIMADE adapter serves described records through
the provider contract. The layers communicate through stable core types rather
than importing one another's implementation details.

## Core design decisions

The modules in *httk₂* are independent packages, but they follow the same small set
of design contracts. These contracts are what let data move between modules,
representations, and storage systems without silently changing its meaning.

### Backends own data; views expose representations

Data-representation classes consistently follow the **Backend/View pattern**. A
backend owns the original representation and its data, while views expose that
backend through another public interface. This separates what an object *is* from
how a caller needs to work with it and allows new representations to be added
without pairwise conversion code between every class.

### Exact by default

*httk₂* does not perform lossy conversions behind the user's back. Exact values and
the original backend remain the source of truth; data is approximated or otherwise
modified only when the caller explicitly requests a lossy operation or
presentation. View round-trips retain the backend object, so constructing View B
from View A and then returning to View A recovers the original backend and preserves
its data exactly—even if View B presented an approximation.

### Immutable by default

Data-representation objects are to be treated as immutable unless their class name
starts with `Mutable`. Python cannot enforce this contract in every case, so callers
must not mutate internal data merely because an implementation detail happens to be
reachable. Immutability makes shared backends, safe views, exact round-trips, hashing,
and deduplication dependable.

### Semantic properties through OPTIMADE definitions

OPTIMADE property and entry-type definitions are central to *httk₂*. They give data
fields machine-readable identity, type, shape, units, and meaning, allowing modules,
databases, and protocol adapters to exchange semantically described records rather
than unrelated dictionaries with coincidentally similar keys.

### Storage independent of the database backend

The *httk₂* ORM stores and reconstructs ordinary frozen dataclasses through a
database-backend-agnostic API. The same domain objects and query expressions work
across supported databases; SQL generation and dialect details remain behind the
storage backend instead of leaking into the models or their callers.

### Views are usually lazy

Most views convert from their backend only when data is actually requested.
Constructing a view does not eagerly convert the underlying data, which avoids
unnecessary conversions when a view is only passed along or partially used.
