# Finding, installing and writing workflows

A *workflow* is a package: a directory with an `httk_workflow.toml` manifest
plus the runner, hooks, and support files it names. `httk job new --workflow`
and friends resolve one from a name, a git URI, or a local directory; this
page is about where workflows come from and the manifest essentials, not
about running a campaign — see {doc}`campaigns` for that.

## Three repositories

- [workflows-vasp](https://github.com/httk/workflows-vasp) — production VASP
  workflows: `vasp.relax`, `vasp.relax-bash`, `vasp.static`, and
  `vasp.relax-static`. Use these for real calculations; no runner authoring
  needed.
- [workflows-vasp-other-languages](https://github.com/httk/workflows-vasp-other-languages) —
  the same relaxation authored once per native SDK language, `vasp.relax-ada`
  through `vasp.relax-rust`. Use as a starting point for a compiled or JVM
  runner.
- [workflows-examples](https://github.com/httk/workflows-examples) — teaching
  packages (`examples.hello` up through a fan-out and a compose example).
  Read these to learn the package anatomy, or copy one to grow.

## Referencing a workflow by URI

```text
git+https://github.com/<org>/<repo>[@<ref>][#<subdir>]
```

`@<ref>` is a branch, tag, or commit (default branch if omitted); `#<subdir>`
picks one workflow out of a multi-workflow repository. The first reference
fetches and installs it, and the job records the **canonical URI** with the
ref expanded to the full commit hash:

```console
httk job new --workflow 'git+https://github.com/httk/workflows-vasp#vasp-relax' \
    --input structure=POSCAR
```

Once installed, the manifest's `[workflow] name` (its **short name**, for
example `vasp.relax`) also resolves the workflow, as long as it is not
ambiguous between repositories. Install, list, or forget workflows without
creating a job:

```console
httk workflow install 'git+https://github.com/httk/workflows-vasp#vasp-relax'
httk workflow list
httk workflow uninstall vasp.relax
```

The complete grammar, commit pinning, and short-name resolution rules are in
the [workflow URI guide](https://docs.httk.org/httk-workflow/dev/main/details/workflow_uris.html).

## Package essentials

`[workflow] name` identifies the workflow; `requires = ["httk-workflow>=2.2.0"]`
declares minimum distribution versions, checked both when the job is created
and again by the claiming manager, so a runner needs no import guard — an
unmet manager simply leaves the job for another one. `[workflow.runner]`
selects an executable `entry` (any executable package member; `run.py`/
`run.sh` recommended, and then the package carries no plain `run` member), an
argument-vector `command` (for a compiled, JVM, or interpreted program that
needs no bridge script, with `{package}`/`{artifacts}` placeholders), or a
language realization (CWL, PWD, jobflow, httk-v1). Inputs are staged to a
`destination` path or consumed by an `[workflow.instantiate]` hook —
required inputs are checked before it runs, it sees only the caller-supplied
parameters, and declared parameter defaults are applied only after it
returns; `[workflow.collect]` produces the declared outputs;
`[workflow.postprocess.NAME]` scripts run on request afterward. A
compiled package additionally declares `[workflow.build]`, built and
registered per machine with `httk workflow build` (see {doc}`campaigns`); the
language SDKs it builds against live under `HTTK_WORKFLOW_LANGUAGES_DIR`.

The full manifest reference — every table and key — is the
[package guide](https://docs.httk.org/httk-workflow/dev/main/workflow_packages.html)
and its [detailed reference](https://docs.httk.org/httk-workflow/dev/main/details/workflow_packages.html)
in the module docs.

## Plugins and templates

A repository can also carry an `httk_plugin.toml` listing its workflow
directories, so `httk plugin install git+https://github.com/httk/workflows-vasp`
installs all of them at once; `[plugin] requires` then applies to every
workflow it bundles. Project templates are installed the same way, by URI or
from a plugin:

```console
httk project template install git+https://github.com/org/templates@v1#starter
httk project init --template starter my-project
```

See the [plugins](https://docs.httk.org/httk-core/dev/main/plugins.html) and
[project templates](https://docs.httk.org/httk-core/dev/main/projects.html)
module documentation.

## Definition versus declaration

The canonical git URI a job was created from is its **definition** URI — the
code that ran; jobs from a local directory or a registered workflow have none.
A workflow may separately publish a **declaration**, a document
describing its inputs and outputs, named by the manifest's
`declaration_uri`. Collection records both on the `Run`, as
`workflow_definition_uri` and `workflow_declaration_uri`; see the
[provenance](https://docs.httk.org/httk-workflow/dev/main/provenance.html) and
[declarations](https://docs.httk.org/httk-workflow/dev/main/details/declarations.html)
module documentation.

## Read next

- {doc}`campaigns` — running and collecting jobs day to day.
- {doc}`walkthrough/01-workflows` — authoring a package step by step.
- [Workflow CLI](https://docs.httk.org/httk-workflow/dev/main/details/workflow_cli.html) —
  the complete `install`/`uninstall`/`list`/`describe` reference.
- [Runner SDKs](https://docs.httk.org/httk-workflow/dev/main/sdks/) — the nine
  language bridges.
