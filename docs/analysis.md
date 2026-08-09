# Analysis

Analysis starts with collected records, not with a new storage layer. Query a
local store using its search DSL, pass compositions and energies to
*httk-analyse*, and keep the returned hull or phase diagram as the immutable
analysis snapshot. For a binary phase diagram, the documented API is:

```python
from httk.analyse.matsci import PhaseDiagram

diagram = PhaseDiagram.from_compositions(
    [{"A": 1}, {"B": 1}, {"A": 1, "B": 1}],
    [0.0, 0.0, -2.0],
    ids=["A", "B", "AB"],
)
assert tuple(diagram.hull_indices) == (0, 1, 2)
assert diagram.energy_above_hull[2] == 0.0
```

`energy_above_hull` identifies entries above the stable lower envelope, while
`phase_lines` exposes the supported boundaries. Query stores before building a
diagram so the analysis input is explicit and reproducible. For data outside
your local store, `OptimadeStore` is the synchronous read-only OPTIMADE client;
discover an endpoint, query it, and save any resources you want to analyze
locally.

## Read next

- [Generic lower hulls](https://docs.httk.org/httk-analyse/dev/main/generic-hulls/) and [phase diagrams](https://docs.httk.org/httk-analyse/dev/main/phase-diagrams/).
- [OPTIMADE client](https://docs.httk.org/httk-serve/dev/main/optimade/client/), [data queries](https://docs.httk.org/httk-data/dev/main/db/), and [database details](https://docs.httk.org/httk-data/dev/main/details/db/).
