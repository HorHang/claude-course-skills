# Assignments & Final Project Rubric

Three distinct things — do not conflate them:

| Artifact | Scope | Count | Where |
|----------|-------|-------|-------|
| **Inline exercises** | One chapter, quick in-flow checks | 3-5 per chapter | Inside each chapter notebook (collapsible solutions) |
| **Assignments** | Span everything taught so far | **~5 for the WHOLE course** | Their own explicit notebooks, released at 20% milestones |
| **Final project** | The whole course, integrative | **1** | Its own notebook, after the course completes |

## Milestone schedule (the 20% rule)

The course has 5 assignments total, one released after each **20% of the course**. With `N` chapters, release assignment `k` (k = 1..5) after chapter `ceil(k * N / 5)`:

| N chapters | Assignments after chapters |
|-----------|----------------------------|
| 5 | 1, 2, 3, 4, 5 |
| 10 | 2, 4, 6, 8, 10 |
| 12 | 3, 5, 8, 10, 12 |
| 20 | 4, 8, 12, 16, 20 |

Each assignment is **cumulative** — it draws on every chapter up to its milestone, not just the latest one. Generate an assignment notebook only when its milestone chapter has been built.

## Assignment notebook anatomy

One file per assignment: `Assignment_<k>_<topic>.ipynb`. Contents:

- **Header** — which 20% milestone, which chapters it covers, the `> Audience: **<persona>**` line.
- **2-4 problems** mixing the milestone's chapters. Each problem has: Context · Deliverables · Acceptance criteria (objective/checkable) · optional starter stub · a **collapsible** self-check / reference solution (use the `solution()` helper).
- Escalating difficulty across the 5 assignments (see ladder).

## Difficulty ladder (across the 5 course assignments)

| Assignment | ~Milestone | Emphasis |
|-----------|-----------|----------|
| 1 | 20% | Apply early concepts to new inputs |
| 2 | 40% | Modify / combine two concepts |
| 3 | 60% | Implement a component from a spec |
| 4 | 80% | Analyze / measure / compare; interpret |
| 5 | 100% | Extend / design; open-ended |

Scale scaffolding by persona (learner-personas.md): fresh-student assignments give stubs and tight specs; PhD/senior assignments are open and rigorous.

## Final project (one, after the course)

File: `Final_Project_<title>.ipynb`, generated after the last chapter. A single integrative build that uses concepts from across the whole course.

- **Brief** — the problem and why it's worth building.
- **Milestones** — 3-5 checkpoints so it isn't one intimidating blob.
- **Definition of done** — measurable outcome (a working tool, a benchmark report, a small library).
- **Stretch goals** — for advanced personas.
- **Scope by persona** — fresh student: tightly specified build; PhD/senior: ambitious extension, novel variant, or perf/scalability target.

Keep assignments and the final project runnable in the same environment / runner profile as the chapters, so the learner never leaves the notebook.

## Building these notebooks

Reuse build-script-template.py (same `md()` / `code()` / `solution()` helpers and nbformat output). An assignment/final-project notebook is just a notebook whose cells are problems + collapsible solutions instead of the concept arc.
