# Interactive & Animated Visualization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fourth, ML-focused visualization tier (animation, loss landscapes, architecture graphs, interactive explainers) to the `build-course` skill, with a graceful-degradation contract so the core stays dependency-light and the reviewer stays green on a bare machine.

**Architecture:** Two reusable matplotlib helpers (`animate_to_gif`, `loss_surface`) and one markdown helper (`interactive_callout`) are added to the build-course templates; every rich viz is authored try-rich/except-static so a missing heavy dep degrades to a static PNG/text. A new reference doc (`interactive-visualization.md`) holds the tool catalog, a when-to-use matrix, and copy-paste cell recipes. The reviewer gains a heuristic that flags an unguarded heavy import. `notebook-blueprint.md`, `runner-profiles.md`, `SKILL.md`, and `docs/build-course.md` get extended (not replaced).

**Tech Stack:** Python 3.11+, matplotlib (required floor), pytest for the helper/reviewer tests; manim / plotly / netron / torchinfo are optional and always guarded.

**Spec:** `docs/superpowers/specs/2026-06-25-interactive-visualization-design.md`

**Deviation from spec (intentional):** the spec listed a "matplotlib layer-stack PNG" as netron's last-resort fallback. The repo's own `figures-template.py` forbids hand-placing boxes/arrows in matplotlib for architecture diagrams. So the netron degradation chain is **`netron.start` (launch) → `torchinfo` text summary → a Mermaid `graph LR` diagram**, never a matplotlib box drawing. No `nn_architecture` matplotlib helper is added.

---

## File Structure

- `skills/build-course/assets/figures-template.py` — add `animate_to_gif`, `loss_surface`; make `_save` return the written `Path`. (matplotlib data/animation only)
- `skills/build-course/assets/build-script-template.py` — add `interactive_callout`; guard the notebook-write block under `__main__` so the helpers are importable/testable.
- `skills/build-course/assets/review-notebook.py` — add an unguarded-heavy-import heuristic (WARN).
- `skills/build-course/references/interactive-visualization.md` — **new**: tool catalog + when-to-use matrix + cell recipes.
- `skills/build-course/references/runner-profiles.md` — add the `animation / interactive-viz` profile + a "Choosing" table row.
- `skills/build-course/references/notebook-blueprint.md` — add a motion/interactivity row to the Visualization-decision matrix + one line in the per-concept arc.
- `skills/build-course/SKILL.md` — one-line pointers (steps 4–5) + `compatibility:` note.
- `docs/build-course.md` — "optional visualization extras" note.
- `tests/test_interactive_viz.py` — **new**: tests for the three helpers + the reviewer heuristic.
- `tests/fixtures/build_viz_demo.py`, `tests/fixtures/build_viz_demo_figures.py` — **new**: integration sample exercising every new pattern.

---

## Task 1: Make build-script-template importable + add `interactive_callout`

**Files:**
- Modify: `skills/build-course/assets/build-script-template.py`
- Test: `tests/test_interactive_viz.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_interactive_viz.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_interactive_viz.py::test_interactive_callout_emits_cited_markdown -v`
Expected: FAIL — either `module ... has no attribute 'interactive_callout'`, or an `.ipynb` is written into `tmp_path` (because the write block is not yet guarded).

- [ ] **Step 3: Guard the write block under `__main__`**

In `build-script-template.py`, replace the trailing block (currently lines ~124–141, from `notebook = {` through the final `print(...)`) so the file-writing side effects only run when executed directly:

```python
def build() -> Path:
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py", "mimetype": "text/x-python", "name": "python",
                "nbconvert_exporter": "python", "pygments_lexer": "ipython3", "version": "3.11",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / f"{CHAPTER}_build").mkdir(parents=True, exist_ok=True)
    NB_PATH.write_text(json.dumps(notebook, indent=1))
    print(f"wrote {NB_PATH} ({len(cells)} cells)")
    return NB_PATH


if __name__ == "__main__":
    build()
```

