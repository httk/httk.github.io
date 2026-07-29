# Writing a new httk module

Start from the [`httk-module-template`](https://github.com/httk/httk-module-template)
repository and instantiate it for the new distribution. The template provides
the package layout, PEP 420 namespace configuration, tests, documentation
scaffolding, versioned documentation publishing, and CI/release workflows.

Keep the conventions that make modules composable: use `httk-core` for shared
contracts and dependency-free models, put external-dependency capabilities in
the appropriate module, follow the Backend/View representation pattern, and
keep data exact and immutable by default. Add a handler package when the module
needs import-time registration with a core registry. Describe public fields with
the relevant OPTIMADE definitions and keep the module's documentation lock and
release metadata current.

The aggregate site includes released module sources as submodules. It must not
copy the template's placeholder API into its reference; the template is a
starting point for a new repository, not a runtime module in this ecosystem
snapshot.
