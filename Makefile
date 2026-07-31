PYTHON ?= python3

# Base URL of the published httk documentation site, used for cross-linking docs
# between httk repositories (read by docs/conf.py via HTTK_DOCS_BASE_URL).
DOCS_BASE_URL ?= https://docs.httk.org

.PHONY: docs docs-live docs-clean docs-inventories docs-lock docs-lock-check ecosystem-manifest release-check clean

docs: docs-clean
	HTTK_DOCS_BASE_URL=$(DOCS_BASE_URL) $(PYTHON) -m sphinx -E -a -b html -W --keep-going docs docs/_build/html

docs-live:
	HTTK_DOCS_BASE_URL=$(DOCS_BASE_URL) sphinx-autobuild docs docs/_build/html

docs-clean:
	rm -rf docs/_build docs/reference/autoapi docs/_generated

# The aggregate has no internal dependency pins: all seven module checkouts are
# installed separately, while this lock contains only external docs requirements.
docs-lock:
	$(PYTHON) -m httk.core.docs lock
	$(PYTHON) scripts/check_lock_members.py

docs-lock-check: docs-clean
	@set -eu; \
	check_dir=$$(mktemp -d "$${TMPDIR:-/tmp}/httk-site-docs-lock-check.XXXXXX"); \
	trap 'rm -rf "$$check_dir"' EXIT; \
	env -u PYTHONPATH -u PYTHONHOME $(PYTHON) -m venv "$$check_dir/venv"; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" -m pip install -r docs/requirements.lock; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" -m pip install -e submodules/httk-core --no-deps; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" -m pip install -e submodules/httk-atomistic --no-deps; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" -m pip install -e submodules/httk-analyse --no-deps; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" -m pip install -e submodules/httk-io --no-deps; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" -m pip install -e submodules/httk-data --no-deps; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" -m pip install -e submodules/httk-serve --no-deps; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" -m pip install -e submodules/httk-workflow --no-deps; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" -m pip install -e . --no-deps --no-build-isolation; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" -m pip check; \
	env -u PYTHONPATH -u PYTHONHOME "$$check_dir/venv/bin/python" scripts/check_lock_members.py; \
	env -u PYTHONPATH -u PYTHONHOME HTTK_DOCS_BASE_URL="$(DOCS_BASE_URL)" \
		"$$check_dir/venv/bin/python" -m sphinx -E -a -b html -W --keep-going docs "$$check_dir/html"

ecosystem-manifest:
	$(PYTHON) -m httk.core.docs ecosystem-manifest \
		--submodules-dir submodules --out docs/ecosystem.json

release-check: docs
	$(MAKE) docs-lock-check

# Refresh the committed intersphinx inventories (the one docs task that uses the
# network); docs builds themselves resolve against these vendored files offline.
docs-inventories:
	curl -fsSL https://docs.python.org/3/objects.inv -o docs/_inventories/python.inv
	curl -fsSL https://www.starlette.io/objects.inv -o docs/_inventories/starlette.inv

clean: docs-clean
	find . -name "*.pyc" -print0 | xargs -0 rm -f
	find . -name "*~" -print0 | xargs -0 rm -f
	find . -name "__pycache__" -print0 | xargs -0 rm -rf