- [ ] **Step 4: Add the `interactive_callout` helper**

Insert directly after the `solution(...)` function (after line ~53), so it sits with the other cell helpers:

```python
def interactive_callout(name: str, url: str, why: str, *, tier: str = "link-out") -> dict:
    """Emit a markdown callout pointing at a hosted interactive tool.

    For `launch`/`link-out` tier tools (Transformer Explainer, LIT, CNN
    Explainer, GAN Lab, ...) that cannot embed in a notebook. Renders as a
    blockquote that stands out in VS Code, JupyterLab, GitHub, and nbviewer.
    See references/interactive-visualization.md for the catalog and tiers.

    Args:
        name: Tool name shown in bold.
        url: Live tool URL (cited as an autolink).
        why: One line on what the learner should look for there.
        tier: Integration tier label — "link-out" or "launch".
    """
    return {"cell_type": "markdown", "metadata": {}, "source": (
        f"> 🔬 **Interactive — {name}** · _{tier}_\n>\n"
        f"> {why}\n>\n"
        f"> ▶ Open: <{url}>"
    )}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_interactive_viz.py::test_interactive_callout_emits_cited_markdown -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add skills/build-course/assets/build-script-template.py tests/test_interactive_viz.py
git commit -m "feat(build-course): add interactive_callout helper; make template import-safe"
```

---

## Task 2: Add `animate_to_gif` + `loss_surface` to figures-template

**Files:**
- Modify: `skills/build-course/assets/figures-template.py`
- Test: `tests/test_interactive_viz.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_interactive_viz.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_interactive_viz.py -k "animate_to_gif or loss_surface" -v`
Expected: FAIL with `AttributeError: module ... has no attribute 'animate_to_gif'` / `loss_surface`.

- [ ] **Step 3: Make `_save` return the path**

In `figures-template.py`, change `_save` (lines ~42–47) to accept an extension and return the written `Path`:

```python
def _save(fig, name: str, ext: str = "png") -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f"fig_{CHAPTER}_{name}.{ext}"
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {path}")
    return path
```

- [ ] **Step 4: Add the two helpers**

Insert after `_save` (before `fig_distribution`):

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_interactive_viz.py -k "animate_to_gif or loss_surface" -v`
Expected: PASS (both). The PNG fallbacks always exist even without Pillow/plotly.

- [ ] **Step 6: Commit**

```bash
git add skills/build-course/assets/figures-template.py tests/test_interactive_viz.py
git commit -m "feat(build-course): add animate_to_gif and loss_surface figure helpers with static fallbacks"
```

---

## Task 3: Reviewer flags unguarded heavy imports

**Files:**
- Modify: `skills/build-course/assets/review-notebook.py`
- Test: `tests/test_interactive_viz.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_interactive_viz.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_interactive_viz.py -k reviewer -v`
Expected: FAIL — `test_reviewer_warns_on_unguarded_heavy_import` fails because no warning mentions `plotly` yet.

- [ ] **Step 3: Add the heuristic**

In `review-notebook.py`, inside `review(...)`, after the specialized-subject-language heuristic block (after line ~95, before the `# --- 2 + 3.` execution section), insert:

```python
    # --- unguarded heavy-viz import heuristic ---
    # Rich visualizations (manim/plotly/netron/torchview/torchinfo) are optional.
    # They MUST be wrapped so a missing dep degrades to a static fallback; an
    # unguarded import would crash the cell on a bare machine. Flag it (WARN).
    heavy_viz_deps = ("manim", "plotly", "netron", "torchview", "torchinfo")
    for i, c in enumerate(cells):
        if c["cell_type"] != "code":
            continue
        src = _src(c)
        if "try" in src:
            continue
        for dep in heavy_viz_deps:
            if re.search(rf"^\s*(?:import {dep}\b|from {dep}\b)", src, re.MULTILINE):
                warns.append(f"cell[{i}] imports optional '{dep}' without a try/except "
                             "fallback — wrap rich viz so it degrades to a static PNG/text "
                             "on a bare machine (see references/interactive-visualization.md)")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_interactive_viz.py -k reviewer -v`
