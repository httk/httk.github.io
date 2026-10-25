# Finding, installing and writing workflows

A *workflow* is a package: a directory with an `httk_workflow.toml` manifest
plus the runner, hooks, and support files it names. `httk job new --workflow`
and friends resolve one from a name, a git URI, or a local directory; this
page is about where workflows come from and the manifest essentials, not
about running a campaign — see {doc}`campaigns` for that.

## Four repositories

- [workflows-vasp](https://github.com/httk/workflows-vasp) — production VASP
  workflows: `vasp.relax`, `vasp.relax-bash`, `vasp.static`,
  `vasp.relax-static`, `vasp.relax-static-coarse`, `vasp.relax-static-hse`,
  `vasp.general`, `vasp.relax-ions`, and `vasp.band-structure`, and the
  property workflows built natively on *httk-analyse*: `vasp.dos`,
  `vasp.dielectric`, `vasp.elastic`, `vasp.eos`, and `vasp.phonons` (phonopy),
  collected as typed records. `vasp.full-characterization` runs them as child
  jobs on one material: one tight relaxation, then band structure, density of
  states, elastic tensor, equation of state, dielectric response and phonons in
  parallel where they allow, sharing the self-consistent density and the Born
  charges so no VASP calculation runs twice. Use these for real calculations; no
  runner authoring needed.
- [workflows-vasp-atomate2](https://github.com/httk/workflows-vasp-atomate2) —
  atomate2's VASP Makers as workflows: `atomate2.static`, `atomate2.relax`,
  `atomate2.tight-relax`, `atomate2.double-relax`, `atomate2.band-structure`,
  `atomate2.dielectric`, `atomate2.elastic`, and `atomate2.phonons`, run through
  the jobflow realization with atomate2's input sets and custodian error handling,
  and collected as typed records (band structures, densities of states, elastic and
  dielectric tensors, phonon properties). `atomate2.full-characterization` runs
  them as child jobs on one material: a shared tight relaxation, then band
  structure, elastic tensor, dielectric response and phonons in parallel, with no
  VASP calculation run twice. Every package carries `report` and `plots`
  postprocess scripts (`httk workflow postprocess --script plots`) that write a
  summary and the figures: relaxation steps, band structures and densities of
  states, dielectric tensors and Born charges, elastic moduli and directional
  Young's modulus, phonon dispersions and thermodynamics. Use these when you want
  atomate2's protocols; they need `atomate2` where jobs run.
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
picks one workflow out of a multi-workflow repository. A job runs only a
workflow installed in its workspace; `--install` fetches and installs it there
first, and the job records the **canonical URI** with the ref expanded to the
full commit hash:

```console
httk job new --workflow 'git+https://github.com/httk/workflows-vasp#vasp-relax' \
    --install --input structure=POSCAR
```

Once installed, the manifest's `[workflow] name` (its **short name**, for
example `vasp.relax`) also resolves the workflow, as long as it is not
ambiguous between repositories. Install, list, or remove a workspace's
workflows without creating a job:

```console
httk workflow install --workspace default 'git+https://github.com/httk/workflows-vasp#vasp-relax'
httk workflow list --workspace default
httk workflow uninstall --workspace default vasp.relax
```

A `git+` URI without `#subdir`, whose repository root holds an
`httk_plugin.toml` (and no `httk_workflow.toml`), installs every workflow
package that manifest lists. Each is installed under its pinned member URI
(`…@<commit>#<subdir>`), and one `ID<TAB>NAME` line is printed per workflow:

```console
httk workflow install --workspace default 'git+https://github.com/httk/workflows-vasp-atomate2@wf-v0.2.0'
```

A call from one listed workflow to another, by name or alias, binds to the
member at the same commit. A repository whose root holds
`httk_workflow.toml` is a single package, as before, and `httk job new
--workflow` and `httk workflow describe` still need `#subdir`, since they name
one workflow. A running workspace daemon needs no reload: managers read the
workspace's installed workflows when they claim jobs.

Without `--workspace`, `httk workflow install` only fetches into this machine's
cache. Workflows do not travel with jobs by default: install them in every
workspace that runs those jobs, or embed the workflow in the job (next section).

A workflow id names one workflow, so do not reinstall different sources under
an id that unfinished jobs use. Nothing refuses it, but `httk workflow install`
warns and names those jobs, `httk job why` shows a `workflow pin` check, and
`httk collect` refuses a job whose installed tree changed since it ran, naming
the remedies.

The complete grammar, commit pinning, and short-name resolution rules are in
the [workflow URI guide](https://docs.httk.org/httk-workflow/dev/main/details/workflow_uris.html).

## Embedding a workflow in a job

A job can embed its workflow instead of naming a workspace installation. With
`--embed-workflow`, `httk job new` copies the workflow package into the job's
own `workflow/` directory and installs nothing in the workspace store. Use it
for one-off jobs (a `--from-command` template, a runner file, a package under
development) and for jobs whose code must travel and be sealed with them:

```console
httk job new --workspace WS --embed-workflow --workflow-dir ./my_relax --input structure=POSCAR
httk job new --workspace WS --embed-workflow --from-command 'my_executable {input}' --file input=a.dat
```

It works with `--workflow`, `--workflow-dir`, `--from-runner` and
`--from-command` (`embed_workflow=True` in Python), and is refused together with
`--install`. The job's workflow id is `embedded:<name>@<sha12>`, and `job.json`
pins the tree digest together with everything the manager acts on: the runner,
steps, calls and requirements, read from the manifest when the job is created.

- The embedded code runs only inside the job's sandbox. The manager, the
  workspace daemon, launch templates and build steps never read or run anything
  from `workflow/`, and the manager checks the tree against the pinned digest
  before every launch.
- `workflow/` is read-only to the running job. Collection runs the collectors
  from a verified private copy, and children that run the parent's workflow get
  their own verified copy.
- Language realizations, packages with `[workflow.build]`, and calls to workflows
  that are not installed cannot be embedded. Jobs submitted through a daemon's
  exchange cannot embed a workflow, and `set_workflow` cannot switch an
  embedded job.
- To edit one job's code, `httk job unlock` it and change `workflow/`.

Details are in the
[embedded workflows reference](https://docs.httk.org/httk-workflow/dev/main/details/workflow_packages.html#embedded-workflows).

## Package essentials

`[workflow] name` identifies the workflow; `requires = ["httk-workflow>=2.2.0"]`
declares minimum distribution versions, recorded at installation and checked
by the claiming manager (and by `httk workflow describe`), so a runner needs no
import guard — an unmet manager simply leaves the job for another one. `[workflow.runner]`
selects an executable `entry` (any executable package member; `run.py`/
`run.sh` recommended, and then the package carries no plain `run` member), an
argument-vector `command` (for a compiled, JVM, or interpreted program that
needs no bridge script, with `{package}`/`{artifacts}` placeholders), or a
language realization (CWL, PWD, jobflow, httk-v1). Inputs are staged to a
`destination` path or consumed by an `[workflow.instantiate]` hook —
required inputs are checked before it runs, it sees only the caller-supplied
parameters, and declared parameter defaults are applied only after it
returns; `[workflow.collect]` produces the declared outputs;
`[workflow.postprocess.NAME]` scripts run on request afterward; a script
that declares `outputs` can have its files stored as runs with
`httk collect WS --postprocess NAME --into STORE --id-base BASE`. A
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
makes all of them known on this machine at once (a workspace still installs
the ones it runs, and `httk workflow install --workspace WS` of the repository
URI, without `#subdir`, installs them all there); `[plugin] requires` then
applies to every workflow it bundles.

The workflow repositories are also pip-installable from a clone:
`pip install -e .` (or `pip install .`) installs their Python dependencies and
makes every workflow known to *httk₂* in that Python environment, at HEAD and
at every `wf-v*` tag, under the same commit-pinned GitHub URIs a git install
records, so jobs and workspaces move freely between machines installed either
way (see
[workflows by URI](https://docs.httk.org/httk-workflow/dev/main/details/workflow_uris.html)).

Project templates are installed the same way as plugin workflows, by URI or
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
