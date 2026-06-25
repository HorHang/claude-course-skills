import importlib.util
import json
import os
from pathlib import Path

CHAPTER = "99"; SLUG = "Viz_Demo"
OUTPUT_DIR = Path(os.environ.get("BUILD_COURSE_OUTPUT_DIR", "course"))
NB_PATH = OUTPUT_DIR / f"Chapter_{CHAPTER}_{SLUG}.ipynb"

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
NB_PATH.parent.mkdir(parents=True, exist_ok=True)
NB_PATH.write_text(json.dumps(notebook, indent=1))
print(f"wrote {NB_PATH} ({len(cells)} cells)")
