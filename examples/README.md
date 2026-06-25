# Example generated chapters

These are **real, runnable course chapters** produced by [`build-course`](../docs/build-course.md) — kept in the repo so you can see the output before installing anything. Together they show the two source modes the skill supports.

| Chapter | Source mode | Source | Runner profile |
|---------|-------------|--------|----------------|
| [`Chapter_01_Quorum_Consistency.ipynb`](Chapter_01_Quorum_Consistency.ipynb) | **book → course** | *Designing Data-Intensive Applications*, ch. 5 (prose only) | concept-simulation |
| [`Chapter_02_BPE_Tokenizer.ipynb`](Chapter_02_BPE_Tokenizer.ipynb) | **repo → course** | [karpathy/minbpe](https://github.com/karpathy/minbpe) (real code) | Python |

Both pass the bundled reviewer with **0 errors, 0 warnings** — every code cell executes and every collapsible solution is checked against its exercise's asserts.

## Chapter 01 — Quorum Consistency (book → course)

Turns a prose-only idea (the `w + r > n` rule) into something you **run, break, and measure** for a graduate learner: a Mermaid diagram of the client/replica paths, a brute-force overlap check, a Monte-Carlo stale-read estimate that matches the closed form, a data plot, and 3 self-checking exercises. This is the high-value case — a conceptual book with no code becomes a **concept-simulation**.

## Chapter 02 — Byte Pair Encoding (repo → course)

Follows a real codebase, `minbpe`, function by function. It re-implements `get_stats`, `merge`, and the training loop, and includes **"translation bridge"** cells that map each concept back to where it lives in the source (`minbpe/base.py`, `minbpe/basic.py`). This is how a repo-primary course threads abstract concepts to concrete `path:function` anchors.

## Bonus — an animated explainer (PagedAttention)

The README hero is a Problem → Idea → Mechanism → Payoff walk-through of PagedAttention ([vLLM, arXiv:2309.06180](https://arxiv.org/abs/2309.06180)), built straight from the paper's running example (prompt `"Four score and seven years ago our"`, block size 4; block table `0→7, 1→1, 2→3`). It demonstrates build-course's **animation tier**, which has two paths:

- **Polish — [`build_pagedattention_manim.py`](build_pagedattention_manim.py)** renders [`figures/pagedattention.mp4`](figures/pagedattention.mp4) with [manim](https://github.com/3b1b/manim) (the 3Blue1Brown engine). manim + ffmpeg are heavy, but needed only to *regenerate* the video — the committed MP4 plays for every reader.
- **Fallback — [`build_pagedattention_animation.py`](build_pagedattention_animation.py)** renders the same four beats with pure matplotlib + Pillow (no manim/ffmpeg/GPU), so build-course still produces a usable animation on the repo's dependency floor.

```bash
# polish path (manim) — writes the MP4 embedded in the README
manim -qm --format=mp4 build_pagedattention_manim.py PagedAttention -o pagedattention
ffmpeg -i media/videos/build_pagedattention_manim/720p30/pagedattention.mp4 \
  -filter:v "setpts=0.66*PTS" -an -pix_fmt yuv420p -movflags +faststart figures/pagedattention.mp4

# fallback path (matplotlib) — writes a self-contained GIF
python build_pagedattention_animation.py              # figures/pagedattention.gif
BUILD_QA=1 python build_pagedattention_animation.py   # + per-scene QA PNGs
```

## Bonus — a 3D loss landscape (Muon optimizer)

The second README clip teaches **geometry a still frame can't**: it draws an ill-conditioned least-squares problem as a **3D loss valley** and walks two optimizers down it — **SGD-momentum** vs **[Muon](https://kellerjordan.github.io/posts/muon/)**, from the same start, for the same step budget. SGD oscillates up the steep wall and stalls; Muon orthogonalizes its step and flows along the valley floor to a ~1.7× lower loss. It's the *animated twin* of the chapter's static contour figure — same seed, same trajectories, now showing the **mechanism** the contour can only assert.

- **[`build_muon_loss_landscape_manim.py`](build_muon_loss_landscape_manim.py)** — a manim `ThreeDScene` (`LossLandscapeWalkScene`) that builds the loss `Surface` from the loss function, then steps both optimizers along their paths *on the surface*. Renders [`figures/muon_loss_landscape.mp4`](figures/muon_loss_landscape.mp4) (the same scene exports a notebook GIF twin at 480p).

```bash
# README clip (720p MP4)
manim -qm --format=mp4 build_muon_loss_landscape_manim.py LossLandscapeWalkScene -o muon_loss_landscape
# notebook GIF twin (480p)
manim -ql --format=gif build_muon_loss_landscape_manim.py LossLandscapeWalkScene -o anim_18a_loss_walk
```

## Files

For each chapter `NN`:

| File | Role |
|------|------|
| `Chapter_NN_*.ipynb` | The generated notebook — **open this** (GitHub renders it inline) |
| `build_NN_*.py` | The build script — the **source of truth** that emits the notebook |
| `build_NN_*_figures.py` | Generates that chapter's data plot |
| `figures/fig_NN_*.png` | The quantitative figure |
| `review-notebook.py` | The bundled reviewer (shared, copied from the skill) |

## Reproduce them

```bash
# Chapter 01
python build_01_quorum_consistency_figures.py
python build_01_quorum_consistency.py
python review-notebook.py Chapter_01_Quorum_Consistency.ipynb   # 0 errors, 0 warnings

# Chapter 02
python build_02_bpe_tokenizer_figures.py
python build_02_bpe_tokenizer.py
python review-notebook.py Chapter_02_BPE_Tokenizer.ipynb        # 0 errors, 0 warnings
```

The reviewer executes every code cell *and* extracts each collapsible solution to check it against its exercise's asserts — so a chapter can't ship with a broken cell or a wrong solution.
