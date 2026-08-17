# Fetching results back

When jobs have finished on the remote (page {doc}`04-remote-execution`), bring
them home with the same `transfer` verb, pointed the other way. Fetching is a
sealed, detached operation: it survives interruption and never corrupts the
copy in flight.

```console
httk workflow transfer kappa:runs default --state succeeded --state failed
```

`--state` (repeatable, default `succeeded` and `failed`) chooses which finished
jobs move. The finished jobs are offered, pulled home, imported, and only then
is each remote source retired.

Every transfer is a sealed bundle. It fences an explicit quiescent state, seals
it in the payload, and validates the payload digest at import; the digest pins
every path, every file's content *and executable bit*, and the literal target
of every symlink, so a runner arriving without its executable bit — or a link
retargeted in transit — is a detected mismatch, not a silent corruption. The
source is retired only after an idempotent acknowledgement. An interrupted
fetch resumes by re-running the exact same `transfer` command.

```{admonition} In httk v1
:class: note

`httk-tasks-receive-from-computer kappa Runs/` rsync-pulled the matching
`ht.finished/` task directories back and deleted the remote copies — no
digests, no resume, and the job's state lived only in the directory name
(`ht.task.…finished`, `ht.task.…broken`). httk₂ seals the transfer bundle
itself and retires the source only on acknowledgement.
```

## Collecting the fetched jobs into records

After the jobs are home, turn them into records:

```console
httk workflow collect
```

`collect` iterates the *succeeded* jobs by default; add `--state failed`
(repeatable `--state`) to include the failures you just fetched. Each job
becomes a record: `JobRecord` is the mechanical readout of one stopped job, and
`CollectedJob` adds the workflow-declared outputs, roles, and provenance on top
of it. Land the records
in a store with `--into` — that is page {doc}`06-database`:

```console
httk workflow collect --into results.sqlite
```

```{admonition} In httk v1
:class: note

"Sealing" in v1 was a *read-time* step: `httk.task.reader()` picked the newest
`ht.run.<timestamp>` in each `.finished` directory and built a signed
`ht.manifest.bz2` per run. httk₂ seals the transfer bundle when it moves and
records provenance per job at collection, so reading is no longer where
integrity is established.
```

```{admonition} In httk v1
:class: note

Job state was a suffix on the directory name — `finished`, `broken`,
`stopped` — that you filtered by moving directories. In httk₂ you select job
states directly on the command line with `--state succeeded --state failed`.
```

## Read next

- {doc}`../tutorial/11-collect-results` — collecting into SQLite, worked.
- {doc}`06-database` — where the collected records land.
- [Collecting](https://docs.httk.org/httk-workflow/dev/main/collecting/) and
  [CLI details](https://docs.httk.org/httk-workflow/dev/main/details/workflow_cli/).
- [Provenance](https://docs.httk.org/httk-workflow/dev/main/provenance/) — the `Run` recorded per job.
