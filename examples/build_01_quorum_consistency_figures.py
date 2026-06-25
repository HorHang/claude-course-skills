"""
Figure generator for the sample chapter (Quorum Consistency).

Run:  python examples/build_01_quorum_consistency_figures.py

Writes a DATA plot to examples/figures/fig_01_stale_read.png. Matplotlib is used
ONLY for the quantitative plot (stale-read probability vs read quorum). The
concept diagram in the notebook is a Mermaid block, not a hand-placed figure.
"""
import os
from math import comb
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless; no display needed
import matplotlib.pyplot as plt

CHAPTER = "01"
OUTPUT_DIR = Path(os.environ.get("BUILD_COURSE_OUTPUT_DIR", Path(__file__).parent))
FIG_DIR = OUTPUT_DIR / "figures"


def _save(fig, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f"fig_{CHAPTER}_{name}.png"
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {path}")


def prob_stale(n: int, w: int, r: int) -> float:
    """Exact probability a read quorum of r misses every one of the w
    up-to-date replicas (i.e. reads only stale copies): C(n-w, r) / C(n, r)."""
    if r > n - w:
        return 0.0
    return comb(n - w, r) / comb(n, r)


def fig_stale_read() -> None:
    """How read-quorum size drives the chance of a stale read (n=5, w=3)."""
    n, w = 5, 3
    rs = list(range(1, n + 1))
    ps = [prob_stale(n, w, r) for r in rs]

    fig, ax = plt.subplots(figsize=(6, 3.6), constrained_layout=True)
    ax.plot(rs, ps, marker="o")
    ax.axvline(n - w + 0.5, color="C3", ls="--", lw=1)
    ax.text(n - w + 0.6, max(ps) * 0.6, "w + r > n\n(stale = 0)", color="C3", fontsize=9)
    ax.set_xticks(rs)
    ax.set_xlabel("read quorum r  (n = 5, w = 3)")
    ax.set_ylabel("P(stale read)")
    ax.set_title("Once w + r > n, stale reads become impossible")
    _save(fig, "stale_read")


if __name__ == "__main__":
    fig_stale_read()
