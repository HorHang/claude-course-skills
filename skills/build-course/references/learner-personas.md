# Learner Personas

Ask the learner to pick a persona (AskUserQuestion) **before drafting**. Record the chosen persona in the chapter front matter so regeneration stays consistent and `teach-course` can read it. The persona maps to concrete, deterministic knobs — not vibes.

## Persona → adaptation knobs

| Persona | Term definitions | Math depth | Figures | Code/sim | Exercises | Assignments | Capstone |
|---------|------------------|-----------|---------|----------|-----------|-------------|----------|
| **Fresh student** | Define every term on first use | Minimal; intuition first, formulas optional | Many (1 per sub-concept) | Heavily commented, fill-in-the-blank | 3, gentle, lots of scaffolding | 5, guided, partial stubs | Small, step-by-step spec |
| **Graduate** | Define domain-specific terms only | Standard; show key derivations | 1 per major concept | Commented, some TODOs | 4, moderate | 5, acceptance criteria only | Medium, open-ended spec |
| **PhD / researcher** | Assume vocabulary; cite primary sources | Full derivations, edge cases, proofs sketched | Selective, information-dense | Minimal scaffolding; reference impls | 4-5, includes open/research-flavored | 5, rigorous, may cite papers | Ambitious; novel extension or ablation |
| **Entry-level practitioner** | Define jargon; emphasize usage | Light; "how/when", not "why-proof" | Workflow/architecture diagrams | Runnable, production-shaped | 4, applied | 5, build-something tasks | Realistic mini-project |
| **Senior engineer** | Skip basics | Trade-offs, complexity, perf models | Comparison tables/plots | Dense expert path | 3-5, focus on design trade-offs | 5, design/perf-oriented | System-level, perf or scalability focus |

## How the knobs apply

- **Vocabulary / definitions** — whether to inline-define terms or assume them.
- **Math depth** — from "intuition only" to "full derivation".
- **Pacing / figure density** — more figures + smaller steps for earlier personas.
- **Exercise & assignment difficulty** — see assignments-rubric.md; scale the acceptance criteria and the amount of provided scaffolding.
- **Capstone scope** — from a tightly-specified small build to an open research extension.

## Front-matter record

Each chapter's front matter includes a line such as:

```
> Audience: **graduate** · depth: standard · prerequisites: <list>
```

If the learner is unsure, default to **graduate** and offer to adjust. `teach-course` reads this line and may re-confirm or switch persona at learn time.
