# build-course — turn a repo, book, or blog into a hands-on notebook course

`build-course` is the **authoring** skill. It reads source material you already have and generates self-paced, chapter-by-chapter Jupyter notebooks: each chapter puts the concept, a diagram, runnable code, and graded exercises in one place. It is the first skill in the [build → teach → update](../README.md#the-loop) loop.

> Triggers: `/build-course`, "make a course from", "turn this repo/book into notebooks", "create a learning notebook for", "build a curriculum from".

## What it produces

- **One notebook per chapter** (`Chapter_NN_Title.ipynb`) following a concept arc: motivate → define → diagram → naive gap → runnable code → interpret.
- **3–5 inline exercises** per chapter, each with a **collapsible solution** (hidden by default).
- **~5 course-level assignments** released at 20% progress milestones (their own notebooks, cumulative).
- **One capstone final project** after the last chapter.
- A **`build_<ch>.py` script per chapter** — the source of truth that emits the `.ipynb`. You never hand-write notebook JSON.

## The workflow

1. **Ingest sources & confirm the primary one.** Repo (Glob/Grep/Read or GitHub MCP), PDF/book (read by page range), blogs (web fetch/search). You're asked which source is **primary** — it sets the chapter spine (repo modules vs. book table of contents).
2. **Confirm the learner persona** (required) — fresh student, graduate, PhD/researcher, entry-level practitioner, or senior engineer — plus the content language and the code language for hands-on cells. This drives vocabulary, math depth, figure density, and difficulty.
3. **Propose a chapter outline** for your buy-in (objectives + prerequisites, one screen).
4. **Research & ground each chapter** — verify claims, cite sources, plan one visual per major concept.
5. **Generate each chapter** by filling and running a build script; figures are drawn by a separate figures script.
6. **Emit assignments & the final project** at the right milestones.
7. **Review & verify** with the bundled reviewer before shipping.

## Runner profiles (how the code cells run)

The skill picks the executable-cell recipe that fits the domain so the learner *runs* something every chapter:

| Source domain | Profile |
|---------------|---------|
| ML / DS / general | Python |
| GPU / systems | CUDA / C / C++ |
| Databases / analytics | SQL (sqlite/DuckDB, in-memory) |
| CLI / pipelines / ops | Bash |
| **Conceptual / theory book with no code** | **Concept-simulation** — a small runnable model of the idea |
| Reference code in another language | Port-reference-implementation (reuse its tests) |
| Subject *is* a query/DSL (SQL, Cypher, SPARQL) | Keep verbatim and run for real |
| Needs a cluster / GPU / prod infra | Single-machine simulation + a "Going to production" cell |

Full detail: [`skills/build-course/references/runner-profiles.md`](../skills/build-course/references/runner-profiles.md).

## Design principles

- **The build script is the source of truth.** Regenerate, don't hand-edit.
- **Prefer a runnable simulation over a static diagram** whenever a concept can be made interactive — the differentiator for prose-only books.
- **Mermaid-first for diagrams** (renders in JupyterLab, VS Code, GitHub, nbviewer); matplotlib only for quantitative data plots.
- **Ground every claim** — web-search and cite, never assert from memory.
- **Verify before shipping** — the reviewer executes every code cell and checks each collapsible solution against its exercise's asserts.

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

## Requirements

Python 3.11+ and `matplotlib`. CUDA chapters also need the NVIDIA CUDA toolkit (`nvcc`). Notebook verification uses `subprocess`, not Jupyter/nbconvert.

## See also

- [teach-course](teach-course.md) — get taught the chapters you just built.
- [update-course](update-course.md) — revise a chapter that isn't landing.
- The full skill spec: [`skills/build-course/SKILL.md`](../skills/build-course/SKILL.md).
