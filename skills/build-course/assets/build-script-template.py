"""
Template build script for a single course chapter notebook.

Copy this to <course>/build_<ch>.py, fill in `cells`, then run:
    python <course>/build_<ch>.py

The build script is the SOURCE OF TRUTH for the chapter. Never hand-edit the
generated .ipynb; edit this script and re-run. Figures are generated separately
by build_<ch>_figures.py into <OUTPUT_DIR>/figures/.

Portability: output paths are derived from a configurable OUTPUT_DIR relative to
the current working directory (or the BUILD_COURSE_OUTPUT_DIR env var). No
machine-specific absolute paths, so this runs unmodified in any repo.
"""
import json
import os
from pathlib import Path

# --- Config (edit these) ---
CHAPTER = "03"                       # e.g. "03" or "14a"
TITLE = "Title With Spaces"          # human title
SLUG = "Title_With_Underscores"      # file-name slug

# Output dir: env override, else ./course under the current working directory.
OUTPUT_DIR = Path(os.environ.get("BUILD_COURSE_OUTPUT_DIR", "course"))
NB_PATH = Path.cwd() / f"Chapter_{CHAPTER}_{SLUG}.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text}


def code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text}


def solution(text: str, lang: str = "python") -> dict:
    """A solution that is genuinely COLLAPSED by default, via an HTML <details>
    block inside a markdown cell.

    This folds by default and gives a click-to-expand toggle in VS Code,
    JupyterLab, Jupyter Notebook, GitHub, and nbviewer. (cell metadata
    `jupyter.source_hidden` is NOT honored by VS Code, which is why the plain
    code-cell approach did not collapse — so we use <details> instead.)

    Trade-off: the solution is a markdown cell, so it is for reading/checking,
    not auto-run. Keep any runnable correctness check in the exercise's own
    (visible) code cell above.
    """
    body = text.rstrip("\n")
    return {"cell_type": "markdown", "metadata": {},
            "source": f"<details>\n<summary>▶ Show solution</summary>\n\n```{lang}\n{body}\n```\n\n</details>"}


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


cells = []

# --- 1. Front matter ---
cells.append(md(rf"""# Chapter {CHAPTER} — {TITLE}

> Course context: <one line>.
> Builds on: <prerequisite chapters/concepts>.
> Audience: **<persona>** · depth: <level>

<Why this matters — the stakes, in 2-3 sentences.>

### What you'll learn
- <objective 1>
- <objective 2>
- <objective 3>
"""))

# --- 2. Concept section (duplicate this block per concept; follow the arc:
#         motivate -> define/math -> figure -> gap -> runnable -> interpret) ---
cells.append(md(rf"""## 1. <Concept name>

<Motivate: the problem this solves. Bold the **key terms**.>

<Definition; formula if relevant.>

![<caption stating the insight>](figures/fig_{CHAPTER}_<name>.png)
"""))

cells.append(code(r"""# Runnable demo (pick the runner profile: Python / CUDA / SQL / Bash / sim).
# Self-contained; ends with a printed result + an assert check.
print("hello")
"""))

cells.append(md(r"""<Interpret the output the learner just saw.>"""))

# --- 3. Exercises (3-5; each: prompt + 'predict' + solution) ---
cells.append(md(r"""## Exercise 1 — <task>

<Clear instruction.> **Predict** the result before running, then check.
"""))
cells.append(solution(r"""# worked solution (collapsed by default; learner clicks to reveal)
print("PASS")
"""))

# NOTE: Assignments and the final project are COURSE-LEVEL, not per chapter.
# Do NOT add ~5 assignments or a capstone here. The skill emits ~5 assignment
# notebooks at 20% progress milestones, plus 1 final-project notebook after the
# course completes. See references/assignments-rubric.md.

# --- 4. Further reading ---
cells.append(md(r"""## Further reading

**Source of truth**
- <primary source / repo path / book section>

**Going deeper**
- <link — one-line why it matters>
"""))

# --- 7. Recap ---
cells.append(md(r"""## Recap
- <bullet 1>
- <bullet 2>

Next: <teaser for the next chapter>.
"""))


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