Expected: PASS (both).

- [ ] **Step 5: Commit**

```bash
git add skills/build-course/assets/review-notebook.py tests/test_interactive_viz.py
git commit -m "feat(build-course): reviewer warns on unguarded optional viz imports"
```

---

## Task 4: New reference doc — interactive-visualization.md

**Files:**
- Create: `skills/build-course/references/interactive-visualization.md`

- [ ] **Step 1: Write the catalog + matrix + recipes**

Create `skills/build-course/references/interactive-visualization.md` with these sections (full content, not a stub):

1. **Header / principle** — restate the graceful-degradation contract: every rich viz cell is try-rich/except-static; web-only tools are honest link-outs, never faked as local.

2. **Tiers** — define `embed` / `launch` / `link-out` exactly as in the spec.

3. **When to use (decision matrix)** — a table mapping concept → recommended viz → fallback:

   | Concept being taught | Reach for | Fallback |
   |---|---|---|
   | A math transform / iterative algorithm / gradient path (motion teaches) | `animate_to_gif(frame_fn, ...)` (manim optional for polish) | static filmstrip PNG |
   | Optimization geometry / sharp-vs-flat minima | `loss_surface(loss_fn, ...)` (plotly interactive) | static 3D PNG |
   | Network architecture / layer shapes | `netron.start(model_file)` | `torchinfo.summary(model)` text → Mermaid `graph LR` |
   | Attention / transformer internals | `interactive_callout("Transformer Explainer", ...)` + toy attention heatmap | matplotlib heatmap |
   | Model interpretability / saliency / embeddings | `interactive_callout("LIT" / "What-If Tool", ...)` | matplotlib saliency / embedding scatter |
   | CNN feature maps, GANs, playground intuition | matching `interactive_callout(...)` from the catalog | local matplotlib reproduction |

4. **When NOT to animate** — a short list: don't animate static facts, tables, or anything a labelled still frame shows as well; motion must encode a variable changing (time/step/parameter); never add a GIF for decoration; keep frames ≤ ~30 and seeds fixed.

5. **Cell recipes** — copy-paste blocks, each already degradation-safe:
   - **Animation** (uses `animate_to_gif`; reference the resulting `figures/fig_<ch>_<name>.gif` from markdown).
   - **Loss landscape** (uses `loss_surface`; note the interactive `.html` is a bonus, the `.png` is what the notebook embeds).
   - **Architecture (netron)** — the launch → torchinfo → Mermaid chain:
     ```python
     try:
         import netron, torch  # optional
         torch.save(model, "model.pt"); netron.start("model.pt")  # opens a browser
     except Exception as e:
         print(f"NOTE netron/torch unavailable ({type(e).__name__}); text summary below")
         try:
             from torchinfo import summary
             summary(model, input_size=(1, 3, 32, 32))
         except Exception:
             print("Install torchinfo for a text summary; architecture diagram in the next cell.")
     ```
     followed by a markdown cell with a hand-authored Mermaid `graph LR` of the layers.
   - **Link-out tool** (uses `interactive_callout`).

