# update-course — revise a chapter and regenerate it

`update-course` keeps a course alive. When teaching ([teach-course](teach-course.md)) or feedback reveals a chapter is too hard, has an error, or lacks a concrete example, this skill revises the chapter's **build script** and regenerates the notebook. The course is a living artifact — you fix the chapter, not just re-explain it in the moment.

> Triggers: `/update-course`, "this chapter is too hard", "update/improve the course", "add an example to chapter", "fix this notebook chapter".

## Core principle

The **build script is the source of truth.** Every change goes into `build_<ch>.py` (and `build_<ch>_figures.py`), then you re-run to emit the `.ipynb`. **Never hand-edit the `.ipynb`** — the next rebuild would wipe it.

## When to use it

- A learner repeatedly stalls on the same concept or asks for an example the chapter lacks.
- A cell is wrong, confusing, or too dense; a difficulty spike loses the learner.
- `teach-course` recommended an update for a specific concept.

**Not for:** authoring a brand-new chapter (use [build-course](build-course.md)) or a one-off explanation the learner just needs right now.

## The workflow

1. **Identify the chapter and the friction** — the specific concept and what's missing.
2. **Open `build_<ch>.py`** (the source of truth). If only the `.ipynb` exists, reconstruct the build script first.
3. **Apply the minimal revision** (playbook below) — keep the front matter (persona, languages) intact and the change scoped.
4. **Regenerate** the figures (if changed) and the notebook.
5. **Re-review** with the bundled reviewer; fix every error.
6. **Report** the concrete change and the reviewer result.

## Revision playbook (symptom → change)

| Symptom from teaching / feedback | Change to the build script |
|----------------------------------|----------------------------|
| "Too abstract / I don't get it" | Add a concrete worked example before the definition; add a predict-then-run demo. |
| Learner keeps asking for an example | Insert a runnable example (or concept-simulation) for that exact concept. |
| Difficulty spike — one cell jumps too far | Split into intermediate steps; add a bridging cell. |
| Wall-of-text cell | Split along the concept arc: motivate → define → figure → gap → runnable → interpret. |
| The diagram doesn't land | Add or improve a Mermaid diagram. |
| Exercise too hard / too easy | Re-tune to the persona; add a stub or hint; adjust the asserts. |
| A claim is wrong or uncited | Correct it and cite the source. |
| A query/DSL was paraphrased in Python | Restore the specialized language verbatim. |
| Cell errors out | Fix the code; the reviewer must pass. |

## Requirements

Python 3.11+ and the chapter's `build_<ch>.py`. It re-runs the build and the reviewer.

## See also

- [build-course](build-course.md) — authors chapters in the first place.
- [teach-course](teach-course.md) — surfaces what to fix while tutoring.
- The full skill spec: [`skills/update-course/SKILL.md`](../skills/update-course/SKILL.md).
