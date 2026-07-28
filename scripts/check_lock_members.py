"""Check that the aggregate lock covers member runtime and docs dependencies."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path


_REQUIREMENT = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[([^]]+)\])?")


def _normalized(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _requirement(value: str) -> tuple[str, tuple[str, ...]] | None:
    match = _REQUIREMENT.match(value)
    if match is None:
        return None
    extras = tuple(part.strip() for part in (match.group(2) or "").split(",") if part.strip())
    return _normalized(match.group(1)), extras


def _member_requirements(path: Path) -> dict[str, set[str]]:
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    project = document.get("project", {})
    if not isinstance(project, dict):
        raise SystemExit(f"{path}: project must be a table")
    distribution = project.get("name")
    if not isinstance(distribution, str):
        raise SystemExit(f"{path}: project.name is missing")
    found: set[str] = set()
    optional = project.get("optional-dependencies", {})
    if not isinstance(optional, dict):
        optional = {}
    seen_extras: set[str] = set()
    distribution_name = _normalized(distribution)

    def add_values(values: object) -> None:
        if not isinstance(values, list):
            return
        for value in values:
            if not isinstance(value, str):
                continue
            requirement = _requirement(value)
            if requirement is None:
                continue
            name, extras = requirement
            if name == distribution_name:
                for extra in extras:
                    add_extra(extra)
            elif not name.startswith("httk-"):
                found.add(name)

    def add_extra(extra: str) -> None:
        if extra in seen_extras:
            return
        seen_extras.add(extra)
        add_values(optional.get(extra, []))

    add_values(project.get("dependencies", []))
    add_extra("default")
    add_extra("docs")
    return {_normalized(distribution): found}


def _locked_names(path: Path) -> set[str]:
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        requirement = _requirement(line)
        if requirement is not None:
            names.add(requirement[0])
    return names


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    lock = root / "docs" / "requirements.lock"
    requirements: dict[str, set[str]] = {}
    for pyproject in sorted((root / "submodules").glob("*/pyproject.toml")):
        requirements.update(_member_requirements(pyproject))
    locked = _locked_names(lock)
    missing: dict[str, list[str]] = {}
    for module, names in requirements.items():
        absent = sorted(names - locked)
        if absent:
            missing[module] = absent
    if missing:
        print(f"{lock}: missing member requirements:")
        for module, names in sorted(missing.items()):
            print(f"  {module}: {', '.join(names)}")
        return 1
    print(f"{lock}: covers all member runtime/default/docs requirement names")
    return 0


if __name__ == "__main__":
    sys.exit(main())
