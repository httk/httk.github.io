"""Execute the CIF/JSON OPTIMADE walkthrough, including its real HTTP client."""

import importlib
import json
import re
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlencode
from urllib.request import urlopen

import uvicorn
from httk.serve.optimade import create_asgi_app


def main() -> None:
    """Run the published import, local query, HTTP requests, and remote query."""
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
    expected_item = json.loads(
        [code for language, code in blocks if language == "json"][1]
    )
    assert len(python) == 3 and len(cifs) == 2
    with TemporaryDirectory(prefix="httk-serving-example-") as directory:
        root = Path(directory)
        (root / "cifs").mkdir()
        for name, code in zip(("NaCl.cif", "MgO.cif"), cifs, strict=True):
            (root / "cifs" / name).write_text(code, encoding="utf-8")
        (root / "results.json").write_text(inputs, encoding="utf-8")
        (root / "api.py").write_text(python[0], encoding="utf-8")
        # Exercise the documented command twice: the second import must deduplicate.
        for _ in range(2):
            subprocess.run(
                [sys.executable, "api.py", "build"], cwd=root, check=True, timeout=60
            )
        sys.path.insert(0, directory)
        try:
            api = importlib.import_module("api")
            (root / "query.py").write_text(python[1], encoding="utf-8")
            output = subprocess.run(
                [sys.executable, "query.py"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            assert output.stdout.strip() == "ClNa -1.2", output.stdout
            with api.open_store() as store, socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
                server = uvicorn.Server(
                    uvicorn.Config(create_asgi_app(store), log_level="error")
                )
                thread = threading.Thread(
                    target=server.run, kwargs={"sockets": [listener]}, daemon=True
                )
                thread.start()
                try:
                    deadline = time.monotonic() + 15
                    while (
                        not server.started
                        and thread.is_alive()
                        and time.monotonic() < deadline
                    ):
                        time.sleep(0.05)
                    assert server.started, "OPTIMADE server did not start"
                    base = f"http://127.0.0.1:{port}"

                    def get(path, **params):
                        with urlopen(
                            base + path + "?" + urlencode(params), timeout=15
                        ) as response:
                            return json.load(response)

                    records = get("/v1/_httk_records")["data"]
                    structures = get("/v1/structures")["data"]
                    assert len(records) == len(structures) == 2
                    assert {s["attributes"]["nsites"] for s in structures} == {8}
                    assert {
                        s["attributes"]["chemical_formula_reduced"] for s in structures
                    } == {"ClNa", "MgO"}
                    info = get("/v1/info/_httk_records")["data"]["properties"]
                    assert (
                        info["_httk_custom_formation_energy"]["x-optimade-unit"] == "eV"
                    )
                    assert info["_httk_custom_formation_energy"]["sortable"]
                    payload = get(
                        "/v1/_httk_records",
                        filter="_httk_custom_formation_energy < -1",
                        include="structures",
                        response_fields="_httk_custom_formation_energy",
                    )
                    assert payload["data"] == [expected_item], payload["data"]
                    linked_id = expected_item["relationships"]["structures"]["data"][0][
                        "id"
                    ]
                    assert [(s["type"], s["id"]) for s in payload["included"]] == [
                        ("structures", linked_id)
                    ]
                    related = get(
                        "/v1/_httk_records", filter='structures.elements HAS "Na"'
                    )
                    assert [r["id"] for r in related["data"]] == [expected_item["id"]]
                    sorted_records = get(
                        "/v1/_httk_records", sort="-_httk_custom_formation_energy"
                    )["data"]
                    assert [
                        r["attributes"]["_httk_custom_formation_energy"]
                        for r in sorted_records
                    ] == [-0.8, -1.2]
                    (root / "remote_query.py").write_text(
                        python[2].replace("http://127.0.0.1:8080", base),
                        encoding="utf-8",
                    )
                    output = subprocess.run(
                        [sys.executable, "remote_query.py"],
                        cwd=root,
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    assert output.stdout.strip() == "ClNa -1.2", output.stdout
                finally:
                    server.should_exit = True
                    thread.join(timeout=15)
                    assert not thread.is_alive(), "OPTIMADE server did not stop"
        finally:
            sys.path.remove(directory)
            sys.modules.pop("api", None)
    print(
        f"{page.name}: CIF/JSON import, reopen, relationships, and HTTP client passed"
    )


if __name__ == "__main__":
    main()
