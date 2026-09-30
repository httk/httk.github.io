"""Execute the VASP-calculations OPTIMADE walkthrough, including its real HTTP client."""

import contextlib
import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

COLLECT = "httk collect calculations --into vasp.sqlite --id-base example"
CUSTOM = COLLECT + " --collector ./my-vasp-relax"


def console_outputs(blocks):
    """Map each ``$ command`` of the page's console blocks to its shown output lines."""
    outputs = []
    for language, code in blocks:
        if language != "console":
            continue
        for chunk in code.split("$ ")[1:]:
            command, *lines = chunk.rstrip("\n").split("\n")
            outputs.append((command, lines))
    return outputs


def main() -> None:
    """Run the published calculation-tree collect, re-run, custom collector, and HTTP serving example."""
    page = Path(sys.argv[1]).resolve()
    section = page.read_text(encoding="utf-8").split("From VASP calculations", 1)[1]
    blocks = re.findall(r"^```(\w+)\n(.*?)^```", section, re.MULTILINE | re.DOTALL)
    python = [code for language, code in blocks if language == "python"]
    (toml,) = [code for language, code in blocks if language == "toml"]
    commands = "\n".join(code for language, code in blocks if language == "bash")
    assert len(python) == 4
    assert "port=8080" in python[2]
    shown = console_outputs(blocks)
    assert [command for command, _ in shown] == [
        "httk collect calculations --dry-run",
        COLLECT,
        "python show_results.py",
        COLLECT,
        "python show_results.py",
        "curl http://127.0.0.1:8080/v1/_httk_records/example.records-1-3/_httk_revs",
        CUSTOM,
        "python show_results.py",
    ], shown
    (copy,) = [line for line in commands.splitlines() if line.startswith("cp -r ")]
    for query in (
        "curl http://127.0.0.1:8080/v1/info",
        "--data-urlencode 'filter=elements HAS \"Na\"'",
        "curl http://127.0.0.1:8080/v1/_httk_runs/example.runs-1-3",
        "--data-urlencode 'filter=_httk_source_id STARTS \"vasp.calculation.static\"'",
        "--data-urlencode 'include=structures'",
    ):
        assert query in commands, query

    with TemporaryDirectory(prefix="httk-vasp-example-") as directory:
        root = Path(directory)
        work = root / "work"
        work.mkdir()
        env = dict(os.environ)
        env.update(
            HTTK_CONFIG_HOME=str(root / "config"),
            HTTK_DATA_HOME=str(root / "data"),
            PATH=str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", ""),
        )
        for name, code in zip(
            ("make_example_calculations.py", "show_results.py", "serve_vasp.py"),
            python[:3],
            strict=False,
        ):
            (work / name).write_text(code, encoding="utf-8")

        def run(command, *, status=0):
            done = subprocess.run(
                command,
                cwd=work,
                env=env,
                shell=True,
                check=False,
                timeout=300,
                capture_output=True,
                text=True,
            )
            assert done.returncode == status, (
                f"{command} exited {done.returncode}:\n{done.stderr}"
            )
            return done

        def lines(command, *, status=0):
            return run(command, status=status).stdout.splitlines()

        def records(stdout_lines):
            return [json.loads(line) for line in stdout_lines]

        def counts():
            with contextlib.closing(sqlite3.connect(work / "vasp.sqlite")) as db:
                return [
                    db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    for table in (
                        "atomistic_unitcell_structure",
                        "core_data_record",
                        "core_run",
                    )
                ]

        run('httk init --name "Your Name" --email you@example.org')
        run("python make_example_calculations.py")

        dry = shown[0][1]
        assert lines("httk collect calculations --dry-run") == dry

        # The first collect: KCl degrades (exit 1), Al/md is unclaimed.
        first = run(COLLECT, status=1)
        assert "Al/md: not collected by vasp.calculation.relax" in first.stderr
        assert "creating id ledger vasp.sqlite.ids.sqlite" in first.stderr
        assert (work / "vasp.sqlite.ids.sqlite").is_file()
        report = records(first.stdout.splitlines())
        assert first.stdout.splitlines()[-1] == shown[1][1][-1]
        stored = {item["job_id"][:8]: item for item in report[:-1]}
        fe = stored["0c110c39"]
        assert fe["stored"] == {
            "entries": ["example-1-5", "example-1-8", "example.records-1-1"],
            "run": "example.runs-1-1",
        }
        assert json.dumps(fe["stored"], separators=(",", ":")) in shown[1][1][4]
        kcl = stored["0b9429ef"]
        assert kcl["skipped"] == "degraded" and kcl["stored"] is None
        assert kcl["missing_collector"].endswith("calculations/KCl/relax/CONTCAR")
        assert kcl["unfulfilled"] == ["relaxed_structure", "total_energy"]
        before = counts()
        assert before == [7, 4, 4]
        # Collecting again adds nothing.
        again = records(lines(COLLECT, status=1))
        assert again == report
        assert counts() == before
        assert lines("python show_results.py") == shown[2][1]

        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        base = f"http://127.0.0.1:{port}"

        def get(path, **params):
            with urlopen(base + path + "?" + urlencode(params), timeout=15) as response:
                return json.load(response)

        def related(entry):
            return {
                key: [
                    (item["id"], item["meta"].get("_httk_label"))
                    for item in value["data"]
                ]
                for key, value in entry.get("relationships", {}).items()
            }

        # The documented script fixes port 8080; use a temporary copy for this check.
        (work / "serve_check.py").write_text(
            python[2].replace("port=8080", f"port={port}"), encoding="utf-8"
        )
        with (work / "server.log").open("w+") as log:
            server = subprocess.Popen(
                [sys.executable, "serve_check.py"],
                cwd=work,
                env=env,
                stdout=log,
                stderr=log,
            )
            try:
                deadline = time.monotonic() + 30
                while True:
                    if server.poll() is not None or time.monotonic() > deadline:
                        log.seek(0)
                        raise AssertionError(
                            f"OPTIMADE server did not start:\n{log.read()}"
                        )
                    try:
                        get("/v1/info")
                        break
                    except OSError:
                        time.sleep(0.05)

                info = get("/v1/info")["data"]["attributes"]
                assert sorted(info["entry_types_by_format"]["json"]) == [
                    "_httk_records",
                    "_httk_runs",
                    "structures",
                ]
                assert "_httk_records~revs" in info["available_endpoints"]

                sodium = {
                    entry["id"]: entry
                    for entry in get("/v1/structures", filter='elements HAS "Na"')[
                        "data"
                    ]
                }
                assert sorted(sodium) == ["example-1-17", "example-1-20"]
                initial, relaxed = sodium["example-1-20"], sodium["example-1-17"]
                assert initial["attributes"]["lattice_vectors"][0][0] == 3.99
                assert relaxed["attributes"]["lattice_vectors"][0][0] == 4.02
                assert related(initial) == {
                    "_httk_is_input": [("example.runs-1-3", "initial_structure")]
                }
                assert related(relaxed)["_httk_is_output"] == [
                    ("example.runs-1-3", "relaxed_structure")
                ]
                assert related(relaxed)["_httk_has_product"] == [
                    ("example.records-1-3", "relaxed_structure")
                ]

                nacl = get("/v1/_httk_runs/example.runs-1-3")["data"]
                assert nacl["attributes"]["_httk_source_id"].startswith(
                    "vasp.calculation.relax:eac3f541"
                )
                assert related(nacl)["_httk_has_input"] == [
                    ("example-1-20", "initial_structure")
                ]
                assert related(nacl)["_httk_has_output"] == [
                    ("example-1-17", "relaxed_structure"),
                    ("example.records-1-3", "total_energy"),
                ]

                static = get(
                    "/v1/_httk_runs",
                    filter='_httk_source_id STARTS "vasp.calculation.static"',
                )["data"]
                assert [entry["id"] for entry in static] == ["example.runs-1-4"]

                payload = get("/v1/_httk_records", include="structures")
                products = {
                    entry["id"]: related(entry)["_httk_product_of"]
                    for entry in payload["data"]
                }
                assert products == {
                    "example.records-1-1": [("example-1-5", "relaxed_structure")],
                    "example.records-1-2": [("example-1-11", "relaxed_structure")],
                    "example.records-1-3": [("example-1-17", "relaxed_structure")],
                    "example.records-1-4": [("example-1-23", "initial_structure")],
                }
                assert {entry["id"] for entry in payload["included"]} == {
                    "example-1-5",
                    "example-1-11",
                    "example-1-17",
                    "example-1-23",
                }
                # The documented limitation: record values are not served yet.
                try:
                    get("/v1/_httk_records", filter="_httk_total_energy < -10")
                except HTTPError as error:
                    assert error.code == 400
                else:
                    raise AssertionError(
                        "records now serve their values; update the page"
                    )

                # Re-run NaCl/relax in place, as documented, with the server running.
                calculation = work / "calculations" / "NaCl" / "relax"
                for name, old, new in (
                    ("OUTCAR", "-6.83000000", "-6.85000000"),
                    ("CONTCAR", "4.02", "4.03"),
                ):
                    text = (calculation / name).read_text(encoding="utf-8")
                    assert old in text, (name, text)
                    (calculation / name).write_text(
                        text.replace(old, new), encoding="utf-8"
                    )
                rerun = records(lines(COLLECT, status=1))
                assert json.dumps(rerun[-1], separators=(",", ":")) == shown[3][1][-1]
                revised = [item for item in rerun[:-1] if item["revised"]]
                assert [item["job_id"][:8] for item in revised] == ["eac3f541"]
                assert revised[0]["stored"]["run"] == "example.runs-1-3"
                assert lines("python show_results.py") == shown[4][1]
                revisions = get("/v1/_httk_records/example.records-1-3/_httk_revs")[
                    "data"
                ]
                assert [
                    (entry["id"], related(entry)["_httk_product_of"][0][0])
                    for entry in revisions
                ] == [
                    ("example.records-1-3~1", "example-1-17"),
                    ("example.records-1-3~2", "example-1-26"),
                ]
                runs = get("/v1/_httk_runs/example.runs-1-3/_httk_revs")["data"]
                assert [related(entry)["_httk_has_output"][0][0] for entry in runs] == [
                    "example-1-17",
                    "example-1-26",
                ]
                get("/v1/structures/example-1-17")  # the old cell stays

                # The custom collector: copy the shipped one and add the magnetization.
                run(copy)
                package = work / "my-vasp-relax"
                manifest = package / "httk_workflow.toml"
                assert 'name = "vasp.calculation.relax"' in manifest.read_text(
                    encoding="utf-8"
                )
                with manifest.open("a", encoding="utf-8") as handle:
                    handle.write("\n" + toml)
                (package / "collect.py").write_text(python[3], encoding="utf-8")
                custom = records(lines(CUSTOM, status=1))
                assert json.dumps(custom[-1], separators=(",", ":")) == shown[6][1][-1]
                assert [
                    item["job_id"][:8] for item in custom[:-1] if item["revised"]
                ] == ["0c110c39"]
                assert lines("python show_results.py") == shown[7][1]
                fe_run = get("/v1/_httk_runs/example.runs-1-1")["data"]
                assert fe_run["attributes"]["immutable_id"] == "example.runs-1-1~2"
                assert related(fe_run)["_httk_has_output"][-1] == (
                    "example.records-1-5",
                    "total_magnetization",
                )
            finally:
                server.terminate()
                try:
                    server.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()
                    raise AssertionError("OPTIMADE server did not stop") from None
    print(
        f"{page.name}: calculation-tree collect, re-run revisions, custom collector, "
        "and HTTP serving passed"
    )


if __name__ == "__main__":
    main()
