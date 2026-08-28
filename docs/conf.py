import json
import importlib
import os
import warnings
from datetime import date
from pathlib import Path

from sphinx.deprecation import RemovedInSphinx10Warning
warnings.filterwarnings("ignore", category=RemovedInSphinx10Warning)

# The notebooks are executed by a Jupyter kernel whose working directory is the
# notebook's own folder, not this project root. Any relative PYTHONPATH entry (used
# in local builds to point at a sibling module checkout, e.g. ../httk-atomistic/src)
# would fail to resolve there, so normalize PYTHONPATH to absolute paths before the
# kernel subprocess inherits it. Relative entries are resolved against the project
# root (this conf.py's parent directory), which is where such a PYTHONPATH is meant
# to be interpreted. This is a no-op in CI, where the modules are pip-installed and
# PYTHONPATH is unset.
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_pythonpath = os.environ.get("PYTHONPATH")
if _pythonpath:
    os.environ["PYTHONPATH"] = os.pathsep.join(
        os.path.join(_project_root, entry) if entry and not os.path.isabs(entry) else entry
        for entry in _pythonpath.split(os.pathsep)
    )

project = "httk₂"
author = "The httk₂ AUTHORS"
copyright = f"{date.today().year}, {author}"

extensions = [
    # Core API docs
    "sphinx.ext.autodoc",        # pull docstrings
    "sphinx.ext.autosummary",    # API summary tables + stub gen
    "sphinx.ext.napoleon",       # Google/NumPy docstrings
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",        # math rendering via MathJax

    # Nice-to-haves
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",

    # Markdown + notebooks
    "myst_nb",                   # .ipynb support

    "autoapi.extension",
    "httk.core.docs.sphinx_ext",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "**/.ipynb_checkpoints"]

# Autosummary: generate stub pages automatically
autosummary_generate = True

# Autodoc defaults (tweak to taste)
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": False,
    "show-inheritance": True,
}
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_typehints_format = "short"  # no-op under AutoAPI 3.8 (annotations render fully qualified); kept for intent
typehints_fully_qualified = False
typehints_document_rtype = True
typehints_defaults = "comma"
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_attr_annotations = True

# MyST / Markdown configuration (math + nice syntax)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "substitution",
    "tasklist",
    "dollarmath",  # enables $...$ and $$...$$
]
myst_heading_anchors = 3

# Execute the example notebooks as part of the strict docs build, so that an
# example incompatible with the httk-core / httk-atomistic APIs fails the build.
nb_execution_mode = "force"
# Cells default to myst-nb's 30 s timeout, which sits too close to the legitimate
# runtime of the heavier example notebooks under machine load; the timeout's job
# is to catch hangs, not to benchmark, so give it generous headroom.
nb_execution_timeout = 300

html_theme = "furo"
html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
}

# The inventory is vendored in docs/_inventories/ so docs builds need no network
# access; link targets still point at the live site. Refresh the committed
# inventory with `make docs-inventories`.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", "_inventories/python.inv"),
    # Public Starlette types use the vendored Starlette inventory.
    "starlette": ("https://www.starlette.io/", "_inventories/starlette.inv"),
}

autoapi_options = [
       "members",
       "undoc-members",
       "show-inheritance",
       "show-module-summary",
       "imported-members",
]
autoapi_root = "reference/autoapi"
autoapi_ignore = []  # include everything

autoapi_type = "python"
# The merged httk namespace tree is made from committed symlinks into all seven
# submodule checkouts, so AutoAPI parses the runtime distributions as one PEP 420
# httk root and cross-module references resolve in the aggregate inventory.
autoapi_dirs = ["../src/httk"]
autoapi_add_toctree_entry = True
autoapi_keep_files = True
autoapi_member_order = "bysource"
autoapi_python_class_content = "module"  # docstring under class, not merged from __init__
autoapi_python_use_implicit_namespaces = True
autoapi_follow_symlinks = True
autoapi_template_dir = "_templates/autoapi"