6. **Tool catalog** — a table of every tool, each row: name · what it teaches · tier · topic tags · URL. Include the five named tools and the full Machine-Learning-Tokyo/Interactive_Tools list. Source of the catalog: https://github.com/Machine-Learning-Tokyo/Interactive_Tools

   Rows (tier, topic tags):
   - Transformer Explainer — next-token GPT-2 internals — `link-out` — `transformers` — https://poloclub.github.io/transformer-explainer/
   - exBERT — BERT attention/representations — `link-out` — `transformers,interpretability` — https://huggingface.co/exbert/
   - BertViz — attention across BERT/GPT-2/etc — `embed` — `transformers,interpretability` — https://github.com/jessevig/bertviz
   - CNN Explainer — convnet layer-by-layer — `link-out` — `cnn` — https://poloclub.github.io/cnn-explainer/
   - GAN Lab — GAN training dynamics — `link-out` — `gan` — https://poloclub.github.io/ganlab/
   - ConvNet Playground — CNN semantic image search — `link-out` — `cnn` — https://convnetplayground.fastforwardlabs.com
   - Activation Atlases — learned feature atlases — `link-out` — `cnn,interpretability` — https://distill.pub/2019/activation-atlas/
   - Visual Intro to ML — decision-tree/statistical learning intuition — `link-out` — `ml-basics` — http://www.r2d3.us/visual-intro-to-machine-learning-part-1/
   - TensorFlow Playground — NN hyperparameter intuition — `link-out` — `ml-basics,nn` — https://playground.tensorflow.org/
   - Neural Network Initialization — init effects — `link-out` — `nn,training` — https://www.deeplearning.ai/ai-notes/initialization/
   - Embedding Projector — PCA/t-SNE/UMAP embeddings — `link-out` — `embeddings` — https://projector.tensorflow.org/
   - OpenAI Microscope — neuron/layer vision-model viz — `link-out` — `cnn,interpretability` — https://microscope.openai.com/
   - Atlas (Nomic) — large dataset exploration — `link-out` — `data` — https://atlas.nomic.ai/discover
   - Language Interpretability Tool (LIT) — NLP model behavior — `launch`/`link-out` — `interpretability,nlp` — https://pair-code.github.io/lit/
   - What-If Tool — probe trained models — `launch`/`link-out` — `interpretability,fairness` — https://pair-code.github.io/what-if-tool/
   - Measuring Diversity — bias in search/recsys — `link-out` — `fairness` — https://pair.withgoogle.com/explorables/measuring-diversity/
   - Sage Interactions — algebra/calculus/crypto demos — `link-out` — `math` — https://wiki.sagemath.org/interact/
   - Probability Distributions — distribution tour — `link-out` — `probability,math` — https://www.simonwardjones.co.uk/posts/probability_distributions/
   - Bayesian Inference — coin-flip Bayes — `link-out` — `probability,math` — https://www.simonwardjones.co.uk/posts/bayesian_inference/
   - Seeing Theory — visual probability & stats — `link-out` — `probability,math` — https://seeing-theory.brown.edu/
   - Gaussian Process Visualization — GP & kernels — `link-out` — `probability,math` — http://www.infinitecuriosity.org/vizgp/
   - manim — programmatic math animation — `embed` — `math,animation` — https://github.com/3b1b/manim
   - netron — model architecture graphs — `launch` — `architecture` — https://github.com/lutzroeder/netron
   - loss-landscape — NN loss surface viz — `embed` (reproduce) — `training,optimization` — https://github.com/tomgoldstein/loss-landscape

- [ ] **Step 2: Verify the doc has no unclosed fences and the recipes parse**

Run:
```bash
python - <<'PY'
import pathlib, re
t = pathlib.Path("skills/build-course/references/interactive-visualization.md").read_text()
assert t.count("```") % 2 == 0, "unbalanced code fences"
# every python recipe block must compile
for block in re.findall(r"```python\n(.*?)```", t, re.DOTALL):
    compile(block, "recipe", "exec")
print("doc OK:", len(t), "chars")
PY
```
Expected: `doc OK: <n> chars` (non-zero), no assertion/compile error.

- [ ] **Step 3: Commit**

```bash
git add skills/build-course/references/interactive-visualization.md
git commit -m "docs(build-course): add interactive-visualization reference (catalog, matrix, recipes)"
```

---

## Task 5: Add the runner profile

**Files:**
- Modify: `skills/build-course/references/runner-profiles.md`

- [ ] **Step 1: Add the profile section**

In `runner-profiles.md`, after the "Specialized / domain language" section (before "Beyond-the-laptop infra"), add:

```markdown
### Animation / interactive-viz (motion & interactivity for ML/DL)
When a concept is better felt through MOTION or interactivity — a math transform,
a gradient-descent path, optimization geometry, a network's architecture, attention
internals — use the interactive-visualization tier. **Contract: try-rich / except-static.**
Each cell attempts the rich path (manim, plotly, netron, real model introspection)
and, on any missing dependency, degrades to a static matplotlib PNG / text summary and
prints a one-line `NOTE`. This keeps the core dependency floor at matplotlib and keeps
`review-notebook.py` green on a bare machine.

