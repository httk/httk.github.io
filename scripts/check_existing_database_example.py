"""Execute the existing-database OPTIMADE walkthrough, including its real HTTP client."""

import json
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen


def main() -> None:
    """Run the published existing-database serving example."""
    page = Path(sys.argv[1]).resolve()
    section = page.read_text(encoding="utf-8").split("From an existing database", 1)[1]
    blocks = re.findall(r"^```(\w+)\n(.*?)^```", section, re.MULTILINE | re.DOTALL)
    python = [code for language, code in blocks if language == "python"]
    assert len(python) == 2
    with TemporaryDirectory(prefix="httk-existing-db-example-") as directory:
        root = Path(directory)
        (root / "make_example_db.py").write_text(python[0], encoding="utf-8")
        subprocess.run(
            [sys.executable, "make_example_db.py"], cwd=root, check=True, timeout=60
        )
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        base = f"http://127.0.0.1:{port}"

        def get(path, **params):
            with urlopen(base + path + "?" + urlencode(params), timeout=15) as response:
                return json.load(response)

        # The documented script fixes port 8080; use a temporary copy for this check.
        assert "port=8080" in python[1]
        (root / "serve_db.py").write_text(
            python[1].replace("port=8080", f"port={port}"), encoding="utf-8"
        )
        with (root / "server.log").open("w+") as log:
            server = subprocess.Popen(
                [sys.executable, "serve_db.py"], cwd=root, stdout=log, stderr=log
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
                info = get("/v1/info/structures")["data"]["properties"]
                assert {"nelements", "elements", "_example_band_gap"} <= set(info)
                na = get("/v1/structures", filter='elements HAS "Na"')["data"]
                assert sorted(s["id"] for s in na) == ["1", "3"]
                one = get("/v1/structures/3")["data"]
                assert one["id"] == "3"
                assert one["attributes"]["nelements"] == 2
                page_two = get("/v1/structures", sort="-nsites", page_limit=2)
                assert [s["attributes"]["nsites"] for s in page_two["data"]] == [8, 4]
                assert page_two["links"]["next"]
                low_gap = get("/v1/structures", filter="_example_band_gap < 1")["data"]
                assert sorted(s["id"] for s in low_gap) == ["3", "5"]
                try:
                    get("/v1/structures", filter="nelements=2")
                except HTTPError as error:
                    assert error.code == 501, error.code
                else:
                    raise AssertionError("computed property filter did not fail")
            finally:
                server.terminate()
                try:
                    server.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()
                    raise AssertionError("OPTIMADE server did not stop") from None
    print(f"{page.name}: existing-database mapping and HTTP serving passed")


if __name__ == "__main__":
    main()
