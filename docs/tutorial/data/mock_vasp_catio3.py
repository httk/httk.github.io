#!/usr/bin/env python3
"""Write canned VASP-like results for the Ca--Ti--O tutorial.

This is a demonstration mock, not VASP: it computes no physical energy.  The
numbers are deliberately chosen to make Ca, Ti, O, CaO, and CaTiO3 stable and
TiO unstable in the tutorial phase diagram.
"""

from pathlib import Path


# These are total energies for the actual unit cells in the bundled CIFs.
_ENERGIES = {
    ("Ca", 4): -4.0,
    ("O", 2): -2.0,
    ("Ti", 6): -6.0,
    ("Ca", 4, "O", 4): -16.0,
    ("O", 10, "Ti", 10): -18.0,
    ("Ca", 1, "O", 3, "Ti", 1): -11.0,
}


def _energy(poscar: list[str]) -> float:
    symbols = poscar[5].split()
    counts = tuple(int(value) for value in poscar[6].split())
    key = tuple(item for pair in sorted(zip(symbols, counts)) for item in pair)
    try:
        return _ENERGIES[key]
    except KeyError as exc:
        raise ValueError(f"no canned Ca-Ti-O energy for POSCAR composition {key!r}") from exc


def main() -> int:
    poscar = Path("POSCAR").read_text(encoding="utf-8").splitlines()
    energy = _energy(poscar)
    Path("OUTCAR").write_text(
        " fake vasp 6.4.1\n"
        "   NELM   =     60;   NELMIN=  2; NELMDL= -5\n"
        "   NSW    =     99    number of steps for IOM\n"
        "   FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)\n"
        f"   free  energy   TOTEN  =       {energy:.8f} eV\n"
        f"   energy  without entropy=      {energy:.8f}  energy(sigma->0) =      {energy:.8f}\n"
        "  General timing and accounting informations for this job:\n",
        encoding="utf-8",
    )
    Path("OSZICAR").write_text(
        "       N       E                     dE             d eps       ncg     rms\n"
        f"   1 F= {energy:.8f} E0= {energy:.8f}  d E ={energy:.8f}\n",
        encoding="utf-8",
    )
    relaxed = list(poscar)
    relaxed[0] = "relaxed by the Ca-Ti-O tutorial mock"
    relaxed[-1] = "0.5100000000 0.5100000000 0.5100000000"
    Path("CONTCAR").write_text("\n".join(relaxed) + "\n", encoding="utf-8")
    Path("vasprun.xml").write_text(
        '<modeling><structure name="finalpos"><crystal>'
        '<i name="volume">      8.00000000 </i></crystal></structure></modeling>\n',
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
