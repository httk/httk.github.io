# httk₂ for users coming from httk v1

httk₂ is a ground-up rewrite of the toolkit you know from httk v1 (last
released as `httk` v1.2.0). The concepts carry over — a project anchor,
structures with exact arithmetic, task templates, computers, a database, and
an OPTIMADE server — but almost every name and boundary has moved. This page
is the map: what changed at the top level, with old→new name pairs and a link
onward for each. The lifecycle pages that follow walk the same path you took
in v1, from defining a calculation to publishing and re-consuming the results.

## One package became many

httk v1 was a single monolithic package you put on `PYTHONPATH` by sourcing
`init.shell`. httk₂ is a PEP 420 native namespace: `httk-core` supplies the
shared primitives (type dispatch, datastreams, the `DatasetLoader`), and you
add the capability modules you need — `httk-atomistic`,
`httk-store`, `httk-serve`, `httk-analyse`, `httk-workflow`. The `httk2`
metapackage installs the standard set in one step, replacing the old
`init.shell`/`PYTHONPATH` dance:

```console
$ pip install httk2
```

See {doc}`../modules` for every module and where its docs live.

## Python 2.7 became Python 3.12+

The v1 codebase was written to run under Python 2.7. httk₂ requires Python
3.12 and is fully typed. The exact-by-default arithmetic that made httk
trustworthy is retained and strengthened: exact rationals throughout, with a
view/backend layer that keeps geometry exact until you explicitly ask for a
float. See {doc}`../architecture` for the design decisions.

## The project anchor moved and kept its keys

```{admonition} In httk v1
:class: note

`httk-project-setup` created a hidden `ht.project/` directory with Ed25519
keys under `ht.project/keys/`, a `config`, `tags`, and `references`, plus a
site-level `httk.cfg` (and `~/.httk.cfg`). You edited these files by hand.
```

In httk₂ the anchor is a deliberately visible `httk_project/` created by
`httk project init`, with its manifest at `httk_project/project.json` and its
Ed25519 identity under `httk_project/keys/`. A legacy anchor is read in place:

```console
$ httk project init --name my-project
$ httk project import-v1 PATH     # reads PATH/ht.project
```

See <https://docs.httk.org/httk-core/dev/main/projects/>.

## Task templates became workflow packages

```{admonition} In httk v1
:class: note

A calculation was a task-template directory under
`Execution/tasks-templates/vasp/{single,batch}/`, referenced with the `t:`
prefix (`t:vasp/batch/vasp-relax-two`). It carried an `ht.instantiate.py` run
once per structure and `ht_steps` shell scripts, and its progress was encoded
in the *name* of the result directory
(`ht.task.<computer>.<taskid>.<step>...<status>`).
```

In httk₂ a workflow is a package: a directory with an `httk_workflow.toml`
manifest and a runner. Jobs live in a workspace with durable, transactional
records instead of state-encoding directory names, and everything is driven
through the single `httk workflow` CLI with managers. See {doc}`01-workflows`
and {doc}`03-bulk-runs`.

## Computers became remotes

```{admonition} In httk v1
:class: note

`httk-computer-setup` / `httk-computer-install` registered a cluster, with a
per-queue `config.<queue>` holding the scheduler details.
```

httk₂ models the same machines as remotes. You add, configure, and verify one
with `httk workflow remote add`, `remote configure`, and `remote check`, and a
remote owns a workspace (`kappa:runs`) whose settings include the scheduler
configuration. See {doc}`04-remote-execution`.

## The database kept its shape, gained backends

```{admonition} In httk v1
:class: note

`httk.db` provided a `SqlStore`, and result classes were annotated with
`@httk.httk_typed_init` to make them storable and queryable.
```

httk₂'s `httk-store` gives a content-addressed `SqlStore` over SQLite, DuckDB,
or PostgreSQL (and a `MongoStore`), storing plain frozen-dataclass records.
OPTIMADE property definitions are the shared vocabulary across storage,
querying, and serving. See {doc}`06-database`.

## Publishing moved to httk-serve

```{admonition} In httk v1
:class: note

`httk.httkweb` published and served project websites; `httk.optimade` was
the built-in OPTIMADE server.
```

httk₂ separates serving into `httk-serve`: OPTIMADE serving from one or more
providers, arbitrary HTTP from an OpenAPI 3.1 contract (the mechanism behind
its Data Space Protocol support), and static OPTIMADE-widget websites. See
{doc}`08-publishing`.

## New in httk₂

Some things have no v1 equivalent:

- a first-class OPTIMADE *client* for consuming published data
  ({doc}`09-optimade-client`);
- first-class provenance as `Run` records collected alongside results;
- runner SDKs in nine languages (Python, Bash, C, C++, Fortran, Rust, Perl,
  Ada, Java);
- signed detached transfers between machines.

## Bringing v1 assets along

Several import verbs read legacy assets so you do not start from scratch:

- `httk project import-v1` — imports a legacy `ht.project` anchor.
- `httk workflow project import-v1` — the same legacy `ht.project` anchor
  import, available from the workflow namespace.
- `httk workflow remote import-v1` — maps a legacy computer bundle to a
  remote; it never runs legacy shell code.
- `httk workflow config import-v1` — imports legacy configuration.
- `httk workflow v1 collect` — harvests a finished v1 result tree into records.
- the `httk-v1` workflow language — wraps an existing v1 template as a package
  (`language = "httk-v1"`), so it runs unchanged under the httk₂ CLI.

Full migration guides:
<https://docs.httk.org/httk-workflow/dev/main/httk_v1_migration_guide/>,
<https://docs.httk.org/httk-workflow/dev/main/details/httk_v1_migration_guide/>,
<https://docs.httk.org/httk-store/dev/main/migrating_from_v1/>, and
<https://docs.httk.org/httk-workflow/dev/main/v1_compatibility/>.

## The lifecycle, page by page

The rest of this section follows one calculation campaign from definition to
re-consumption, contrasting each step with how you did it in httk v1.

```{toctree}
:maxdepth: 1

01-workflows
02-ingesting-data
03-bulk-runs
04-remote-execution
05-fetching-results
06-database
07-analysis
08-publishing
09-optimade-client
```
