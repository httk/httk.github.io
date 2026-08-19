"""Verify that the aggregate source tree follows the committed ecosystem manifest."""

import json
import sys
from pathlib import Path
from typing import NoReturn

_EXPECTED_MODULES = frozenset(
    {
        "httk-core",
        "httk-atomistic",
        "httk-analyse",
        "httk-store",
        "httk-serve",
        "httk-workflow",
    }
)

_EXPECTED_REGISTRY_LINKS = {
    Path("io/atomistic"): "httk-atomistic",
    Path("workflow"): "httk-workflow",
    Path("cli/atomistic"): "httk-atomistic",
    Path("cli/core"): "httk-core",
    Path("cli/serve"): "httk-serve",
    Path("entries/atomistic"): "httk-atomistic",
    Path("entries/core"): "httk-core",
    Path("entries/store"): "httk-store",
    Path("schemas/atomistic"): "httk-atomistic",
    Path("schemas/core"): "httk-core",
}


def _fail(message: str) -> NoReturn:
    raise SystemExit(message)


def _inside(path: Path, root: Path, label: str) -> None:
    if not path.is_symlink():
        _fail(f"{label} is missing or not a symlink: {path}")
    try:
        path.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (FileNotFoundError, ValueError):
        _fail(
            f"{label} resolves outside its module checkout: {path} -> {path.resolve()}"
        )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        document = json.loads(
            (root / "docs" / "ecosystem.json").read_text(encoding="utf-8")
        )
        modules = document["modules"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        _fail(f"cannot read valid docs/ecosystem.json: {exc}")
    if not isinstance(modules, dict) or not modules:
        _fail("docs/ecosystem.json has no modules")
    if set(modules) != _EXPECTED_MODULES:
        _fail("ecosystem module set does not contain exactly the six expected modules")

    source_root = root / "src" / "httk"
    submodules = root / "submodules"
    shortnames = {name.removeprefix("httk-") for name in _EXPECTED_MODULES}
    stale_handler_root = source_root / "handlers"
    if stale_handler_root.exists() or stale_handler_root.is_symlink():
        _fail(f"stale src/httk/handlers must not exist: {stale_handler_root}")
    expected_root_entries = shortnames | {"registry"}
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

    registry_root = source_root / "registry"
    if not registry_root.is_dir() or registry_root.is_symlink():
        _fail(f"src/httk/registry must be a real directory: {registry_root}")
    expected_registry = {path.parts[0] for path in _EXPECTED_REGISTRY_LINKS}
    actual_registry = {entry.name for entry in registry_root.iterdir()}
    if actual_registry != expected_registry:
        _fail(
            "src/httk/registry entries do not match the expected namespace: "
            + ", ".join(sorted(actual_registry))
        )
    nested_registry_roots = {
        path.parts[0] for path in _EXPECTED_REGISTRY_LINKS if len(path.parts) == 2
    }
    for parent in sorted(nested_registry_roots):
        namespace_root = registry_root / parent
        if not namespace_root.is_dir() or namespace_root.is_symlink():
            _fail(
                f"src/httk/registry/{parent} must be a real directory: {namespace_root}"
            )
        expected_children = {
            path.parts[1]
            for path in _EXPECTED_REGISTRY_LINKS
            if path.parts[0] == parent
        }
        actual_children = {entry.name for entry in namespace_root.iterdir()}
        if actual_children != expected_children:
            _fail(
                f"src/httk/registry/{parent} entries do not match the expected namespace: "
                + ", ".join(sorted(actual_children))
            )
    for relative, name in sorted(
        _EXPECTED_REGISTRY_LINKS.items(), key=lambda item: str(item[0])
    ):
        target = submodules / name / "src" / "httk" / "registry" / relative
        if not target.is_dir():
            _fail(f"registry source is missing for {name}: {target}")
        _inside(
            registry_root / relative,
            submodules / name,
            f"registry link for {name}:{relative}",
        )
    print("topology matches docs/ecosystem.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
