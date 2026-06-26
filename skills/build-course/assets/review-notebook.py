"""
Automated reviewer for a generated chapter notebook.

Run after building a chapter, BEFORE shipping it:
    python <course>/review-notebook.py <course>/Chapter_<ch>_<Title>.ipynb

It catches the mechanical failures that otherwise ship silently:
  1. Render-breakers — missing image files, unbalanced LaTeX `$`, malformed
     `<details>` blocks, and mermaid blocks (which several hosts do not render).
  2. Code correctness — every code cell executes in order in a shared namespace.
  3. SOLUTION correctness — solutions now live in markdown `<details>` blocks, so
     the normal run never executes them. This extracts each solution, splices it
     in place of its exercise stub, and runs the exercise's own asserts against it.

Exit code is non-zero if any ERROR is found, so it can gate a build.
Qualitative checks (fidelity to the source, reading-flow / "aha" progression)
are NOT automatable — see references/notebook-review.md for that checklist.
"""
import json
import os
import re
import sys
from pathlib import Path


def _src(cell: dict) -> str:
    s = cell["source"]
    return "".join(s) if isinstance(s, list) else s


def _python_source(src: str) -> str | None:
    """Return the runnable-Python view of a code cell, or None if the cell is
    Jupyter-only (not valid plain Python).

    A code cell may legitimately be CUDA/C++ (`%%writefile x.cu`), shell
    (`!nvcc ...`, `%%bash`), or carry line magics (`%matplotlib inline`).
    Running those through `exec` raises a false-positive SyntaxError, so the
    reviewer must NOT treat them as Python. A whole-cell magic (`%%...`) means
    the cell is not Python at all; otherwise drop the shell/magic lines and run
    whatever real Python remains so genuine errors are still caught."""
    lines = src.splitlines()
    first = next((ln for ln in lines if ln.strip()), "")
    if first.lstrip().startswith("%%"):
        return None
    kept = [ln for ln in lines if not ln.lstrip().startswith(("!", "%"))]
    body = "\n".join(kept)
    return body if body.strip() else None


def _strip_stub(src: str) -> str:
    """Drop a `def ...(): ... raise NotImplementedError` stub, keep the rest
    (the asserts), so a substituted solution can be checked against them."""
    lines = src.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if re.match(r"\s*def \w+\(", lines[i]):
            j = i
            while j < len(lines) and "NotImplementedError" not in lines[j]:
                j += 1
            i = j + 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def _solution_after(cells: list[dict], start: int) -> str | None:
    """Return the python inside the next `<details>` markdown cell after `start`."""
    for c in cells[start + 1:]:
        if c["cell_type"] != "markdown":
            continue
        src = _src(c)
        if "<details" not in src:
            continue
        m = re.search(r"```(?:python|py)?\n(.*?)```", src, re.DOTALL)
        return m.group(1) if m else None
    return None


def review(path: str) -> int:
    nb = json.load(open(path))
    cells = nb["cells"]
    base = Path(path).parent
    errors: list[str] = []
    warns: list[str] = []

    # --- 1. static render checks ---
    for i, c in enumerate(cells):
        src = _src(c)
        if c["cell_type"] != "markdown":
            continue
        for ref in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", src):
            if ref.startswith("http"):
                continue
            if not (base / ref).exists():
                errors.append(f"cell[{i}] image not found: {ref}")
        if src.count("$") % 2 != 0:
            warns.append(f"cell[{i}] odd number of '$' — LaTeX may be unbalanced")
        if "<details" in src and "</details>" not in src:
            errors.append(f"cell[{i}] <details> not closed")
        if src.count("```") % 2 != 0:
            errors.append(f"cell[{i}] unclosed ``` fence (code or mermaid diagram won't render)")
        if len(src) > 1800:
            warns.append(f"cell[{i}] long markdown cell ({len(src)} chars) — split per the concept arc")

    # --- specialized subject-language heuristic ---
    # If the chapter is about a query/DSL language, that language should appear
    # verbatim (a ```<lang> fence), not be silently replaced by Python.
    blob = "\n".join(_src(c) for c in cells).lower()
    for lang in ("cypher", "sparql", "datalog", "graphql"):
        if lang in blob and f"```{lang}" not in blob:
            warns.append(f"chapter mentions {lang.upper()} but shows no ```{lang} block — "
                         "keep the specialized language verbatim, don't replace it with Python")

    # --- unguarded heavy-viz import heuristic ---
    # Rich visualizations (manim/plotly/netron/torchview/torchinfo) are optional.
    # They MUST be wrapped so a missing dep degrades to a static fallback; an
    # unguarded import would crash the cell on a bare machine. Flag it (WARN).
    heavy_viz_deps = ("manim", "plotly", "netron", "torchview", "torchinfo")
    unguarded_heavy_cells: set[int] = set()
    for i, c in enumerate(cells):
        if c["cell_type"] != "code":
            continue
        src = _src(c)
        if "try" in src:
            continue
        for dep in heavy_viz_deps:
            if re.search(rf"^\s*(?:import {dep}\b|from {dep}\b)", src, re.MULTILINE):
                unguarded_heavy_cells.add(i)
                warns.append(f"cell[{i}] imports optional '{dep}' without a try/except "
                             "fallback — wrap rich viz so it degrades to a static PNG/text "
                             "on a bare machine (see references/interactive-visualization.md)")

    # --- 2 + 3. execute code cells, and verify solutions against exercise asserts ---
    ns: dict = {}
    for i, c in enumerate(cells):
        if c["cell_type"] != "code":
            continue
        if i in unguarded_heavy_cells:
            continue  # already flagged (WARN); the missing optional dep would crash here
        src = _src(c)
        py = _python_source(src)
        if py is None:
            continue  # CUDA/C++/shell/magic cell — not Python, would false-positive
        try:
            exec(compile(py, f"cell[{i}]", "exec"), ns)
        except NotImplementedError:
            sol = _solution_after(cells, i)
            if sol is None:
                errors.append(f"cell[{i}] is an unfilled stub with NO solution to verify")
                continue
            try:
                exec(compile(sol, f"cell[{i}]-solution", "exec"), ns)
                exec(compile(_strip_stub(src), f"cell[{i}]-asserts", "exec"), ns)
            except Exception as e:  # noqa: BLE001 - report any solution failure
                errors.append(f"cell[{i}] SOLUTION fails its own asserts: {type(e).__name__}: {e}")
        except Exception as e:  # noqa: BLE001 - report any cell failure
            errors.append(f"cell[{i}] code raised {type(e).__name__}: {e}")

    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s) in {os.path.basename(path)}")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(review(sys.argv[1]))
