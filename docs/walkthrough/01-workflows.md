# Defining workflows for external codes

In httk v1 a calculation was a task-template directory you pointed at with a
`t:` reference. In *httk₂* it is a *workflow package*: a self-contained directory
whose `httk_workflow.toml` manifest is the httk-owned glue around a runner, and
whose runner is written against a small SDK. The whole directory is installed
into the workspace and pinned by digest per job, so upgrading *httk₂* underneath
a queued campaign cannot change what its jobs execute.

## The quickstart shape

For VASP you do not have to author anything: the `vasp.relax` workflow
package from the [httk/workflows-vasp](https://github.com/httk/workflows-vasp)
repository runs VASP through three steps — prepare, run, publish — and needs
only a POSCAR and a `vasp.command` setting.

```console
$ httk project init --name quickstart .
$ httk workspace init --name default workspace
$ httk job new --workflow 'git+https://github.com/httk/workflows-vasp#vasp-relax' \
      --install --input structure=POSCAR --tag silicon
$ httk workspace settings set --key vasp.command --value "$PWD/examples/mock_vasp.py" default
$ httk workflow run
```

A job runs only a workflow installed in its workspace: `--install` fetches the
repository and installs the workflow there first (`httk workflow install
--workspace default URI` does the same on its own). The ref is canonicalized to
the resolved commit hash and that pinned URI is recorded on the job; afterward
the short name `vasp.relax` also works wherever a workflow is accepted.

`vasp.command` is an application setting resolved most-specific-first: a job's
own `vasp.command` parameter, then `HTTK_VASP_COMMAND` in the environment, then
the workspace setting. On a real machine you would set it to the bare program,
such as `vasp_std`; the parallel start comes from the attempt's launch prefix.

```{admonition} In httk v1
:class: note

The equivalent was a per-code shell layer. `ht_steps` scripts dispatched on
`$STEP` (start → prerelax → relax1 → relax2 → cleanup) and sourced helpers
such as `ht_tasks_api.sh` and `vasptools.sh`; the VASP invocation lived in
shell functions like `VASP_PREPARE_CALC` and `VASP_RUN_CONTROLLED`. In *httk₂*
that is the `workflows-vasp` runner plus the one `vasp.command` workspace
setting.
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
name = "example.relax"

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
or in C, C++, Fortran, Rust, Perl, Ada, or Java. A compiled or JVM runner needs
no `run` bridge script: declare `[workflow.runner] command`, an argument
vector such as `command = ["{artifacts}/relax"]` or
`command = ["java", "-cp", "{artifacts}/classes", "Relax"]`, instead of `entry`.

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
unchanged as a package with `format = "httk-v1"` and it runs under the *httk₂*
CLI — see the migration guide, §15.
```

## Read next

- <https://docs.httk.org/httk-workflow/dev/main/quickstart.html> — the eight-command
  walkthrough with a mock VASP.
- <https://docs.httk.org/httk-workflow/dev/main/workflow_packages.html> and
  <https://docs.httk.org/httk-workflow/dev/main/details/workflow_packages.html> —
  the package manifest, every table and key.
- <https://docs.httk.org/httk-workflow/dev/main/workflow_compat.html> — CWL, PWD,
  jobflow, and httk-v1 as compat formats.
- <https://github.com/httk/workflows-vasp> — the VASP workflow packages
  (`vasp.relax`, `vasp.relax-bash`, `vasp.static`, `vasp.relax-static`): what
  they do, their inputs, parameters, and failure codes.
- <https://docs.httk.org/httk-workflow/dev/main/sdks/> — the runner SDK
  in nine languages.
- {doc}`../workflows` — the three workflow repositories, URIs, and installing.
- {doc}`../campaigns` — the four-command cycle at ecosystem level.