nitpicky = True
nitpick_ignore = [
    ("py:class", "typing.Any"),
    ("py:class", "typing.Optional"),
    ("py:class", "typing.Union"),
    ("py:class", "Ellipsis"),
    # numpy and ASE are optional dependencies surfaced by the numeric and compatibility
    # layers; these targeted entries cover their external types.
    ("py:class", "numpy.ndarray"),
    ("py:obj", "numpy.ndarray"),
    ("py:class", "ase.Atoms"),
    ("py:obj", "ase.Atoms"),
    # The workflow CLI exposes argparse's private parser-action type.
    ("py:class", "argparse._SubParsersAction"),
    # pymatgen is an optional dependency surfaced by the integrations layer.
    ("py:class", "pymatgen.core.Structure"),
    ("py:obj", "pymatgen.core.Structure"),
    # AutoAPI renders this TYPE_CHECKING-only record annotation without its
    # module qualification; the concrete record remains documented in the
    # storage records module.
    ("py:class", "NormalizedCompositionRecord"),
    # SQLAlchemy is optional, and these internal-facing signatures have no vendored
    # external inventory.
    ("py:class", "sqlalchemy.Engine"),
    ("py:class", "sqlalchemy.Connection"),
    ("py:class", "sqlalchemy.MetaData"),
    ("py:class", "sqlalchemy.Table"),
    ("py:class", "sqlalchemy.ColumnElement"),
    ("py:class", "sqlalchemy.FromClause"),
    # PEP 695 method type parameters are not classes.
    ("py:class", "T"),
    # Member-module AutoAPI artifacts: these are intentionally unresolved
    # bare aliases, private types, or protocol-member references. Their
    # qualified public objects remain indexed in the aggregate tree.
    ("py:obj", "FrozenJson"),
    ("py:class", "Decimal"),
    ("py:meth", "one"),
    ("py:class", "_RemoteVariable"),
    # The data query API exposes this bare alias.
    ("py:class", "FilterAst"),
    ("py:class", "_Context"),
    ("py:class", "_BackingPlan"),
    # PyMongo publishes no usable intersphinx target for its client class; this
    # targeted ignore follows the sanctioned external-type precedent in httk-core.
    ("py:class", "pymongo.MongoClient"),
    # The parallel bulk-ingest merge entry points (bulk_parallel.merge and
    # ParallelController) carry the module-private worker-manifest type in their
    # signatures; AutoAPI intentionally omits that implementation dataclass.
    ("py:class", "_WorkerManifest"),
    # StoredEntrySource is lazily re-exported from httk.store.backend.sql; AutoAPI
    # keeps the public annotation but indexes its defining module instead.
    ("py:class", "httk.store.backend.sql.StoredEntrySource"),
    ("py:class", "httk.store.db.StoredEntrySource"),
    # Current-module signatures render these module-private types (whose defining
    # classes AutoAPI intentionally omits) and their qualified public objects
    # remain indexed in the aggregate tree.
    ("py:class", "_AutomaticBatch"),
    ("py:class", "_Connector"),
    ("py:class", "_Resolver"),
    ("py:class", "_ValidatedASUProof"),
    # Internal base/provider types exposed in signatures without a public index.
    ("py:class", "FracVectorBase"),
    ("py:obj", "FracVectorBase"),
    ("py:class", "DspProvider"),
    ("py:class", "EntryStore"),
    # The ServeApp branded alias (type ServeApp = Starlette) renders as the bare
    # name Starlette, which the vendored inventory only exposes fully qualified.
    ("py:class", "Starlette"),
    # Bare stdlib/external types AutoAPI renders unqualified in signatures.
    ("py:class", "UUID"),
    ("py:class", "datetime"),
    ("py:class", "sqlalchemy.URL"),
    # Stale cross-reference in the current httk-core FracVector docstring.
    ("py:meth", "httk.core.FracVector.to_fractions"),
]
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

# Apply the member modules' warning suppressions to the aggregate build.
# Aggregate-only: Sphinx's Python domain emits duplicate targets as ref.python
# after merging the modules' inventories. The installed Sphinx tags missing
# Python references by their distinct role subtypes (ref.class, ref.meth,
# ref.func, ref.exc, and ref.attr), so those nitpicky warnings remain fatal.
suppress_warnings = ["myst.xref_missing", "autoapi.python_import_resolution", "ref.python", "mystnb"]


# Workflow-specific rules omit internal modules and resolve public bare-name
# aliases in the aggregate reference.
_INTERNAL_MODULES = (
    "models",
    "journal",
    "transactions",
    "runtime_builders",
    "workspace",
    "manager",
    "introspection",
    "gc",
    "fsck",
    "adapter_runtime",
    "cli",
    "workflow_cli",
    # Language runners are internal; the language registration modules are
    # public.
    "languages.cwl.cwl_runner",
    "languages.pwd.pwd_runner",
    "languages.jobflow.jobflow_runner",
    "languages.httk_v1.v1_runner",
    # The VASP facade is public; the cohesive modules it re-exports are not.
    "vasp.inputs",
    "vasp.diagnostics",
    "vasp.remedies",
    "vasp.reports",
    "vasp.workflows",
)
nitpick_ignore_regex = [
    # AutoAPI renders these imported helper names as bare _common.* targets in
    # the merged tree.
    (r"py:.*", r"_common\.(CLIContext|Sequence|argparse\..+)"),
    (r"py:.*", r"httk\.workflow\.(" + "|".join(_INTERNAL_MODULES) + r")(\..+)?"),
    (r"py:.*", r"httk\.workflow\.vasp\.runners(\..+)?"),
    (
        r"py:.*",
        r"(DataMode|WorkdirMode|PublishMode|RunnerSource|StepHandler|JoinCondition"
        r"|DiagnosticSeverity|EventMonitor|RemedyChange|RemedySequence|MarkerFault|V1Materializer)",
    ),
]


