import importlib.util
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "skills/build-course/assets"


def _load(filename):
    """Load a hyphen-named template file as a module (import-safe: the write
    block is guarded under __main__, so importing only defines helpers)."""
    path = ASSETS / filename
    spec = importlib.util.spec_from_file_location(filename.replace("-", "_").replace(".py", ""), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_interactive_callout_emits_cited_markdown(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # guard: importing must not write a notebook here
    build = _load("build-script-template.py")
    cell = build.interactive_callout(
        name="Transformer Explainer",
        url="https://poloclub.github.io/transformer-explainer/",
        why="See live GPT-2 attention as it predicts the next token.",
        tier="link-out",
    )
    assert cell["cell_type"] == "markdown"
    src = cell["source"]
    assert "Transformer Explainer" in src
    assert "https://poloclub.github.io/transformer-explainer/" in src
    assert "live GPT-2 attention" in src
    assert src.lstrip().startswith(">")  # renders as a callout/blockquote
    # importing the template must not have written a notebook into cwd
    assert not list(tmp_path.glob("*.ipynb"))


def test_animate_to_gif_writes_an_artifact(tmp_path):
    figs = _load("figures-template.py")
    figs.OUTPUT_DIR = tmp_path / "course"          # honor the per-test dir
    figs.FIG_DIR = figs.OUTPUT_DIR / "figures"

    def frame(ax, i):
        ax.plot([0, 1], [0, i])
        ax.set_ylim(0, 5)

    out = figs.animate_to_gif(frame, n_frames=5, name="anim_demo", fps=8)
    assert out.exists()                            # gif OR filmstrip png — always exists
    assert out.suffix in {".gif", ".png"}


def test_loss_surface_always_writes_static_png(tmp_path):
    figs = _load("figures-template.py")
    figs.OUTPUT_DIR = tmp_path / "course"
    figs.FIG_DIR = figs.OUTPUT_DIR / "figures"

    out = figs.loss_surface(lambda a, b: a ** 2 + b ** 2, name="bowl", n=12)
    assert out.exists() and out.suffix == ".png"   # static PNG is the guaranteed return


import json
import subprocess
import sys

REVIEWER = ASSETS / "review-notebook.py"


def _run_reviewer(tmp_path, code_src):
    nb = {"cells": [{"cell_type": "code", "execution_count": None,
                     "metadata": {}, "outputs": [], "source": code_src}],
          "metadata": {}, "nbformat": 4, "nbformat_minor": 5}
    p = tmp_path / "nb.ipynb"
    p.write_text(json.dumps(nb))
    return subprocess.run([sys.executable, str(REVIEWER), str(p)],
                          capture_output=True, text=True)


def test_reviewer_warns_on_unguarded_heavy_import(tmp_path):
    r = _run_reviewer(tmp_path, "import plotly\nprint('hi')\n")
    assert "plotly" in r.stdout
    assert "WARN" in r.stdout            # a warning, not a hard error
    assert r.returncode == 0            # WARN must not fail the build


def test_reviewer_silent_when_heavy_import_is_guarded(tmp_path):
    guarded = "try:\n    import plotly\nexcept Exception:\n    plotly = None\nprint('ok')\n"
    r = _run_reviewer(tmp_path, guarded)
    assert "plotly" not in r.stdout
    assert r.returncode == 0


def test_demo_chapter_builds_and_passes_reviewer(tmp_path):
    """End-to-end: figures + notebook build, then review-notebook.py reports 0 errors,
    using only matplotlib (all rich imports are guarded)."""
    import os
    fixtures = Path(__file__).resolve().parent / "fixtures"
    env = {**os.environ, "BUILD_COURSE_OUTPUT_DIR": str(tmp_path / "course")}

    figs = subprocess.run([sys.executable, str(fixtures / "build_viz_demo_figures.py")],
                          capture_output=True, text=True, env=env, cwd=tmp_path)
    assert figs.returncode == 0, figs.stderr

    build = subprocess.run([sys.executable, str(fixtures / "build_viz_demo.py")],
                           capture_output=True, text=True, env=env, cwd=tmp_path)
    assert build.returncode == 0, build.stderr

    nb = next(tmp_path.rglob("Chapter_*_*.ipynb"))
    rev = subprocess.run([sys.executable, str(REVIEWER), str(nb)],
                         capture_output=True, text=True, env=env, cwd=tmp_path)
    assert "0 error(s)" in rev.stdout, rev.stdout
    assert rev.returncode == 0, rev.stdout
