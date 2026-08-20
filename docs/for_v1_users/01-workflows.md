# Defining workflows for external codes

In httk v1 a calculation was a task-template directory you pointed at with a
`t:` reference. In *httk₂* it is a *workflow package*: a self-contained directory
whose `httk_workflow.toml` manifest is the httk-owned glue around a runner, and
whose runner is written against a small SDK. The whole directory is published
content-addressed and pinned by digest per job, so upgrading *httk₂* underneath a
queued campaign cannot change what its jobs execute.

## The quickstart shape

For VASP you do not have to author anything: the packaged `vasp-relax`
workflow (id `httk.vasp.relax`) runs VASP through three steps — prepare,
run, publish — and needs only a POSCAR and a `vasp.command` setting.

```console
$ httk project init --name quickstart
$ httk workflow workspace init . --name default
$ httk workflow job new --workflow vasp-relax --input structure=POSCAR --tag silicon
$ httk workflow workspace settings set vasp.command "$PWD/examples/mock_vasp.py"
$ httk workflow run
```

`vasp.command` is an application setting resolved most-specific-first: a job's
own `vasp.command` parameter, then `HTTK_VASP_COMMAND` in the environment, then
the workspace setting. On a real machine you would set it to something like
`"srun -n 32 vasp_std"`.

```{admonition} In httk v1
:class: note

The equivalent was a per-code shell layer. `ht_steps` scripts dispatched on
`$STEP` (start → prerelax → relax1 → relax2 → cleanup) and sourced helpers
such as `ht_tasks_api.sh` and `vasptools.sh`; the VASP invocation lived in
shell functions like `VASP_PREPARE_CALC` and `VASP_RUN_CONTROLLED`. In *httk₂*
that is the packaged runner plus the one `vasp.command` workspace setting.
```

## Authoring your own package

A package is a directory with a manifest and one executable entry:

```text
my-workflow/
├── httk_workflow.toml
└── run                    # the executable entry (any language)
```

```toml
[workflow]
id = "example.relax"

[workflow.runner]
entry = "run"
steps = ["prepare", "relax", "publish"]
initial_step = "prepare"

[workflow.inputs.structure]
destination = "POSCAR"
entry_type = "structures"

[workflow.parameters.encut]
default = 520
```

The manifest declares `[workflow]` identity, the `[workflow.runner]` (an
executable, or a `language` such as CWL, PWD, jobflow, or httk-v1),
`[workflow.inputs.*]` (staged objects), `[workflow.parameters.*]` (knobs),
`[workflow.outputs.*]`, the `[workflow.instantiate]` and `[workflow.collect]`
hooks, and `[workflow.postprocess.<NAME>]` scripts. Runners are written against
the `Runner`/`Attempt` SDK (`@run.step`, `@run.instantiate`) in Python or Bash,
or in C, C++, Fortran, Rust, Perl, Ada, or Java.

```{admonition} In httk v1
:class: note

The template directory *was* the interface. A batch template under
`Execution/tasks-templates/vasp/batch/` carried its INCAR templates inline and
an `ht.instantiate.py` executed once per structure, and was referenced as
`t:vasp/batch/vasp-relax-two`. A one-shot run went through
`httk.iface.vasp_if.prepare_single_run()`. *httk₂* replaces the directory
convention with a declared manifest and SDK steps.
```

```{admonition} In httk v1
:class: note

You do not have to rewrite an existing v1 template to use it. Wrap it
unchanged as a package with `language = "httk-v1"` and it runs under the *httk₂*
CLI — see the migration guide, §15.
```

## Read next

- <https://docs.httk.org/httk-workflow/dev/main/quickstart/> — the seven-command
  walkthrough with a mock VASP.
- <https://docs.httk.org/httk-workflow/dev/main/workflow_packages/> and
  <https://docs.httk.org/httk-workflow/dev/main/details/workflow_packages/> —
  the package manifest, every table and key.
- <https://docs.httk.org/httk-workflow/dev/main/workflow_languages/> — CWL, PWD,
  jobflow, and httk-v1 as workflow languages.
- <https://docs.httk.org/httk-workflow/dev/main/vasp_runners/> — what the
  packaged VASP runners do, their inputs, parameters, and failure codes.
- <https://docs.httk.org/httk-workflow/dev/main/sdks/> — the runner SDK
  in nine languages.
- {doc}`../campaigns` — the four-command cycle at ecosystem level.
