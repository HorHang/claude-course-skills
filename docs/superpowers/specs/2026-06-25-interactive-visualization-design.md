# Interactive & Animated Visualization for build-course — Design

**Date:** 2026-06-25
**Status:** Approved (design)
**Skill affected:** `build-course` (no change to `teach-course` / `update-course`)

## Problem

`build-course` generates Jupyter-notebook chapters whose visuals today come in three
tiers: matplotlib PNGs (quantitative data plots), Mermaid (diagrams), and
tables/ASCII. For ML/DL topics — math intuition, neural-network architecture, loss
landscapes, attention/transformer internals, model interpretability — a static image
under-teaches. Motion and interactivity carry the "aha" that a still frame cannot.

The goal: add a **fourth visualization tier** — interactive & animated viz — drawing
on established tools (3b1b/manim, lutzroeder/netron, tomgoldstein/loss-landscape,
poloclub/transformer-explainer, PAIR/LIT) and the curated
Machine-Learning-Tokyo/Interactive_Tools catalog — **without** making the core skill
heavy or fragile.

## Guiding principle: graceful degradation

The skill keeps its current dependency floor (matplotlib only). Every new rich viz is
authored as a **try-rich / except-static** cell:

1. Attempt the rich path (manim render, plotly 3D surface, real model introspection).
2. On any missing dependency (no `ffmpeg`/LaTeX/GPU/`manim`/`plotly`/`netron`), fall
   back to a **static matplotlib equivalent** and `print` a one-line NOTE.

Consequences:
- The bundled `review-notebook.py` still executes every cell clean on a bare machine.
- A chapter never hard-fails on a visualization.
- No heavy package becomes a required dependency.

Tools that cannot embed at all (standalone web apps) are never faked as "running
locally." They become **cited link-out callouts** plus a lightweight local
reproduction of the same idea.

## Tool tiers

Each tool is tagged with how it integrates:

- **`embed`** — runs in-notebook and renders inline (with a static fallback).
- **`launch`** — a cell starts a local server / opens a browser (e.g. `netron.start`),
  guarded by try/except; degrades to a static summary.
- **`link-out`** — a cited callout to a hosted interactive demo + a small local
  reproduction of the concept.

### The five named tools

| Tool / repo | Tier | In-notebook behavior | Fallback |
|---|---|---|---|
| **manim** (3b1b math animation) | embed | short MP4/GIF inline animating a math concept (transform, gradient step) | `matplotlib.animation` → GIF via Pillow; if no writer, a multi-panel "filmstrip" PNG |
| **loss-landscape** (Goldstein) | embed | small net + filter-normalized 2-direction slice → plotly interactive 3D surface | matplotlib `plot_surface` static PNG |
| **netron** (architecture) | launch | `netron.start(model_file)` opens the interactive graph in a browser | `torchview`/`torchinfo` text+box summary, else a matplotlib layer-stack PNG |
| **Transformer Explainer** (poloclub) | link-out | cited callout to the live GPT-2 demo | toy local attention-weights heatmap on a short sentence |
| **LIT** (PAIR) | launch / link-out | cited callout (+ optional `lit_nlp` server snippet behind a try) | local saliency / embedding scatter via matplotlib |

### Interactive_Tools catalog

The full Machine-Learning-Tokyo/Interactive_Tools list lands in the catalog as
topic-tagged callouts. Tier notes called out explicitly:

- **`embed`:** BertViz (renders in Jupyter).
- **`link-out`:** Transformer Explainer, exBERT, CNN Explainer, GAN Lab, ConvNet
  Playground, Activation Atlases, Visual Intro to ML, TensorFlow Playground, Neural
  Network Initialization, Embedding Projector, OpenAI Microscope, Atlas (Nomic), LIT,
  What-If Tool, Measuring Diversity, Sage Interactions, Probability Distributions,
  Bayesian Inference, Seeing Theory, Gaussian Process Visualization.

Catalog entry = name, one-line "what it teaches", URL, tier, and **topic tags** (e.g.
`transformers`, `cnn`, `embeddings`, `gan`, `probability`, `interpretability`) so a
chapter author drops in the callout matching the concept being taught.

## Components (surface area)

Four touch points in the `build-course` skill.

### 1. `references/interactive-visualization.md` (new) — the heart

- **Tool catalog:** every tool above with name / what-it-teaches / URL / tier / topic
  tags.
- **When-to-use decision matrix:** concept type → recommended viz → fallback, plus an
  explicit **"when NOT to animate"** section (motion must teach; no gratuitous GIFs).
- **Cell recipes:** copy-paste patterns for each embeddable tool with the
  try-rich/except-static fallback already wired, and the `interactive_callout(...)`
  pattern for link-out tools.

### 2. `references/runner-profiles.md` — one new profile

- Add an **`animation / interactive-viz`** profile documenting the
  try-rich/except-static contract and pointing to the new reference doc.
- Add a row to the "Choosing" table (concept needs motion/interactivity → this
  profile, often mixed with Python).

### 3. `references/notebook-blueprint.md` — extend, don't replace

- Add a **motion/interactivity row** to the "Visualization decision" matrix with a
  pointer to `interactive-visualization.md`.
- The per-concept arc's **"Visual"** step gains: "…or an animation / interactive viz
  where motion teaches better than a still frame."

### 4. Templates — reusable helpers

- `assets/figures-template.py`: add `animate_to_gif(...)` (matplotlib.animation +
  Pillow), `loss_surface(...)`, and `nn_architecture(...)`, each self-contained and
  degrading to a static PNG.
- `assets/build-script-template.py`: add `interactive_callout(name, url, why)` →
  emits a cited markdown callout cell for link-out tools.
- `SKILL.md`: one-line pointers in the research/generate steps (steps 4–5); **no
  workflow change**.

## Verification & guardrails

- **`review-notebook.py`:** no structural change. Add the new optional deps (`manim`,
  `plotly`, `netron`, `torchview`, `ffmpeg`) to the reviewer's known-optional list so a
  fallback prints a NOTE rather than a WARNING. Because every rich cell degrades to
  static, the reviewer still runs clean on a bare machine.
- **Docs:** `docs/build-course.md` and the SKILL `compatibility:` line get an
  "optional visualization extras (all optional)" note.
- **YAGNI:** no new skill; no heavy dep becomes required; web apps are honest
  link-outs, never faked locally; animation only where motion teaches.

## Out of scope

- Changes to `teach-course` or `update-course`.
- Bundling/vendoring any external tool's source.
- GPU-required code paths as anything other than an optional fast path with a CPU/
  static fallback.

## Success criteria

1. A chapter author can pick an interactive viz from the decision matrix and paste a
   recipe that runs rich locally and degrades to a static PNG on a bare machine.
2. `review-notebook.py` passes (0 errors) on a machine with **only** matplotlib
   installed, for a chapter using each new viz pattern.
3. The Interactive_Tools catalog is complete and topic-tagged, so the right callout is
   discoverable per concept.
4. No existing chapter-authoring workflow step is removed or reordered.
