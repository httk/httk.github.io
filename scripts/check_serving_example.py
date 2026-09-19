"""Execute the CIF/JSON OPTIMADE walkthrough, including its real HTTP client."""

import json
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlencode
from urllib.request import urlopen

def main() -> None:
    """Run the published three-file import and HTTP serving example."""
    page = Path(sys.argv[1]).resolve()
    section = page.read_text(encoding="utf-8").split("Serve data over OPTIMADE", 1)[1]
    blocks = re.findall(r"^```(\w+)\n(.*?)^```", section, re.MULTILINE | re.DOTALL)
    python = [code for language, code in blocks if language == "python"]
    cifs = [
        code
        for language, code in blocks
        if language == "text" and code.startswith("data_")
    ]
    inputs = next(code for language, code in blocks if language == "json")
    assert len(python) == 3 and len(cifs) == 2
    with TemporaryDirectory(prefix="httk-serving-example-") as directory:
        root = Path(directory)
        (root / "cifs").mkdir()
        for name, code in zip(("NaCl.cif", "MgO.cif"), cifs, strict=True):
            (root / "cifs" / name).write_text(code, encoding="utf-8")
        (root / "results.json").write_text(inputs, encoding="utf-8")
        for name, code in zip(
            ("result_record.py", "build_db.py", "serve_db.py"), python, strict=True
        ):
            (root / name).write_text(code, encoding="utf-8")
        # Exercise the documented command twice: the second import must deduplicate.
        for _ in range(2):
            subprocess.run(
                [sys.executable, "build_db.py"], cwd=root, check=True, timeout=60
            )
        (root / "results.json").unlink()
        shutil.rmtree(root / "cifs")
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        base = f"http://127.0.0.1:{port}"

        def get(path, **params):
            with urlopen(base + path + "?" + urlencode(params), timeout=15) as response:
                return json.load(response)

        # The documented script fixes port 8080; use a temporary copy for this check.
        (root / "serve_db.py").write_text(
            python[2].replace("port=8080", f"port={port}"), encoding="utf-8"
        )
        with (root / "server.log").open("w+") as log:
            server = subprocess.Popen(
                [sys.executable, "serve_db.py"],
                cwd=root,
                stdout=log,
                stderr=log,
            )
            try:
                deadline = time.monotonic() + 20
                while True:
                    if server.poll() is not None or time.monotonic() > deadline:
                        log.seek(0)
                        raise AssertionError(f"OPTIMADE server did not start:\n{log.read()}")
                    try:
                        get("/v1/info")
                        break
                    except OSError:
                        time.sleep(0.05)
                records = get("/v1/_httk_records")["data"]
                structures = get("/v1/structures")["data"]
                assert len(records) == len(structures) == 2
                assert {s["attributes"]["nsites"] for s in structures} == {8}
                assert {
                    s["attributes"]["chemical_formula_reduced"] for s in structures
                } == {"ClNa", "MgO"}
                info = get("/v1/info/_httk_records")["data"]["properties"]
                assert info["_httk_custom_formation_energy"]["x-optimade-unit"] == "eV"
                assert info["_httk_custom_formation_energy"]["sortable"]
                payload = get(
                    "/v1/_httk_records",
                    filter="_httk_custom_formation_energy < -1",
                    include="structures",
                )
                (result,) = payload["data"]
                assert result["attributes"]["_httk_custom_formation_energy"] == -1.2
                (link,) = result["relationships"]["structures"]["data"]
                assert [(s["type"], s["id"]) for s in payload["included"]] == [
                    ("structures", link["id"])
                ]
                related = get("/v1/_httk_records", filter='structures.elements HAS "Na"')
                assert [r["id"] for r in related["data"]] == [result["id"]]
                sorted_records = get(
                    "/v1/_httk_records", sort="-_httk_custom_formation_energy"
                )["data"]
                assert [
                    r["attributes"]["_httk_custom_formation_energy"]
                    for r in sorted_records
                ] == [-0.8, -1.2]
            finally:
                server.terminate()
                try:
                    server.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()
                    raise AssertionError("OPTIMADE server did not stop") from None
    print(
        f"{page.name}: three-file import, reopen, relationships, and HTTP serving passed"
    )


if __name__ == "__main__":
    main()
