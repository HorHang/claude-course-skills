# Notebook Review

After building a chapter, **review it before shipping**. Two layers:

1. **Mechanical (automated)** — run `assets/review-notebook.py` (copy it to `<course>/review-notebook.py`):
   ```
   python <course>/review-notebook.py <course>/Chapter_<ch>_<Title>.ipynb
   ```
   It fails (non-zero exit) on: missing image files, malformed/unclosed `<details>`, code cells that raise, and — critically — **solutions that fail their own asserts** (solutions live in markdown `<details>`, so a normal run never executes them; the reviewer splices each solution in place of its stub and runs the exercise's asserts). It WARNs on mermaid blocks (not all hosts render them) and over-long cells.

2. **Qualitative (you, against the rubric below)** — the things no script can judge.

Fix every ERROR and triage every WARN before moving on.

## Render correctness (the "rendered error" class)

| Check | Why |
|-------|-----|
| Every `![](path)` resolves | Broken image icon is the #1 visible render bug. |
| Mermaid renders in the **target host** | Plain Jupyter Notebook / nbviewer / some VS Code setups show mermaid as raw text or an error. If the host doesn't render it, replace with a static image or an ASCII diagram (see notebook-blueprint.md "Visualization decision"). |
| `$…$` / `$$…$$` balanced | An odd `$` count breaks all following math. |
| `<details>` opened and closed, fenced code inside | A malformed block dumps raw HTML/markdown. |
| No raw-string artifacts (`\n`, stray `rf"""`) leaking into rendered text | Authoring slip. |

## Code & solution correctness

- Every code cell runs top-to-bottom in one kernel (the reviewer uses a shared namespace — later cells may depend on earlier ones).
- Each exercise's **solution actually satisfies the exercise's asserts** (the reviewer checks this; do not skip it just because the solution "looks right").
- Demos are deterministic (seed RNG) so the printed result the learner predicts is stable.
- `assert … ; print("PASS")` is present so each runnable cell self-verifies.

## Fidelity to the source / book (no automation — you must check)

- Every quantitative claim, definition, and number traces to the source. **Quote or cite the book section / repo `path:line`.** Do not assert from memory.
- Terminology matches the book's (don't invent synonyms that confuse a reader cross-referencing the source).
- Where you simplified or idealized (e.g. "assumes independent failures"), **say so in the cell** — the Chapter_01 availability demo is a good model.
- Adopted prose that was translated still says what the original said — spot-check against the source language.

## Reading flow & the "aha" progression (no automation — you must check)

Read the notebook top to bottom as a learner. Each cell should earn the next.

- **One idea per cell** — long walls of text (the reviewer WARNs >1800 chars) bury the insight. Split along the concept arc: motivate → define → figure → the gap → runnable → interpret.
- **The gap before the payoff** — show the naive approach failing *before* the fix, so the runnable cell delivers an "aha", not just a fact.
- **Predict-then-run** — every runnable/exercise cell asks the learner to predict first; the printed result is the reward.
- **No forward references** — a concept never depends on something taught later. Difficulty rises monotonically.
- **Each concept builds on the last** — section N+1 uses N's result. If a section stands alone, reorder or bridge it.
- **Interpretation closes the loop** — after every runnable cell, one line on *what the learner just saw* and why it matters.

## Output of review

A short pass/fail note: reviewer exit status + the qualitative checklist result. If anything failed, **edit `build_<ch>.py` (never the .ipynb) and re-run**, then re-review.
