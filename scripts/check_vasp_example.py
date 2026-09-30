"""Execute the VASP-calculations OPTIMADE walkthrough, including its real HTTP client."""

import contextlib
import json
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlencode
from urllib.request import urlopen

TOTAL_ENERGY = "https://schemas.httk.org/defs/v0.1/properties/core/total_energy"
DATA_URL = "https://data.example.org/calculations"


def main() -> None:
    """Run the published calculation-tree ingest, re-run, and HTTP serving example."""
    page = Path(sys.argv[1]).resolve()
    section = page.read_text(encoding="utf-8").split("From VASP calculations", 1)[1]
    blocks = re.findall(r"^```(\w+)\n(.*?)^```", section, re.MULTILINE | re.DOTALL)
    python = [code for language, code in blocks if language == "python"]
    assert len(python) == 4
    assert f'DATA_URL = "{DATA_URL}"' in python[2]
    assert "port=8080" in python[3]
    with TemporaryDirectory(prefix="httk-vasp-example-") as directory:
        root = Path(directory)
        names = (
            "make_example_calculations.py",
            "vasp_records.py",
            "ingest_vasp.py",
            "serve_vasp.py",
        )
        for name, code in zip(names, python, strict=True):
            (root / name).write_text(code, encoding="utf-8")

        def run(script):
            done = subprocess.run(
                [sys.executable, script],
                cwd=root,
                check=False,
                timeout=120,
                capture_output=True,
                text=True,
            )
            assert done.returncode == 0, f"{script} failed:\n{done.stderr}"
            return done

        run("make_example_calculations.py")
        # Not in the page's tree: an unreadable calculation must be skipped alone.
        bad = root / "calculations" / "Bad" / "relax"
        bad.mkdir(parents=True)
        (bad / "POSCAR").write_text("garbage\n", encoding="utf-8")
        for name in ("CONTCAR", "OUTCAR"):
            source = root / "calculations" / "NaCl" / "relax" / name
            (bad / name).write_bytes(source.read_bytes())
        # The documented commands ingest twice; the second run must add nothing.
        for _ in range(2):
            ingest = run("ingest_vasp.py")
            assert ingest.stdout == "ingested 4 calculations, skipped 2\n", ingest
            assert "skipping Bad/relax: Malformed POSCAR" in ingest.stderr, (
                ingest.stderr
            )
            assert "skipping KCl/relax" in ingest.stderr, ingest.stderr
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        base = f"http://127.0.0.1:{port}"

        def get(path, **params):
            with urlopen(base + path + "?" + urlencode(params), timeout=15) as response:
                return json.load(response)

        def count(entry_type):
            return get(f"/v1/{entry_type}")["meta"]["data_available"]

        # The documented script fixes port 8080; use a temporary copy for this check.
        (root / "serve_check.py").write_text(
            python[3].replace("port=8080", f"port={port}"), encoding="utf-8"
        )

        @contextlib.contextmanager
        def serving():
            with (root / "server.log").open("w+") as log:
                server = subprocess.Popen(
                    [sys.executable, "serve_check.py"], cwd=root, stdout=log, stderr=log
                )
                try:
                    deadline = time.monotonic() + 20
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
                    yield
                finally:
                    server.terminate()
                    try:
                        server.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        server.kill()
                        server.wait()
                        raise AssertionError("OPTIMADE server did not stop") from None

        with serving():
            assert [count(t) for t in ("structures", "_httk_records")] == [7, 4]
            assert [count(t) for t in ("_httk_runs", "files")] == [4, 4]
            info = get("/v1/info/_httk_records")["data"]["properties"]
            energy = info["_httk_total_energy"]
            assert energy["$id"] == TOTAL_ENERGY
            assert energy["x-optimade-unit"] == "eV"
            custom = {"completed", "source_path", "total_magnetization"}
            assert {f"_httk_custom_{name}" for name in custom} <= set(info)
            assert info["_httk_custom_total_magnetization"]["x-optimade-unit"] == "mu_B"

            payload = get("/v1/_httk_records", include="structures")
            records = {
                r["attributes"]["_httk_custom_source_path"]: r for r in payload["data"]
            }
            assert sorted(records) == [
                "Fe/relax",
                "MgO/relax",
                "NaCl/relax",
                "Si/static",
            ]
            assert records["NaCl/relax"]["id"] == "example.records-1-3"
            assert all(
                r["attributes"]["_httk_custom_completed"] for r in records.values()
            )
            links = {
                name: record["relationships"]["structures"]["data"][0]["id"]
                for name, record in records.items()
            }
            included = {(s["type"], s["id"]) for s in payload["included"]}
            assert included == {("structures", sid) for sid in links.values()}
            magnetization = {
                name: get(
                    f"/v1/_httk_records/{record['id']}",
                    response_fields="_httk_custom_total_magnetization",
                )["data"]["attributes"]["_httk_custom_total_magnetization"]
                for name, record in records.items()
            }
            assert abs(magnetization.pop("Fe/relax") - 2.214) < 1e-9
            assert set(magnetization.values()) == {None}, magnetization

            low = get("/v1/_httk_records", filter="_httk_total_energy < -10")["data"]
            assert [r["id"] for r in low] == [
                "example.records-1-2",
                "example.records-1-4",
            ]

            runs = {
                r["attributes"]["_httk_source_id"]: r
                for r in get("/v1/_httk_runs")["data"]
            }
            assert sorted(runs) == [f"calculations:{name}" for name in sorted(records)]
            for name, record in records.items():
                relationships = runs[f"calculations:{name}"]["relationships"]
                (initial,) = relationships["_httk_has_input"]["data"]
                produced = {
                    edge["meta"]["_httk_label"]: (edge["type"], edge["id"])
                    for edge in relationships["_httk_has_output"]["data"]
                }
                assert produced["result"] == ("_httk_records", record["id"])
                assert produced["outcar"][0] == "files"
                if name == "Si/static":
                    assert "relaxed_structure" not in produced
                    assert initial["id"] == links[name]
                else:
                    assert produced["relaxed_structure"] == ("structures", links[name])
            assert runs["calculations:Fe/relax"]["id"] == "example.runs-1-1"
            fe = get("/v1/structures/example.structures-1-2")["data"]
            assert links["Fe/relax"] == fe["id"]
            (reverse,) = fe["relationships"]["_httk_is_output"]["data"]
            assert (reverse["type"], reverse["id"]) == (
                "_httk_runs",
                "example.runs-1-1",
            )

            files = get("/v1/files")["data"]
            # Request media_type explicitly so that a null value is serialized.
            media_types = [
                (f["attributes"]["name"], f["attributes"]["media_type"])
                for f in get("/v1/files", response_fields="name,media_type")["data"]
            ]
            assert sorted(media_types, key=str) == [
                ("OUTCAR", "text/plain"),
                ("OUTCAR", "text/plain"),
                ("OUTCAR", "text/plain"),
                ("OUTCAR.bz2", None),
            ]
            assert sorted(f["attributes"]["url"] for f in files) == [
                f"{DATA_URL}/{name}/OUTCAR{'.bz2' if name == 'MgO/relax' else ''}"
                for name in sorted(records)
            ]
            assert "sha256" not in files[0]["attributes"]
            revisions = get("/v1/_httk_records/example.records-1-3/_httk_revs")["data"]
            assert len(revisions) == 1
            # type_in_base keeps ids distinct across entry types.
            assert len({records["Fe/relax"]["id"], fe["id"], files[0]["id"]}) == 3

        # Re-run NaCl/relax as documented: a new energy and a new relaxed cell.
        calculation = root / "calculations" / "NaCl" / "relax"
        for name, old, new in (
            ("OUTCAR", "-6.83000000", "-6.85000000"),
            ("CONTCAR", "4.02", "4.03"),
        ):
            text = (calculation / name).read_text(encoding="utf-8")
            assert text.count(old) == 3, (name, text)
            (calculation / name).write_text(text.replace(old, new), encoding="utf-8")
        # Not in the page's tree: a noncollinear run, whose mag= is a vector. It
        # sorts after NaCl, so the documented re-run ids are unchanged.
        noncollinear = root / "calculations" / "Zn" / "noncollinear"
        noncollinear.mkdir(parents=True)
        cell = "Zn\n1.0\n{a} 0 0\n0 {a} 0\n0 0 {a}\nZn\n1\nDirect\n0 0 0\n"
        (noncollinear / "POSCAR").write_text(cell.format(a=2.60), encoding="utf-8")
        (noncollinear / "CONTCAR").write_text(cell.format(a=2.65), encoding="utf-8")
        text = (calculation / "OUTCAR").read_text(encoding="utf-8")
        encut = "   ENCUT  =  520.0 eV\n"
        flag = "   LNONCOLLINEAR =      T  non collinear calculations\n"
        assert text.count(encut) == 1
        (noncollinear / "OUTCAR").write_text(
            text.replace(encut, encut + flag), encoding="utf-8"
        )
        (noncollinear / "OSZICAR").write_text(
            "   1 F= -.12000000E+01 E0= -.12000000E+01  d E =0.000000E+00"
            "  mag=     0.1000     0.2000     2.2000\n",
            encoding="utf-8",
        )
        ingest = run("ingest_vasp.py")
        assert ingest.stdout == "ingested 5 calculations, skipped 2\n", ingest

        with serving():
            assert [count(t) for t in ("structures", "_httk_records")] == [10, 5]
            assert [count(t) for t in ("_httk_runs", "files")] == [5, 5]
            (zn,) = get(
                "/v1/_httk_records",
                filter='_httk_custom_source_path="Zn/noncollinear"',
                response_fields="_httk_custom_total_magnetization",
            )["data"]
            assert zn["attributes"] == {"_httk_custom_total_magnetization": None}, zn
            nacl = get("/v1/_httk_records/example.records-1-3")["data"]
            assert nacl["attributes"]["_httk_total_energy"] == -6.85
            (link,) = nacl["relationships"]["structures"]["data"]
            assert link["id"] == "example.structures-1-8"
            revisions = get("/v1/_httk_records/example.records-1-3/_httk_revs")["data"]
            assert [r["id"] for r in revisions] == [
                "example.records-1-3~1",
                "example.records-1-3~2",
            ]
            assert [r["attributes"]["_httk_total_energy"] for r in revisions] == [
                -6.83,
                -6.85,
            ]
            for path in ("_httk_runs/example.runs-1-3", "files/example.files-1-3"):
                assert len(get(f"/v1/{path}/_httk_revs")["data"]) == 2, path
            get("/v1/structures/example.structures-1-6")  # the old cell stays
    print(
        f"{page.name}: calculation-tree ingest, re-run revisions, and HTTP serving passed"
    )


if __name__ == "__main__":
    main()
