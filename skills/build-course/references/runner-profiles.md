# Runner Profiles

A runner profile is the recipe for the **executable cells** in a chapter. Pick the profile that matches the source domain. The goal: the learner *runs* something every chapter, not just reads.

## Profiles

### Python (default for most ML/DS/SWE/DE)
Direct code cells. Install deps once at the top:
```
!pip -q install numpy matplotlib
```
Use `assert` statements as built-in correctness checks so exercises self-grade:
```python
assert abs(result - expected) < 1e-6, f"got {result}"
print("PASS")
```

### CUDA / C / C++ (write-compile-run)
Mirror the `Chapter_14a` pattern. One bash cell makes the build dir, one code cell writes the source, one bash cell compiles + runs:
```
!mkdir -p <course>/<ch>_build
```
```
%%writefile <course>/<ch>_build/demo.cu
// ... full self-contained source ...
```
```
!nvcc -O2 -lcublas -o <course>/<ch>_build/demo <course>/<ch>_build/demo.cu && ./<course>/<ch>_build/demo
```
The `&&` runs the binary only if compilation succeeds. Adjust `-l<lib>` flags per chapter.

### Bash / CLI (tools, data engineering, SWE ops)
Run commands directly; create scratch files with `%%writefile`. Echo expected vs actual to verify.

### SQL (databases, analytics, data engineering)
Use an embedded engine that needs no server — `sqlite3` via Python, or DuckDB:
```python
import sqlite3, textwrap
con = sqlite3.connect(":memory:")
con.executescript(textwrap.dedent("""... schema + inserts ..."""))
print(con.execute("SELECT ...").fetchall())
```

### Concept-simulation (THE differentiator — for prose/conceptual books)
When the source is conceptual (DDIA, *AI Engineering* theory, distributed systems, probability) and has no code, **construct a small runnable model** so the learner experiments with the idea. Rule: **prefer a runnable simulation over a static diagram whenever a concept can be made interactive.** Only fall back to pseudocode when genuinely non-computable.

Examples:
- *Replication (DDIA)* — simulate leader/follower with artificial lag; measure stale-read probability vs lag.
- *Quorums (DDIA)* — a `w + r > n` calculator that shows which (w,r) choices guarantee read-your-writes.
- *Partitioning (DDIA)* — a consistent-hashing ring; show key redistribution when a node joins/leaves.
- *Bayesian updating (Statistical Rethinking)* — grid-approximate a posterior and sweep the prior/data.
- *Evaluation (AI Engineering)* — a tiny eval harness scoring toy model outputs against a rubric.

Keep sims < ~40 lines, pure-Python + numpy, deterministic (seed RNG), and end with a printed result the learner can predict first.

### Port a reference implementation (translate existing code to the learner's language)
When the source ships real, tested code in a language the learner didn't choose (e.g. `letsddia-go` is Go, learner wants Python), **port it** rather than re-inventing:
- Translate the reference file into the chosen language, preserving behavior and naming intent.
- Keep the **original** as a "translation bridge" markdown cell (`source path:line`) so the learner sees the Go↔target mapping.
- Reuse the upstream **tests** (e.g. `*_test.go`) as the exercise's correctness check — re-express the same assertions in the chosen language and end with `print("PASS")`.
- Cite the source file; don't present the port as original work.
- Record the chosen code language in chapter front matter so `teach-course` explains in the same language.

### Specialized / domain language (keep verbatim, run for real)
When the chapter teaches a specific query/markup/DSL language, the runnable cells use THAT language — never a Python translation of it. Make it executable in-notebook:
- **SQL** — `sqlite3` (stdlib) or DuckDB, in-memory.
- **SPARQL** — `rdflib` over a tiny in-memory graph.
- **Cypher / graph queries** — a small Python graph stand-in + the real Cypher shown as the reference (point to Neo4j for the real engine if none embeds cleanly).
- **Regex / jq / GraphQL / config DSLs** — run the actual tool/library.

Optionally add a Python cell that produces the **same result** as a labelled mapping aid — but keep the specialized language primary; the learner is here to read *that* syntax.

NOTE: the "Port a reference implementation" profile above applies only to **generic implementation code** (e.g. a Go data structure → Python). It does NOT apply to a subject language like SQL/Cypher/SPARQL — those are the learning target and are kept verbatim, not ported.

### Animation / interactive-viz (motion & interactivity for ML/DL)
When a concept is better felt through MOTION or interactivity — a math transform,
a gradient-descent path, optimization geometry, a network's architecture, attention
internals — use the interactive-visualization tier. **Contract: try-rich / except-static.**
Each cell attempts the rich path (manim, plotly, netron, real model introspection)
and, on any missing dependency, degrades to a static matplotlib PNG / text summary and
prints a one-line `NOTE`. This keeps the core dependency floor at matplotlib and keeps
`review-notebook.py` green on a bare machine.

- Animation -> `animate_to_gif(frame_fn, ...)` (filmstrip PNG fallback).
- Loss landscape -> `loss_surface(loss_fn, ...)` (static 3D PNG fallback).
- Architecture -> `netron.start(model_file)` -> `torchinfo` text -> Mermaid `graph LR`.
- Web-only tools (Transformer Explainer, LIT, CNN Explainer, ...) -> `interactive_callout(...)`.

Recipes, the decision matrix, and the full tool catalog: see
references/interactive-visualization.md. Use it ONLY when motion/interactivity teaches;
otherwise a still matplotlib plot or a Mermaid diagram is the right call.

### Beyond-the-laptop infra (cluster / distributed / production)
When the real thing needs infra the learner's machine lacks (Kafka, Spark, a multi-node DB, GPUs): run a **single-machine simulation** for the aha (concept-simulation), and add a **"Going to production" cell** naming the real setup, topology, resource needs, and how to provision it. Never present a toy as if it were the production system. See notebook-blueprint.md "Scaling ceiling".

## Choosing

| Source domain | Profile |
|---------------|---------|
| GPU / systems C/C++ | CUDA / C |
| ML / DS / general Python | Python |
| Databases / analytics | SQL |
| CLI tools / pipelines / ops | Bash |
| Conceptual / architecture / theory book | Concept-simulation |
| Source has reference code in another language | Port-reference-implementation (+ chosen-language profile) |
| Subject IS a query/markup/DSL language (SQL, Cypher, SPARQL…) | Specialized / domain language (keep verbatim, run for real) |
| Needs a cluster / distributed / GPU / prod infra | Concept-simulation + a "Going to production" cell |
| Concept needs motion / interactivity (animation, loss landscape, architecture, attention) | Animation / interactive-viz (often mixed with Python) |

A chapter may mix profiles (e.g. a Python sim plus a SQL demo). Record the chosen profile(s) per chapter in the outline.
