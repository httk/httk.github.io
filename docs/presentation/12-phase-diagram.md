# Draw a phase diagram

```{admonition} Porting gap
:class: warning

There is currently no v2 equivalent of `StructurePhaseDiagram.create(...)` or
its visualization plugin. *httk-data* can store and query the structures,
compositions, and energies needed to build a convex hull, but the atomistic
phase-diagram model and renderer have not been ported.
```

Keeping this step explicit prevents database storage from being mistaken for
the scientific analysis that consumes it. A future phase-diagram capability
should live in a domain module, consume neutral stored records, and keep
plotting as a presentation boundary.
