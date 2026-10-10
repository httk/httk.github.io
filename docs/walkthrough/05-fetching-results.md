# Fetching results back

When jobs have finished on the remote (page {doc}`04-remote-execution`), bring
them home with the same `job transfer` verb, pointed the other way. Fetching
survives interruption: the jobs stay held on the remote until the copy at home
has been adopted.

```console
httk job transfer --job JOB-UUID kappa:runs default
```

A remote source names each job by its UUID; `--job` is repeatable, and
`--tree` brings a job home together with its spawned descendants. The jobs are
first held on the remote, out of its state trees, then copied home and adopted
into the states they left, and only then is the remote hold released.

Each move is a bundle of complete job directories, checked strictly on
adoption: no symlink or special file in protocol positions, and every job's
`job.json` agreeing with the bundle manifest. A succeeded job's seal travels
inside its payload, so the seal can still be verified at home. Delivery is at
least once: an interrupted fetch is finished by re-running the same
`job transfer` command or `httk job transfer --resume`, and
`httk transfer status` lists the holds still in flight.

```{admonition} In httk v1
:class: note

`httk-tasks-receive-from-computer kappa Runs/` rsync-pulled the matching
`ht.finished/` task directories back and deleted the remote copies — no
digests, no resume, and the job's state lived only in the directory name
(`ht.task.…finished`, `ht.task.…broken`). *httk₂* holds the jobs on the source
and releases the hold only after the destination has adopted them.
```

## Collecting the fetched jobs into records

After the jobs are home, turn them into records:

```console
httk collect
```

`collect` iterates the *succeeded* jobs by default; add `--state failed`
(repeatable `--state`) to include the failures you just fetched. Each job
becomes a record: `JobRecord` is the mechanical readout of one stopped job, and
`CollectedJob` adds the workflow-declared outputs, roles, and provenance on top
of it. That provenance is what the job *observed* as it ran; externally known
inputs — like the database entity a run is *for* — are instead *declared* at
scaffold time, via `new_job`'s `provenance=` (or `new_jobs`'s per-item
provenance), and arrive in the collected `Run` untouched, with no further
steps at collection. Land the records
in a store with `--into` — that is page {doc}`06-database`:

```console
httk collect --into results.sqlite --id-base example
```

```{admonition} In httk v1
:class: note

"Sealing" in v1 was a *read-time* step: `httk.task.reader()` picked the newest
`ht.run.<timestamp>` in each `.finished` directory and built a signed
`ht.manifest.bz2` per run. *httk₂* seals each job as it succeeds, the seal
travels with the job, and provenance is recorded per job at collection, so
reading is no longer where integrity is established.
```

```{admonition} In httk v1
:class: note

Job state was a suffix on the directory name — `finished`, `broken`,
`stopped` — that you filtered by moving directories. In *httk₂* you select job
states directly on the command line with `--state succeeded --state failed`.
```

## Read next

- {doc}`../tutorial/11-collect-results` — collecting into SQLite, worked.
- {doc}`06-database` — where the collected records land.
- [Collecting](https://docs.httk.org/httk-workflow/dev/main/collecting.html) and
  [CLI details](https://docs.httk.org/httk-workflow/dev/main/details/workflow_cli.html).
- [Provenance](https://docs.httk.org/httk-workflow/dev/main/provenance.html) — the `Run` recorded per job.