- Animation -> `animate_to_gif(frame_fn, ...)` (filmstrip PNG fallback).
- Loss landscape -> `loss_surface(loss_fn, ...)` (static 3D PNG fallback).
- Architecture -> `netron.start(model_file)` -> `torchinfo` text -> Mermaid `graph LR`.
- Web-only tools (Transformer Explainer, LIT, CNN Explainer, ...) -> `interactive_callout(...)`.

Recipes, the decision matrix, and the full tool catalog: see
references/interactive-visualization.md. Use it ONLY when motion/interactivity teaches;
otherwise a still matplotlib plot or a Mermaid diagram is the right call.
```

- [ ] **Step 2: Add a "Choosing" table row**

In the "Choosing" table at the bottom, add a row before the final note paragraph:

```markdown
| Concept needs motion / interactivity (animation, loss landscape, architecture, attention) | Animation / interactive-viz (often mixed with Python) |
```

- [ ] **Step 3: Commit**

```bash
git add skills/build-course/references/runner-profiles.md
git commit -m "docs(build-course): add animation/interactive-viz runner profile"
```

---

## Task 6: Extend the visualization-decision matrix

**Files:**
- Modify: `skills/build-course/references/notebook-blueprint.md`

- [ ] **Step 1: Add a matrix row**

In the "Visualization decision" table, add a row after the matplotlib data-plot row:

```markdown
| **Motion or interactivity teaches it** — a transform, gradient path, loss surface, architecture, attention | **Interactive-viz tier** (`animate_to_gif` / `loss_surface` / `netron` / `interactive_callout`) — see references/interactive-visualization.md |
```

- [ ] **Step 2: Extend the per-concept arc "Visual" step**

In "The per-concept arc", step 3 (**Visual**), append one sentence:

```markdown
…or, when **motion or interactivity** teaches better than a still frame (a transform, a gradient-descent path, a loss surface, an architecture, attention), use the **interactive-viz tier** (references/interactive-visualization.md) — always with its static fallback.
```

- [ ] **Step 3: Commit**

```bash
git add skills/build-course/references/notebook-blueprint.md
git commit -m "docs(build-course): add interactive-viz tier to the visualization decision matrix"
```

---

## Task 7: SKILL.md pointers + docs note

**Files:**
- Modify: `skills/build-course/SKILL.md`
- Modify: `docs/build-course.md`

- [ ] **Step 1: Point step 4 (Research & ground) at the new tier**

In `SKILL.md`, in the step "### 4. Research & ground each chapter", append after the Mermaid sentence:

```markdown
When a concept is better felt through **motion or interactivity** (a math transform, a gradient path, a loss surface, a network's architecture, attention), plan an **interactive-viz** instead of a still image — see references/interactive-visualization.md (catalog, decision matrix, degradation-safe recipes). Use it only when motion teaches.
```

- [ ] **Step 2: Point step 5 (Generate) at the helpers**

In "### 5. Generate each chapter", append a bullet:

```markdown
- For interactive/animated concepts, use the **animation / interactive-viz** runner profile and the figure helpers `animate_to_gif` / `loss_surface` (figures script) and `interactive_callout` (build script). Every rich cell must be try-rich/except-static so it degrades to a PNG/text on a bare machine — the reviewer warns on an unguarded `manim`/`plotly`/`netron`/`torchview`/`torchinfo` import.
```

- [ ] **Step 3: Update the `compatibility:` front-matter line**

In `SKILL.md` front matter, change the `compatibility:` value to add the optional extras:

```yaml
compatibility: Requires Python 3.11+ and matplotlib; CUDA chapters also need the NVIDIA CUDA toolkit (nvcc). Interactive-viz is optional and degrades gracefully — manim (math animation, needs ffmpeg/LaTeX), plotly (interactive loss surfaces), netron + torchinfo (architecture), all optional. Notebook verification uses subprocess, not Jupyter/nbconvert.
```

- [ ] **Step 4: Add Common-Mistakes rows**

In the "Common Mistakes" table, add:

```markdown
| Unguarded `import manim/plotly/netron` (crashes on a bare machine) | Wrap rich viz try-rich/except-static; degrade to a PNG/text. The reviewer warns on unguarded imports. |
| Animating a static fact for decoration | Animate only when a variable changes over time/step/parameter; otherwise a still plot or Mermaid. |
```

- [ ] **Step 5: Add the optional-extras note to docs/build-course.md**

In `docs/build-course.md`, add a short subsection (place it near the visualization/figures discussion; if none, append before the end):

```markdown
### Optional visualization extras

The interactive-viz tier (animation, loss landscapes, architecture graphs, interactive
explainers) is **entirely optional**. With only `matplotlib` installed, every such cell
degrades to a static PNG or text summary, and `review-notebook.py` still passes. Install
extras only for the richer output:

- `manim` (+ ffmpeg, LaTeX) — polished math animation (the `matplotlib.animation`
  filmstrip is the fallback).
- `plotly` — interactive 3D loss surfaces (static 3D PNG is the fallback).
- `netron` + `torch` + `torchinfo` — interactive/textual architecture views (a Mermaid
  diagram is the fallback).

See `skills/build-course/references/interactive-visualization.md` for the full tool
catalog, the when-to-use matrix, and copy-paste recipes.
```

- [ ] **Step 6: Commit**

```bash
git add skills/build-course/SKILL.md docs/build-course.md
git commit -m "docs(build-course): wire interactive-viz tier into SKILL.md and docs"
```

---

## Task 8: Integration — a sample chapter exercising every new pattern

**Files:**
- Create: `tests/fixtures/build_viz_demo_figures.py`
- Create: `tests/fixtures/build_viz_demo.py`
- Test: `tests/test_interactive_viz.py`

- [ ] **Step 1: Write the failing integration test**

Append to `tests/test_interactive_viz.py`:

```python
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

    nb = next(tmp_path.glob("Chapter_*_*.ipynb"))
    rev = subprocess.run([sys.executable, str(REVIEWER), str(nb)],
                         capture_output=True, text=True, env=env, cwd=tmp_path)
    assert "0 error(s)" in rev.stdout, rev.stdout
    assert rev.returncode == 0, rev.stdout
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pytest tests/test_interactive_viz.py -k demo_chapter -v`
Expected: FAIL — the two fixture scripts do not exist yet.

- [ ] **Step 3: Create the figures fixture**

Create `tests/fixtures/build_viz_demo_figures.py` — it imports the SHIPPED figure helpers and calls the two new ones. The figures fixture also records which extension `animate_to_gif` actually produced (gif vs png) into `course/figures/descent.ext`, so the notebook fixture references the real artifact in both environments:

```python
import importlib.util
import os
from pathlib import Path

CHAPTER = "99"
OUTPUT_DIR = Path(os.environ.get("BUILD_COURSE_OUTPUT_DIR", "course"))
FIG_DIR = OUTPUT_DIR / "figures"

_asset = Path(__file__).resolve().parents[2] / "skills/build-course/assets/figures-template.py"
_spec = importlib.util.spec_from_file_location("figtpl", _asset)
_figtpl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_figtpl)
_figtpl.CHAPTER = CHAPTER
_figtpl.OUTPUT_DIR = OUTPUT_DIR
_figtpl.FIG_DIR = FIG_DIR


