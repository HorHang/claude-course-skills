# FAQ

## What are these skills, exactly?

Three [Agent Skills](https://www.anthropic.com/news/agent-skills) for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (and other agent hosts) that turn source material into interactive learning. `build-course` authors notebook chapters from a repo/book/blogs, `teach-course` tutors you through them Socratic-style, and `update-course` revises a chapter when it isn't working.

## How is this different from asking an LLM to "explain this repo"?

A one-off explanation is passive and gone when the chat scrolls away. These skills produce a **persistent, runnable course** — notebooks with code you execute, exercises you solve, and a tutor that quizzes you and corrects your answers. The notebooks are regenerable from build scripts, so they're consistent and maintainable.

## What sources can I turn into a course?

- A **GitHub repo** (a framework, a reference implementation, your own codebase).
- A **book or PDF** — including prose-only conceptual books with no code.
- A **set of blog posts or URLs**.

You can mix them; the skill asks which source is "primary" (it sets the chapter order) and uses the rest as supporting material.

## It's a theory book with no code. What happens?

This is the high-value case. `build-course` writes a **concept-simulation**: a small runnable model of the idea so you can experiment instead of just reading. For example, simulating leader/follower replication lag, a quorum calculator, a consistent-hashing ring, or a Bayesian grid approximation.

## What languages does the generated code use?

Python by default, but you choose the code language for hands-on cells. If the source ships a reference implementation in another language (say Go), it gets **ported** to your language, with the original kept as a bridge and its tests reused as checks. A subject language that *is* the lesson — SQL, Cypher, SPARQL, regex — is kept **verbatim** and run for real, never paraphrased.

## Do I need a GPU?

No. Only chapters whose subject is CUDA/GPU programming need the NVIDIA toolkit (`nvcc`). Material that targets clusters or GPUs you don't have is shrunk to a single-machine simulation, plus a "Going to production" cell describing the real setup.

## Can I use these outside Claude Code?

Yes. Agent Skills are portable — copy the `skills/*` folders into the skills directory of Cursor, Codex, Copilot CLI, or Gemini CLI. `teach-course` and `update-course` need nothing extra; `build-course` needs Python 3.11+ and matplotlib.

## Why generate notebooks from a build script instead of writing them directly?

The `build_<ch>.py` script is the **source of truth**; the `.ipynb` is a build artifact. This makes chapters diffable in git, regenerable, and consistent — and it's why `update-course` can revise a chapter cleanly: edit the script, re-run, done. Hand-editing the notebook would be wiped on the next rebuild.

## How do I fix a chapter that's too hard or has a mistake?

Run [update-course](update-course.md) and describe the friction (e.g. "Chapter 3 is too abstract — add a worked example for attention scores"). It edits the build script, regenerates the notebook, and re-runs the reviewer.

## Are the exercises graded?

Each chapter has 3–5 inline exercises with collapsible solutions and `assert`-based self-checks, so you verify your own attempt. The bundled reviewer also extracts each solution and runs it against the exercise's asserts before a chapter ships — so a wrong solution can't slip through.

## Is it free? What's the license?

Yes — [MIT licensed](../LICENSE). Use it, fork it, build on it. If it helped, a ⭐ on the repo helps others find it.

## How do I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md). New runner profiles (Rust, Go, R, Julia), new learner personas, and example courses from public sources are especially welcome.
