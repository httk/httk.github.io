# Publishing the data

Once results are in a store, publishing makes them available to others. In
*httk₂* everything that serves data lives in *httk-serve*, and everything it
serves is definition-driven: an OPTIMADE API, a static or dynamic website, a
custom OpenAPI contract, or a Dataspace Protocol catalogue. There is no single
central database to submit to — you publish the shape that fits your audience.

## An OPTIMADE API

Turn one or more entry providers into a running OPTIMADE service. For a quick
development server:

```python
from httk.serve.optimade import adapter_from_providers, serve

serve(adapter_from_providers([provider]), port=8080)
```

Serving straight from a store also works, and for real deployment
`create_asgi_app(...)` returns an app you run behind any ASGI server.

```{admonition} In httk v1
:class: note

httk v1 shipped its own OPTIMADE server, `httk.optimade.serve(store, config,
port=8080)`, serving directly from a local `httk.db` store. *httk₂* serving is
definition-driven and lives in httk-serve, with entry providers as the neutral
contract between your data and any served protocol.
```

## A website

For a public-facing site, httk-serve provides a template repository
([example_website_httk](https://github.com/httk/example_website_httk)) with
reusable widgets under `src/widgets/`, invoked in pages as `{{ widget(...) }}`.
Pages can be fully static, with the browser querying an OPTIMADE endpoint
directly, so the site needs no running backend of its own.

```{admonition} In httk v1
:class: note

httk v1 built sites with `httk.httkweb.publish(src_dir, public_dir, base_url)`
from `.httkweb`/rst templates plus `functions/*.py` handlers, and served the
dynamic form with `httk.httkweb.wsgi`. In *httk₂* this is replaced by
httk-serve's site template and widgets, and by plain static hosting.
```

## A custom API

To serve a non-OPTIMADE contract, `httk.serve.http` takes a caller-owned
OpenAPI 3.1 document and derives the routes and request/response validation from
it — you supply the schemas and one handler per operation. This is the same
mechanism behind the Dataspace Protocol support.

`httk.serve.dsp` implements a DSP 2025-1 minimal public catalogue with DCAT-AP
profiles, exposing endpoints such as `GET /dsp/.well-known/dspace-version`.
Publications are declared with `DspDatasetPublication` and served through a
`DspProvider`.

## A self-describing dataset export

To hand someone the data itself, export the store to a bundle that carries its
OPTIMADE definitions alongside the database:

```console
$ httk store export presentation.sqlite dataset.zip
```

The archive holds the SQLite snapshot plus the entry-type and property
definitions and a canonical manifest, so a consumer can read what every served
property means without the original environment or a network lookup.

```{admonition} In httk v1
:class: note

httk v1 published with `httk-project-submit`, which uploaded an Ed25519-signed
project manifest to the central openmaterialsdb.se. The *httk₂* counterparts —
signed project export bundles (`httk project export`), dataset exports, and
the DSP catalogue — none assume one central database, and none upload anywhere
on their own; you choose the distribution channel.
```

Before exporting a project built by an httk-workflow campaign, it can also be
*sealed*: a signed manifest recording what a job, workspace, or project
contained at a moment in time, so any later change to a covered byte is
detectable. `httk job seal`, `httk workspace seal`, and `httk project seal`
seal each level bottom-up, and `httk workflow seal verify` checks the result.
Sealing is distinct from exporting — it proves a finished result was not
silently altered, while `httk project export` is what packages that result
for distribution.

## Read next

- {doc}`../tutorial/14-publish`, {doc}`../tutorial/15-optimade`, and {doc}`../data`.
- [Serving providers](https://docs.httk.org/httk-serve/dev/main/optimade/serving_providers/)
  and [serving stores](https://docs.httk.org/httk-serve/dev/main/optimade/serving_stores/).
- [Site template repository](https://docs.httk.org/httk-serve/dev/main/web/site_template_repository/)
  and [widgets](https://docs.httk.org/httk-serve/dev/main/web/widgets/).
- [Serving an OpenAPI contract](https://docs.httk.org/httk-serve/dev/main/http/openapi/)
  and [the DSP catalogue](https://docs.httk.org/httk-serve/dev/main/dsp/).