def main():
    gif = _figtpl.animate_to_gif(
        lambda ax, i: (ax.plot([0, 1], [0, i / 4.0]), ax.set_ylim(0, 3)),
        n_frames=6, name="descent")
    _figtpl.loss_surface(lambda a, b: a ** 2 + 0.5 * b ** 2, name="bowl", n=20)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    (FIG_DIR / "descent.ext").write_text(gif.suffix)  # ".gif" or ".png"
    print(f"descent artifact: {gif.name}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create the notebook fixture**

Create `tests/fixtures/build_viz_demo.py` — it imports the SHIPPED `md`/`code`/`interactive_callout`, reads the recorded extension so the image reference always resolves, and includes a guarded loss-landscape-style cell:

```python
import importlib.util
import json
import os
from pathlib import Path

CHAPTER = "99"; SLUG = "Viz_Demo"
OUTPUT_DIR = Path(os.environ.get("BUILD_COURSE_OUTPUT_DIR", "course"))
NB_PATH = Path.cwd() / f"Chapter_{CHAPTER}_{SLUG}.ipynb"

_asset = Path(__file__).resolve().parents[2] / "skills/build-course/assets/build-script-template.py"
_spec = importlib.util.spec_from_file_location("buildtpl", _asset)
_b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b)
md, code, interactive_callout = _b.md, _b.code, _b.interactive_callout

ext = (OUTPUT_DIR / "figures" / "descent.ext").read_text().strip()  # ".gif" or ".png"

cells = [
    md("# Chapter 99 — Viz Demo\n\n> Audience: **graduate**"),
    md(f"## 1. Gradient descent (animation)\n\n![descent](figures/fig_99_descent{ext})"),
    md("## 2. Loss landscape\n\n![bowl](figures/fig_99_bowl.png)"),
    code(
        "import numpy as np\n"
        "try:\n"
        "    import plotly  # optional interactive path\n"
        "    have = True\n"
        "except Exception:\n"
        "    have = False\n"
        "z = float((np.array([0.3, -0.2]) ** 2).sum())\n"
        "assert z >= 0\n"
        "print('PASS', 'plotly' if have else 'static-fallback')\n"
    ),
    interactive_callout("Transformer Explainer",
                        "https://poloclub.github.io/transformer-explainer/",
                        "Watch GPT-2 attention as it predicts the next token."),
]

notebook = {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4, "nbformat_minor": 5}
NB_PATH.write_text(json.dumps(notebook, indent=1))
print(f"wrote {NB_PATH} ({len(cells)} cells)")
```

- [ ] **Step 5: Run the integration test to verify it passes**

Run: `pytest tests/test_interactive_viz.py -k demo_chapter -v`
Expected: PASS — the reviewer prints `0 error(s)`. The image reference resolves because the notebook fixture reads the actual produced extension; the guarded `plotly` import keeps the cell green whether or not plotly is installed.

- [ ] **Step 6: Run the full suite**

Run: `pytest tests/test_interactive_viz.py -v`
Expected: all tests PASS.

- [ ] **Step 7: Commit**

```bash
git add tests/fixtures/build_viz_demo.py tests/fixtures/build_viz_demo_figures.py tests/test_interactive_viz.py
git commit -m "test(build-course): end-to-end interactive-viz demo chapter passes the reviewer"
```

---

## Self-Review notes

- **Spec coverage:** five named tools (Tasks 1/2/4), Interactive_Tools catalog (Task 4), graceful degradation (Tasks 1–3), new reference doc + runner profile + blueprint + helpers (Tasks 4–7), reviewer guarantee (Task 3), docs/compatibility (Task 7), end-to-end success criteria (Task 8). Covered.
- **Intentional spec refinement:** netron's last-resort fallback is Mermaid/torchinfo text, not a matplotlib box drawing, to honor `figures-template.py`'s anti-hand-placed-box rule. Documented at the top of this plan and in Task 4.
- **Type/name consistency:** helper names are stable across tasks — `interactive_callout`, `animate_to_gif`, `loss_surface`, `_filmstrip`, `_save(fig, name, ext=...)`, reviewer list `heavy_viz_deps`. The fixtures import the shipped helpers rather than re-defining them (DRY).
