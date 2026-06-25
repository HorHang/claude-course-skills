"""
Figure generator for the sample chapter (BPE tokenizer, repo-sourced).

Run:  python examples/build_02_bpe_tokenizer_figures.py

Writes a DATA plot to examples/figures/fig_02_compression.png — the token
sequence length as a function of the number of BPE merges, measured on a fixed
sample text. Matplotlib is used only for this quantitative plot.
"""
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless; no display needed
import matplotlib.pyplot as plt

CHAPTER = "02"
OUTPUT_DIR = Path(os.environ.get("BUILD_COURSE_OUTPUT_DIR", Path(__file__).parent))
FIG_DIR = OUTPUT_DIR / "figures"

SAMPLE = (
    "the quick brown fox jumps over the lazy dog. " * 12
    + "byte pair encoding merges the most frequent pair, again and again. " * 12
)


def _save(fig, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f"fig_{CHAPTER}_{name}.png"
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {path}")


def get_stats(ids: list[int]) -> dict[tuple[int, int], int]:
    counts: dict[tuple[int, int], int] = {}
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair, 0) + 1
    return counts


def merge(ids: list[int], pair: tuple[int, int], idx: int) -> list[int]:
    out, i = [], 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            out.append(idx)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


def fig_compression() -> None:
    """Sequence length vs. number of merges (the whole point of BPE)."""
    ids = list(SAMPLE.encode("utf-8"))
    lengths = [len(ids)]
    for i in range(60):
        stats = get_stats(ids)
        if not stats:
            break
        pair = max(stats, key=stats.get)
        ids = merge(ids, pair, 256 + i)
        lengths.append(len(ids))

    fig, ax = plt.subplots(figsize=(6, 3.6), constrained_layout=True)
    ax.plot(range(len(lengths)), lengths, marker=".")
    ax.set_xlabel("number of BPE merges")
    ax.set_ylabel("token sequence length")
    ax.set_title("Each merge shortens the sequence (diminishing returns)")
    _save(fig, "compression")


if __name__ == "__main__":
    fig_compression()
