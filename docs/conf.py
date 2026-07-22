import os
import warnings
from datetime import date

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
    "sphinx.ext.extlinks",
    "sphinx.ext.mathjax",        # math rendering via MathJax

    # Nice-to-haves
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",

    # Markdown + notebooks
    "myst_nb",                   # .ipynb support

    "autoapi.extension",
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
autodoc_typehints = "signature"
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

# Execute the example notebooks as part of the (strict) docs build, so that an
# example that no longer matches the current httk-core / httk-atomistic API fails
# the build instead of silently going stale.
nb_execution_mode = "force"

html_theme = "furo"
html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
}

# This top-level site now carries a full aggregate API reference built from the
# submodule sources (see autoapi settings below), so cross-module references resolve
# inside this site's own inventory rather than against the per-module subsites. The
# DOCS_BASE_URL plumbing remains for the module directory's "go to the module's own
# subsite" links. The base URL comes from the DOCS_BASE_URL Makefile variable
# (exported as HTTK_DOCS_BASE_URL); the default below keeps bare sphinx invocations
# working.
_docs_base_url = os.environ.get("HTTK_DOCS_BASE_URL", "https://docs.httk.org")

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Plain "go to the module's docs" links, e.g. {moduledocs}`httk-core`.
extlinks = {"moduledocs": (f"{_docs_base_url}/%s/", "%s documentation")}

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
# The merged httk namespace tree: src/httk/core and src/httk/atomistic are committed
# symlinks into the two submodule checkouts, so AutoAPI parses both distributions as
# a single PEP 420 httk root and cross-module references (httk.atomistic subclassing
# httk.core objects) resolve internally.
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
]
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

suppress_warnings = ["myst.xref_missing"]

def skip_member(app, what, name, obj, skip, options):
    # Skip private members (those starting with _)
    if name.startswith('_'):
        return True
    return skip

def setup(sphinx):
    sphinx.connect('autoapi-skip-member', skip_member)
