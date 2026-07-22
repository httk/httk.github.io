PYTHON ?= python3

# Base URL of the published httk documentation site, used for cross-linking docs
# between httk repositories (read by docs/conf.py via HTTK_DOCS_BASE_URL).
DOCS_BASE_URL ?= https://docs.httk.org

.PHONY: docs docs-live docs-clean docs-inventories clean

docs: docs-clean
	HTTK_DOCS_BASE_URL=$(DOCS_BASE_URL) $(PYTHON) -m sphinx -E -a -b html -W --keep-going docs docs/_build/html

docs-live:
	HTTK_DOCS_BASE_URL=$(DOCS_BASE_URL) sphinx-autobuild docs docs/_build/html

docs-clean:
	rm -rf docs/_build docs/reference/autoapi

# Refresh the committed intersphinx inventories (the one docs task that uses the
# network); docs builds themselves resolve against these vendored files offline.
docs-inventories:
	curl -fsSL https://docs.python.org/3/objects.inv -o docs/_inventories/python.inv

clean: docs-clean
	find . -name "*.pyc" -print0 | xargs -0 rm -f
	find . -name "*~" -print0 | xargs -0 rm -f
	find . -name "__pycache__" -print0 | xargs -0 rm -rf
