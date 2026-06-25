# Contributing to claude-course-skills

Thanks for helping make learning more hands-on. Contributions of all sizes are welcome — from typo fixes to new runner profiles.

## Ways to contribute

- **Report a bug** — a generated chapter that won't run, a reviewer false-positive, a host where install fails. Open an issue with the source you used, the persona, and the error.
- **Add a runner profile** — the executable-cell recipe for a new domain or language (Rust, Go, R, Julia, Scala/Spark, …). See `skills/build-course/references/runner-profiles.md` for the existing ones.
- **Add a learner persona** — a new audience with its own depth/figure/difficulty knobs. See `skills/build-course/references/learner-personas.md`.
- **Improve the docs** — clearer examples, more worked sources, better troubleshooting.
- **Share an example course** — built from a *public* source, so others can see the output.

## How these skills are structured

Each skill is a folder under `skills/`:

```
skills/
├── build-course/   SKILL.md + references/ + assets/ (templates, reviewer)
├── teach-course/   SKILL.md + references/
└── update-course/  SKILL.md
```

- `SKILL.md` is the entry point — its YAML front matter (`name`, `description`) controls when the agent triggers the skill, so keep the trigger phrases in `description` accurate.
- `references/*.md` hold the detailed playbooks the skill loads on demand. Keep them focused and cross-link rather than duplicate.
- `assets/*.py` are templates the skill copies into a course (the build-script template, figures template, and notebook reviewer).

## Editing guidelines

- **Don't hand-edit generated `.ipynb` files** — that principle applies to the skills too. The notebook is always a build artifact of `build_<ch>.py`.
- Keep changes minimal and scoped. Match the surrounding style of the file you edit.
- When you change a trigger phrase or workflow step, update the matching `docs/*.md` page so the public docs stay in sync.
- Test a skill change by running it end to end in your agent host on a small public source before opening the PR.

## Pull requests

1. Fork and branch from `main`.
2. Make the change; verify it locally.
3. Describe **what** changed and **why**, and which skill(s) it touches.
4. Link any related issue.

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
