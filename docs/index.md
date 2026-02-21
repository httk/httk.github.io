# *httk₂*

This is the aggregate documentation website for *httk₂*.

*httk₂* is comprised of independent modules.
There is a "standard set" that one can install to get started;
and then additional modules can be added.

## Install a standard set of modules

Preferably work in a Python virtual environment, then do:
```bash
git clone https://github.com/httk/httk2
cd httk-core
python -m pip install -e .
```

## Add a manually installed plugin module

Use the same Python virual environment, and do, e.g.:
```bash
git clone https://github.com/httk/httk-symgen
cd httk-symgen
python -m pip install -e .
```

## Small usage example

```python
from httk.core import subpackages

print(subpackages)
```

## Documentation
```{toctree}
:maxdepth: 2

reference/index
notebooks/index
```
