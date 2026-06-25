# Tutoring Method

The full Socratic loop for teaching a course notebook. Adapted from the `guide_learn` skill; this file adds the **notebook-mapping** and **persona** specifics. (Cross-reference, don't re-derive: the core method is `guide_learn`.)

## Mapping a notebook to a lesson

| Notebook element | Teaching use |
|------------------|--------------|
| Front matter `> Audience: **<persona>**` | Sets question difficulty and explanation depth |
| `## N. <Concept>` headers | The lesson roadmap (show as ✅ / 👉 / ⏳) |
| Concept markdown + figure | The "explain ONE concept" material |
| Runnable code cell | "Predict the output" / "why this line?" quizzes |
| `## Exercise N` + `### Solution` | Ready-made quizzes — pose the exercise, withhold the solution |
| Assignments / Capstone | Optional deeper practice after the section is understood |

Read the actual cells before teaching; never teach from memory of "how it usually works".

## The loop (per concept)

1. **Explain ONE concept** — a few sentences to a short paragraph at the persona's depth. Point to the figure and the relevant code cell. Stop at one idea; don't front-load.
2. **Quiz** — 1 (max 2) questions that require *thinking*, not recall: predict output, "why N*4 not N?", "what breaks if we remove this?", spot-the-bug, or "explain it back". Prefer the section's embedded exercise when it fits.
3. **STOP and end the turn.** Never answer your own question; never start concept N+1 in the same turn.
4. **Evaluate the reply** — name exactly what's right, pinpoint what's wrong, supply the correction and the *why*. Encouraging and specific. Reveal the embedded solution only after a real attempt. If wrong/unsure: reteach differently and re-quiz the same idea before advancing.

## Persona adaptation at teach time

- **Fresh student** — smaller steps, define terms, more hints before revealing; gentle quizzes.
- **Graduate** — standard depth; expect derivations in answers.
- **PhD / researcher** — push on edge cases, assumptions, and "when does this fail?".
- **Entry-level practitioner** — emphasize "how/when to use"; quiz on applying it.
- **Senior engineer** — quiz on trade-offs, complexity, and design alternatives; skip basics.

If the recorded persona seems off (answers too easy/hard), offer to switch via AskUserQuestion.

## Consolidation & resuming

- At milestones: 2-3 line recap + one synthesis question linking concepts.
- For long notebooks, offer to save a checkpoint (which sections are ✅) so a later session resumes cleanly.

## Red flags (stop immediately)

- You're about to type the answer to a question you just asked.
- You're teaching the next concept in the same turn you quizzed the last.
- You revealed an exercise solution before the learner attempted it.
- You haven't opened the notebook.
