"""Verify that the aggregate source tree follows the committed ecosystem manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NoReturn


_EXPECTED_MODULES = frozenset(
    {
        "httk-core",
        "httk-atomistic",
        "httk-io",
        "httk-data",
        "httk-optimade",
        "httk-web",
        "httk-workflow",
    }
)


def _fail(message: str) -> NoReturn:
    raise SystemExit(message)


def _inside(path: Path, root: Path, label: str) -> None:
    if not path.is_symlink():
        _fail(f"{label} is missing or not a symlink: {path}")
    try:
        path.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (FileNotFoundError, ValueError):
        _fail(f"{label} resolves outside its module checkout: {path} -> {path.resolve()}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        document = json.loads((root / "docs" / "ecosystem.json").read_text(encoding="utf-8"))
        modules = document["modules"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        _fail(f"cannot read valid docs/ecosystem.json: {exc}")
    if not isinstance(modules, dict) or not modules:
        _fail("docs/ecosystem.json has no modules")
    if set(modules) != _EXPECTED_MODULES:
        _fail("ecosystem module set does not contain exactly the seven expected modules")

    source_root = root / "src" / "httk"
    submodules = root / "submodules"
    shortnames = {name.removeprefix("httk-") for name in _EXPECTED_MODULES}
    expected_root_entries = shortnames | {"handlers"}
    actual_root_entries = {entry.name for entry in source_root.iterdir()}
    unexpected = sorted(actual_root_entries - expected_root_entries)
    if unexpected:
        _fail("unexpected entries under src/httk: " + ", ".join(unexpected))
    for name in sorted(modules):
        shortname = name.removeprefix("httk-")
        module_root = submodules / name
        if not module_root.is_dir():
            _fail(f"module checkout is missing: {module_root}")
        _inside(source_root / shortname, module_root, f"module source link for {name}")

    handler_root = source_root / "handlers"
    if not handler_root.is_dir() or handler_root.is_symlink():
        _fail(f"src/httk/handlers must be a real directory: {handler_root}")
    expected_handlers = {
        name.removeprefix("httk-")
        for name in modules
        if (submodules / name / "src" / "httk" / "handlers" / name.removeprefix("httk-")).exists()
    }
    actual_handlers = {entry.name for entry in handler_root.iterdir()}
    unexpected_handlers = sorted(actual_handlers - expected_handlers)
    if unexpected_handlers:
        _fail("unexpected entries under src/httk/handlers: " + ", ".join(unexpected_handlers))
    for name in sorted(modules):
        shortname = name.removeprefix("httk-")
        target = submodules / name / "src" / "httk" / "handlers" / shortname
        if target.exists():
            _inside(handler_root / shortname, submodules / name, f"handler link for {name}")
    print("topology matches docs/ecosystem.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
