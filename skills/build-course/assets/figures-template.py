"""
Template figure generator for a single chapter.

Copy this to <course>/build_<ch>_figures.py, add one function per figure, then run:
    python <course>/build_<ch>_figures.py

Writes PNGs to <OUTPUT_DIR>/figures/fig_<ch>_<name>.png, referenced from the
notebook markdown as ![caption](figures/fig_<ch>_<name>.png).

============================================================================
USE MATPLOTLIB ONLY FOR QUANTITATIVE DATA PLOTS.
============================================================================
Good matplotlib figures: distributions, curves, scatter, histograms,
benchmarks, roofline, learning curves — anything with axes and numbers.

DO NOT hand-place boxes/arrows/text to draw a CONCEPT MAP, TAXONOMY, LIST,
FLOW, or ARCHITECTURE in matplotlib. Manually positioned boxes overlap and
render as garbage (collided titles, text spilling out of boxes). For those,
emit the diagram AS MARKDOWN in the notebook instead — a table, a Mermaid
diagram, or a small ASCII box diagram. See notebook-blueprint.md
("Visualization decision"). It looks better, stays editable, and never
collides.

Rules for the matplotlib figures you DO draw:
- Always use constrained_layout=True so titles/labels never overlap.
- One insight per figure; the title states the insight.
- Keep the title short; if it wraps, shorten it — do not let it collide.
- Draw real data (compute it), not decorative shapes.
"""
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless; no display needed
import matplotlib.pyplot as plt

CHAPTER = "03"  # match build_<ch>.py
OUTPUT_DIR = Path(os.environ.get("BUILD_COURSE_OUTPUT_DIR", "course"))
FIG_DIR = OUTPUT_DIR / "figures"


def _save(fig, name: str, ext: str = "png") -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f"fig_{CHAPTER}_{name}.{ext}"
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {path}")
    return path


def _filmstrip(frame_fn, n_frames: int, name: str, figsize=(6, 3.4)) -> Path:
    """Static fallback for animate_to_gif: up to 4 evenly-spaced frames side by side."""
    import numpy as np
    k = min(n_frames, 4)
    idx = np.linspace(0, n_frames - 1, k).astype(int)
    fig, axes = plt.subplots(1, k, figsize=(figsize[0] * k / 2.0, figsize[1]),
                             constrained_layout=True)
    axes = np.atleast_1d(axes)
    for ax, i in zip(axes, idx):
        frame_fn(ax, int(i))
        ax.set_title(f"step {int(i)}")
    return _save(fig, name, ext="png")


def animate_to_gif(frame_fn, n_frames: int, name: str, *, fps: int = 12,
                   figsize: tuple[float, float] = (6, 3.4)) -> Path:
    """Render an animation to fig_<ch>_<name>.gif via matplotlib + Pillow.

    Use this only when MOTION teaches better than a still frame (a transform, a
    gradient-descent path, an iterative algorithm). If the Pillow writer is
    unavailable, degrade to a static multi-panel "filmstrip" PNG so the artifact
    always exists and the reviewer stays green.

    Args:
        frame_fn: Callable (ax, i) that draws frame i (0-based) onto the Axes.
        n_frames: Number of frames.
        name: Figure slug; output is fig_<ch>_<name>.(gif|png).
        fps: Frames per second for the GIF.
        figsize: Per-frame figure size in inches.

    Returns:
        Path to the written .gif (or the .png filmstrip fallback).
    """
    import matplotlib.animation as animation
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)

    def _update(i):
        ax.clear()
        frame_fn(ax, i)

    try:
        anim = animation.FuncAnimation(fig, _update, frames=n_frames,
                                       interval=max(1, 1000 // fps))
        gif_path = FIG_DIR / f"fig_{CHAPTER}_{name}.gif"
        anim.save(gif_path, writer=animation.PillowWriter(fps=fps))
        plt.close(fig)
        print(f"wrote {gif_path}")
        return gif_path
    except Exception as e:  # noqa: BLE001 - any writer failure degrades to static
        plt.close(fig)
        print(f"NOTE animation writer unavailable ({type(e).__name__}); writing static filmstrip")
        return _filmstrip(frame_fn, n_frames, name, figsize=figsize)


def loss_surface(loss_fn, name: str, *, span: float = 1.0, n: int = 40,
                 interactive: bool = True) -> Path:
    """Plot a 2D slice of a loss surface over (d1, d2) in [-span, span]^2.

    `loss_fn(a, b) -> float` stands in for the loss along two (ideally
    filter-normalized) random directions around a trained point, à la
    Li et al. "Visualizing the Loss Landscape of Neural Nets". When plotly is
    installed and `interactive`, also writes an interactive HTML; a static
    matplotlib 3D PNG is ALWAYS written and its path returned.

    Args:
        loss_fn: Scalar loss at grid point (a, b).
        name: Figure slug; outputs fig_<ch>_<name>.png (+ optional .html).
        span: Half-width of the grid in each direction.
        n: Grid resolution per axis.
        interactive: Try to also emit an interactive plotly HTML.

    Returns:
        Path to the static PNG (the guaranteed artifact).
    """
    import numpy as np
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 - registers the 3d projection
    grid = np.linspace(-span, span, n)
    A, B = np.meshgrid(grid, grid)
    Z = np.vectorize(loss_fn)(A, B)

    if interactive:
        try:
            import plotly.graph_objects as go
            FIG_DIR.mkdir(parents=True, exist_ok=True)
            html_path = FIG_DIR / f"fig_{CHAPTER}_{name}.html"
            go.Figure(data=[go.Surface(x=A, y=B, z=Z)]).write_html(html_path)
            print(f"wrote {html_path}")
        except Exception as e:  # noqa: BLE001 - plotly missing -> static PNG only
            print(f"NOTE plotly unavailable ({type(e).__name__}); static PNG only")

    fig = plt.figure(figsize=(5.5, 4.2), constrained_layout=True)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(A, B, Z, cmap="viridis")
    ax.set_xlabel("direction 1"); ax.set_ylabel("direction 2"); ax.set_zlabel("loss")
    ax.set_title("Loss surface (filter-normalized slice)")
    return _save(fig, name, ext="png")


def fig_distribution() -> None:
    """Example DATA plot: a posterior-like distribution. Title = the insight."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(6, 3.4), constrained_layout=True)
    x = np.linspace(0, 1, 200)
    y = (x ** 6) * ((1 - x) ** 3)
    y /= y.sum() * (x[1] - x[0])
    ax.plot(x, y)
    ax.fill_between(x, y, alpha=0.2)
    ax.set_xlabel("proportion water")
    ax.set_ylabel("plausibility")
    ax.set_title("More data sharpens the estimate")
    _save(fig, "distribution")


if __name__ == "__main__":
    fig_distribution()
    # add calls to your other fig_* functions here — DATA PLOTS ONLY.
    # Concept maps / taxonomies / flows go in the notebook as markdown
    # (table / Mermaid / ASCII), NOT here.
