"""
Build the README hero animation: how PagedAttention fixes the KV-cache memory
problem, step by step.

This is a worked demonstration of the *fourth* visualization tier that
build-course ships (see skills/build-course/references/interactive-visualization.md):
an animated explainer rendered with matplotlib + Pillow only — no ffmpeg, manim,
GPU, or web stack — so it runs on the repo's dependency floor and renders inline
on GitHub.

It dramatizes the running example from the vLLM / PagedAttention paper
(Kwon et al., 2023, arXiv:2309.06180, Figures 2, 3 and 6):

    prompt  = "Four score and seven years ago our"   (7 tokens, block size 4)
    outputs = "fathers", "brought", ...

walking a reader from the problem (KV-cache memory is 60-80% wasted) to the
mechanism (page the cache into fixed-size blocks mapped by a block table, like
OS virtual memory) to the payoff (near-zero waste -> more requests batched).

Run:
    python examples/build_pagedattention_animation.py

Writes examples/figures/pagedattention.gif (+ four QA snapshot PNGs).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")  # headless; no display needed
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUTPUT_DIR = Path(__file__).resolve().parent / "figures"
FPS = 11

# --- palette -------------------------------------------------------------
INK = "#1d3557"          # primary text / strokes
USED = "#2a9d8f"         # KV slots actually used
WASTE = "#e9ecef"        # reserved / wasted memory
WASTE_EDGE = "#ced4da"
FRAG = "#f4a261"         # fragmentation highlight
ALLOC = "#e76f51"        # a freshly allocated physical block
TABLE = "#a8dadc"        # block-table fill
PHYS = "#457b9d"         # physical-block accent
PAPER = "#f8f9fa"        # canvas background

PROMPT = ["Four", "score", "and", "seven", "years", "ago", "our"]
BLOCK = 4  # KV block size in the paper's running example


def _cell(ax, x: float, y: float, w: float, h: float, text: str = "", *,
          fc: str = "white", ec: str = INK, tc: str = INK, fs: float = 8.0,
          lw: float = 1.2, alpha: float = 1.0, hatch: str | None = None,
          weight: str = "normal") -> None:
    """Draw one labelled rounded box on the 0-100 canvas."""
    box = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8",
        linewidth=lw, edgecolor=ec, facecolor=fc, alpha=alpha, hatch=hatch,
    )
    ax.add_patch(box)
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, color=tc, weight=weight, zorder=5)


def _arrow(ax, x1: float, y1: float, x2: float, y2: float, *,
           color: str = INK, lw: float = 1.4, style: str = "-|>") -> None:
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle=style, mutation_scale=11,
        color=color, lw=lw, shrinkA=1, shrinkB=1, zorder=4))


def _frame(ax, title: str, subtitle: str, step: int, n_steps: int) -> None:
    """Reset the canvas and draw the persistent title / step indicator."""
    ax.clear()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 100, 100, boxstyle="square,pad=0",
                                facecolor=PAPER, edgecolor="none", zorder=0))
    ax.text(4, 94, title, ha="left", va="center", fontsize=15,
            weight="bold", color=INK)
    if subtitle:
        ax.text(4, 87.5, subtitle, ha="left", va="center", fontsize=9.5,
                color="#52677d")
    for k in range(n_steps):
        on = k == step
        ax.add_patch(plt.Circle((90 + k * 2.6, 93), 0.8,
                                 color=USED if on else WASTE_EDGE, zorder=5))


def _caption(ax, text: str, *, color: str = INK) -> None:
    ax.text(50, 5.5, text, ha="center", va="center", fontsize=10,
            color=color, style="italic")


# --- scene 1: the problem ------------------------------------------------
def scene_problem(ax, p: float) -> None:
    _frame(ax, "The problem: the KV cache wastes most of GPU memory",
           "Classic serving reserves one contiguous slab per request — sized to the longest it *might* get.",
           0, 4)
    base_x, w, h, gap = 8.0, 5.2, 11.0, 0.6
    y_a = 60
    # request A reserves a contiguous 12-slot slab; only a few hold real tokens.
    reserved = 12
    used = min(5, 1 + int(p * 6))  # fill used slots one-by-one
    ax.text(base_x, y_a + h + 4, "Request A  — reserves 12 slots (its max length)",
            fontsize=9.5, color=INK, weight="bold")
    for i in range(reserved):
        x = base_x + i * (w + gap)
        if i < used:
            _cell(ax, x, y_a, w, h, PROMPT[i] if i < len(PROMPT) else "tok",
                  fc=USED, tc="white", fs=7.5, weight="bold")
        else:
            _cell(ax, x, y_a, w, h, "", fc=WASTE, ec=WASTE_EDGE, hatch="////")
    if p > 0.4:
        x0 = base_x + used * (w + gap)
        x1 = base_x + reserved * (w + gap) - gap
        ax.annotate("", xy=(x1, y_a - 3), xytext=(x0, y_a - 3),
                    arrowprops=dict(arrowstyle="<->", color=FRAG, lw=2))
        ax.text((x0 + x1) / 2, y_a - 7, "reserved + internal fragmentation (never used)",
                ha="center", fontsize=9, color=FRAG, weight="bold")
    # request B cannot fit in the leftover gap -> external fragmentation
    if p > 0.62:
        y_b = 34
        need, gap_slots = 6, 4
        ax.text(base_x, y_b + h + 3.5,
                "Request B needs 6 slots — but only a 4-slot gap is left",
                fontsize=9.5, color=INK, weight="bold")
        for i in range(need):
            x = base_x + i * (w + gap)
            fits = i < gap_slots
            _cell(ax, x, y_b, w, h, "", fc="white" if fits else "#fde0dc",
                  ec=WASTE_EDGE if fits else ALLOC,
                  hatch=None if fits else "xx")
        if p > 0.8:
            ax.text(base_x + need * (w + gap) + 2.5, y_b + h / 2,
                    "✗ can't fit  →  external fragmentation",
                    fontsize=10, color=ALLOC, weight="bold", va="center")
    _caption(ax, "Only 20–38% of KV-cache memory holds real tokens — 60–80% is wasted.  (vLLM, Fig. 2)",
             color=ALLOC if p > 0.8 else INK)


# --- scene 2: the idea ---------------------------------------------------
def scene_idea(ax, p: float) -> None:
    _frame(ax, "The idea: page the KV cache, like OS virtual memory",
           "Cut the cache into fixed-size blocks (here B = 4). Blocks live anywhere — a block table maps logical → physical.",
           1, 4)
    w, h = 8.6, 12.0
    # logical blocks fill left-to-right and are revealed one block at a time.
    blocks = [PROMPT[i:i + BLOCK] for i in range(0, len(PROMPT), BLOCK)]
    n_show = 1 + int(p * len(blocks) * 1.2)
    y_l = 58
    ax.text(8, y_l + h + 3, "Logical blocks (contiguous, per request)",
            fontsize=9.5, color=INK, weight="bold")
    for bi, toks in enumerate(blocks):
        if bi >= n_show:
            break
        bx = 8 + bi * (w * 1.5)
        _cell(ax, bx, y_l, w, h, "", fc="white", ec=INK, lw=1.6)
        for ti in range(BLOCK):
            t = toks[ti] if ti < len(toks) else ""
            yy = y_l + 0.6 + (BLOCK - 1 - ti) * (h - 1.2) / BLOCK  # token 0 on top
            _cell(ax, bx + 0.6, yy, w - 1.2,
                  (h - 1.2) / BLOCK - 0.4, t, fc=USED if t else WASTE,
                  ec="white", tc="white" if t else WASTE_EDGE, fs=7,
                  weight="bold")
        ax.text(bx + w / 2, y_l - 3.5, f"block {bi}", ha="center",
                fontsize=8.5, color=INK)
    # scatter blocks to non-contiguous physical slots
    if p > 0.5:
        y_p = 24
        ax.text(8, y_p + h + 3, "Physical GPU memory (non-contiguous)",
                fontsize=9.5, color=INK, weight="bold")
        for px in range(0, 9):
            bx = 8 + px * (w * 1.0)
            filled = px in (3, 6)
            _cell(ax, bx, y_p, w * 0.92, h, f"#{px}", fc=PHYS if filled else WASTE,
                  ec=INK if filled else WASTE_EDGE,
                  tc="white" if filled else WASTE_EDGE, fs=8,
                  alpha=1.0 if filled else 0.7)
        # arrows from each logical block to a scattered physical block
        targets = {0: 3, 1: 6}
        for bi in range(min(len(blocks), n_show)):
            if bi in targets:
                sx = 8 + bi * (w * 1.5) + w / 2
                tx = 8 + targets[bi] * (w * 1.0) + w * 0.46
                _arrow(ax, sx, y_l - 5, tx, y_p + h + 1, color=PHYS, lw=1.3)
    _caption(ax, "A block can sit anywhere in GPU memory — allocate one only when a request actually needs it.")


# --- scene 3: the mechanism (the paper's running example) ----------------
def scene_mechanism(ax, p: float) -> None:
    # three sub-steps: prefill -> generate "fathers" -> allocate for "brought"
    sub = 0 if p < 0.34 else (1 if p < 0.67 else 2)
    subtitle = {
        0: 'Prefill: 7 prompt tokens fill logical blocks 0–1 → physical blocks 7 and 1.',
        1: 'Decode ①: generate "fathers" into the last free slot of block 1 — no new memory.',
        2: 'Decode ②: block 1 is full → allocate a NEW physical block (3) on demand for "brought".',
    }[sub]
    _frame(ax, 'How it runs:  prompt "Four score and seven years ago our"',
           subtitle, 2, 4)

    # logical block contents per sub-step
    b0 = ["Four", "score", "and", "seven"]
    b1 = ["years", "ago", "our", ("fathers" if sub >= 1 else "")]
    b2 = ["brought", "", "", ""] if sub >= 2 else ["", "", "", ""]
    logical = [("block 0", b0), ("block 1", b1)]
    if sub >= 2:
        logical.append(("block 2", b2))

    # --- left: logical blocks ---
    lx, lw_, lh = 4.0, 18.0, 13.0
    ax.text(lx, 81, "Logical blocks", fontsize=10, color=INK, weight="bold")
    slot_w = (lw_ - 1.2) / BLOCK
    for bi, (label, toks) in enumerate(logical):
        ly = 64 - bi * (lh + 3)
        _cell(ax, lx, ly, lw_, lh, "", fc="white", ec=INK, lw=1.6)
        for ti, t in enumerate(toks):
            fresh = (sub == 1 and bi == 1 and ti == 3) or (sub == 2 and bi == 2 and ti == 0)
            _cell(ax, lx + 0.6 + ti * slot_w, ly + 1.2, slot_w - 0.5, lh - 2.4,
                  t, fc=(ALLOC if fresh else USED) if t else WASTE,
                  ec="white", tc="white" if t else WASTE_EDGE, fs=6.5,
                  weight="bold")
        ax.text(lx - 0.2, ly + lh / 2, label, ha="right", va="center",
                fontsize=8, color=INK, rotation=90)

    # --- middle: block table ---
    tx, tw = 30.0, 24.0
    ax.text(tx, 81, "Block table", fontsize=10, color=INK, weight="bold")
    rows = [("logical", "physical", "# filled")]
    rows.append(("0", "7", "4"))
    rows.append(("1", "1", "4" if sub >= 1 else "3"))
    if sub >= 2:
        rows.append(("2", "3", "1"))
    rh = 8.5
    for ri, (a, b, c) in enumerate(rows):
        ry = 70 - ri * rh
        head = ri == 0
        new = (sub == 2 and ri == 3)
        for ci, val in enumerate((a, b, c)):
            _cell(ax, tx + ci * (tw / 3), ry, tw / 3, rh, val,
                  fc=INK if head else (ALLOC if new else TABLE),
                  tc="white" if (head or new) else INK,
                  ec="white", fs=8, weight="bold" if head else "normal")

    # --- right: physical GPU blocks ---
    px, pw, ph = 60.0, 36.0, 6.3
    ax.text(px, 81, "Physical KV blocks (GPU DRAM)", fontsize=10, color=INK,
            weight="bold")
    for blk in range(9):
        py = 74 - blk * (ph + 1.1)
        content = None
        fresh = False
        if blk == 7:
            content = ["Four", "score", "and", "seven"]
        elif blk == 1:
            content = ["years", "ago", "our", "fathers" if sub >= 1 else ""]
            fresh = sub == 1
        elif blk == 3 and sub >= 2:
            content, fresh = ["brought", "", "", ""], True
        ax.text(px - 1.2, py + ph / 2, f"#{blk}", ha="right", va="center",
                fontsize=7.5, color=INK)
        if content is None:
            _cell(ax, px, py, pw, ph, "", fc=WASTE, ec=WASTE_EDGE)
            continue
        _cell(ax, px, py, pw, ph, "", fc="white",
              ec=ALLOC if fresh else PHYS, lw=2.0 if fresh else 1.4)
        sw = pw / BLOCK
        for ti in range(BLOCK):
            t = content[ti] if ti < len(content) else ""
            cellfresh = fresh and t and (
                (blk == 1 and ti == 3) or (blk == 3 and ti == 0))
            _cell(ax, px + ti * sw + 0.4, py + 0.5, sw - 0.8, ph - 1.0, t,
                  fc=(ALLOC if cellfresh else PHYS) if t else "white",
                  ec="white", tc="white" if t else "white", fs=6.2,
                  weight="bold")

    # block-table -> physical arrows
    arrow_map = {0: 7, 1: 1}
    if sub >= 2:
        arrow_map[2] = 3
    for li, blk in arrow_map.items():
        ry = 70 - (li + 1) * rh + rh / 2
        py = 74 - blk * (ph + 1.1) + ph / 2
        _arrow(ax, tx + tw + 0.5, ry, px - 4.5, py, color=PHYS, lw=1.1)

    _caption(ax, "Blocks fill left-to-right; a new physical block is allocated ONLY when the last one fills — zero reservation, near-zero waste.")


# --- scene 4: the payoff -------------------------------------------------
def scene_payoff(ax, p: float) -> None:
    _frame(ax, "The payoff: pack memory tight → batch more → serve faster",
           "Same GPU, same model — PagedAttention just stops wasting the KV cache.",
           3, 4)
    bar_x, bar_w, bar_h = 14, 60, 13
    # contiguous: mostly wasted
    y1 = 60
    ax.text(bar_x, y1 + bar_h + 3, "Contiguous allocation", fontsize=10,
            color=INK, weight="bold")
    used_frac = 0.3
    _cell(ax, bar_x, y1, bar_w, bar_h, "", fc=WASTE, ec=WASTE_EDGE, hatch="////")
    _cell(ax, bar_x, y1, bar_w * used_frac, bar_h, "~30% used", fc=USED,
          tc="white", fs=9, weight="bold")
    ax.text(bar_x + bar_w + 1.5, y1 + bar_h / 2, "few requests fit",
            va="center", fontsize=9, color="#52677d")
    # paged: packed
    y2 = 32
    fill = min(1.0, 0.2 + p)
    ax.text(bar_x, y2 + bar_h + 3, "PagedAttention", fontsize=10, color=INK,
            weight="bold")
    _cell(ax, bar_x, y2, bar_w, bar_h, "", fc=WASTE, ec=WASTE_EDGE)
    n_blocks = 14
    for i in range(n_blocks):
        if i / n_blocks > fill:
            break
        bw = bar_w / n_blocks
        _cell(ax, bar_x + i * bw, y2, bw - 0.4, bar_h, "",
              fc=USED if i % 2 == 0 else PHYS, ec="white")
    ax.text(bar_x + bar_w + 1.5, y2 + bar_h / 2, "many more batched",
            va="center", fontsize=9, color=USED, weight="bold")
    _caption(ax, "Near-zero waste → up to 2–4× more sequences in a batch → higher throughput.  (vLLM)")


SCHEDULE: list[tuple[Callable, int]] = [
    (scene_problem, 26),
    (scene_idea, 22),
    (scene_mechanism, 42),
    (scene_payoff, 20),
]
HOLD = 10  # extra frames on the final frame of each scene so it reads in a loop


def _render(ax, i: int) -> None:
    cursor = 0
    for fn, n in SCHEDULE:
        if i < cursor + n:
            p = (i - cursor) / max(1, n - 1)
            fn(ax, min(1.0, p))
            return
        cursor += n
        if i < cursor + HOLD:
            fn(ax, 1.0)
            return
        cursor += HOLD
    SCHEDULE[-1][0](ax, 1.0)


def build() -> Path:
    """Render examples/figures/pagedattention.gif and QA snapshot PNGs."""
    import matplotlib.animation as animation

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total = sum(n + HOLD for _, n in SCHEDULE)
    fig, ax = plt.subplots(figsize=(11, 6.2))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # QA: with BUILD_QA=1, dump the final frame of each scene as a PNG so the
    # layout can be eyeballed without scrubbing the GIF.
    if os.environ.get("BUILD_QA"):
        for si, (fn, _n) in enumerate(SCHEDULE):
            fn(ax, 1.0)
            fig.savefig(OUTPUT_DIR / f"pagedattention_scene{si}.png", dpi=110,
                        facecolor=PAPER)

    anim = animation.FuncAnimation(fig, lambda i: _render(ax, i),
                                   frames=total, interval=1000 // FPS)
    gif_path = OUTPUT_DIR / "pagedattention.gif"
    anim.save(gif_path, writer=animation.PillowWriter(fps=FPS), dpi=96)
    plt.close(fig)
    print(f"wrote {gif_path} ({total} frames)")
    return gif_path


if __name__ == "__main__":
    build()