_module_names = (
    "httk-core",
    "httk-atomistic",
    "httk-analyse",
    "httk-store",
    "httk-serve",
    "httk-workflow",
)


# Aggregate-only AutoAPI artifact: workflow_cli imports CLIContext (and its
# program/cwd members) through two source paths, so the merged site renders
# the same objects on the workflow_cli page and on their canonical core page.
# Skip only the redundant workflow_cli entries; the core page remains indexed.
_DUPLICATE_WORKFLOW_CLI_MEMBERS = frozenset(
    {
        "httk.workflow.workflow_cli.CLIContext",
        "httk.workflow.workflow_cli.CLIContext.program",
        "httk.workflow.workflow_cli.CLIContext.cwd",
    }
)


# Internal workflow modules are scanned for names re-exported by public pages,
# but do not receive pages of their own.
_PUBLIC_WORKFLOW_MODULES = frozenset(
    {
        "httk.workflow",
        "httk.workflow.protocol",
        "httk.workflow.errors",
        "httk.workflow.sdk",
        "httk.workflow.runtime",
        "httk.workflow.runtime_utils",
        "httk.workflow.hookapi",
        "httk.workflow.scaffold",
        "httk.workflow.executors",
        "httk.workflow.shell_bridge",
        "httk.workflow.collecting",
        "httk.workflow.provenance",
        "httk.workflow.supervision",
        "httk.workflow.transfers",
        "httk.workflow.manifests",
        "httk.workflow.hygiene",
        "httk.workflow.adapters",
        "httk.workflow.adapter_protocol",
        "httk.workflow.configuration",
        "httk.workflow.projects",
        "httk.workflow.vasp",
        "httk.workflow.compat",
        "httk.workflow.compat.v1",
        "httk.workflow.languages",
        "httk.workflow.languages.cwl",
        "httk.workflow.languages.pwd",
        "httk.workflow.languages.jobflow",
        "httk.workflow.languages.httk_v1",
    }
)
_workflow_exports_cache: dict[str, frozenset[str] | None] = {}


def _workflow_module_exports(module_name: str) -> frozenset[str] | None:
    if module_name not in _workflow_exports_cache:
        try:
            module = importlib.import_module(module_name)
        except Exception:  # pragma: no cover - unavailable optional module
            _workflow_exports_cache[module_name] = None
        else:
            names = getattr(module, "__all__", None)
            _workflow_exports_cache[module_name] = None if names is None else frozenset(names)
    return _workflow_exports_cache[module_name]


def _module_version_rows(srcdir: Path) -> list[tuple[str, str, str]]:
    manifest_path = srcdir / "ecosystem.json"
    if manifest_path.is_file():
        try:
            document = json.loads(manifest_path.read_text(encoding="utf-8"))
            modules = document["modules"]
            if isinstance(modules, dict):
                rows = []
                for name in sorted(modules):
                    entry = modules[name]
                    version = entry.get("version") if isinstance(entry, dict) else None
                    if not isinstance(version, str) or not version:
                        version = "dev:main"
                    link = (
                        f"https://docs.httk.org/{name}/{version}/"
                        if version.startswith("v")
                        else f"https://docs.httk.org/{name}/dev/main/"
                    )
                    rows.append((name, version, link))
                return rows
        except (KeyError, OSError, json.JSONDecodeError, TypeError):
            warnings.warn(f"ignoring malformed ecosystem manifest: {manifest_path}", stacklevel=1)
    submodules = srcdir.parent / "submodules"
    return [(name, "development", f"https://docs.httk.org/{name}/") for name in _module_names if (submodules / name).is_dir()]


def _write_module_versions(app):
    srcdir = Path(app.srcdir)
    output = srcdir / "_generated" / "module_versions.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| Module | Version | Documentation |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| {name} | {version} | [{link}]({link}) |" for name, version, link in _module_version_rows(srcdir))
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def skip_member(app, what, name, obj, skip, options):
    obj_id = str(getattr(obj, "id", None) or name)
    if obj_id in _DUPLICATE_WORKFLOW_CLI_MEMBERS:
        return True
    if obj_id == "httk.workflow" or obj_id.startswith("httk.workflow."):
        if what in {"module", "package"}:
            return obj_id not in _PUBLIC_WORKFLOW_MODULES
        if name.startswith('_'):
            return True
        owner, _, short = obj_id.rpartition(".")
        exports = _workflow_module_exports(owner)
        if exports is not None and short not in exports:
            return True
    # Skip private members (those starting with _)
    if name.startswith('_'):
        return True
    return skip


def setup(sphinx):
    sphinx.connect('autoapi-skip-member', skip_member)
    sphinx.connect('builder-inited', _write_module_versions)
