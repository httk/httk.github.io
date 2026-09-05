"""Execute the introductory examples with a disposable synthetic identity."""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from starlette.testclient import TestClient


def main() -> None:
    """Check the published Python examples and packaged mock workflow."""
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workflow-source", type=Path, default=root / "submodules/httk-workflow"
    )
    arguments = parser.parse_args()
    for page, block in (("structures", 0), ("data", 0), ("data", 2)):
        path = root / "docs" / f"{page}.md"
        code = (
            path.read_text(encoding="utf-8")
            .split("```python\n")[block + 1]
            .split("```", 1)[0]
        )
        namespace = {"__name__": "__main__"}
        exec(compile(code, str(path), "exec"), namespace)
        if "app" in namespace:
            with TestClient(namespace["app"]) as client:
                response = client.get("/v1/references")
                assert response.status_code == 200
                assert response.json()["data"][0]["id"] == "example-1-1"

    with TemporaryDirectory(prefix="httk-first-use-") as directory:
        env = dict(os.environ)
        env.update(
            HTTK_CONFIG_HOME=str(Path(directory) / "config"),
            HTTK_DATA_HOME=str(Path(directory) / "data"),
            PATH=str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", ""),
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "httk.core.cli",
                "init",
                "--name",
                "Example User",
                "--email",
                "test@example.invalid",
            ],
            cwd=directory,
            env=env,
            check=True,
        )
        subprocess.run(
            [
                "bash",
                str(arguments.workflow_source.resolve() / "examples/quickstart.sh"),
            ],
            cwd=directory,
            env=env,
            check=True,
        )
        assert (Path(directory) / "results.sqlite").is_file()
    print("First-use structure, storage, serving, and mock workflow examples passed.")


if __name__ == "__main__":
    main()
