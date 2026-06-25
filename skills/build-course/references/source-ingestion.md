# Source Ingestion

How to read each source type and turn it into a chapter skeleton. Always confirm with the learner **which source is primary** (it sets the chapter spine) before outlining.

## Primary vs assisting sources

| Mode | Spine (chapter order) | Assisting role |
|------|-----------------------|----------------|
| **Repo-primary** | The codebase modules/components/dirs | Book + blogs supply theory, citations, mental models |
| **Book-primary** | The book's table of contents | Repo (often none) + blogs supply runnable code & examples |

Ask via AskUserQuestion. If only one source was given, infer but still confirm.

## Source language (multi-language source trees)

Some sources ship the same content in several languages (e.g. a Hugo repo with `content/en/`, `content/zh/`, `content/tw/`, or an `i18n/` dir). Do NOT pick one arbitrarily:
- Detect parallel language dirs — sibling folders with matching filenames, or an `i18n/` folder.
- **AskUserQuestion: which language to read the source in.** Prefer the most complete copy: the original is usually fuller than in-progress translations (compare line counts to spot the fullest).
- If the chosen reading language differs from the learner's desired output language, **translate as you author**, and record both the **source language** and the **output (content) language** in chapter front matter.

## Multiple sources covering the same material (align by chapter)

When several sources describe the *same* curriculum (e.g. full book text + summary notes + a code repo all covering the same chapters), don't force a single "primary". Instead **align them per chapter**:
- Pick one spine (usually the fullest text, or the book ToC).
- For each chapter, map in the slice from every source — the depth text, a concise recap source, and the matching hands-on code dir.
- Build a small table (chapter → {text section, notes section, code dir}) before outlining, and reuse each source for what it is best at.

## GitHub repo

- Clone or browse with Glob/Grep/Read; or use the GitHub MCP tools (`mcp__plugin_ecc_github__get_file_contents`, `search_code`).
- Map the architecture: entry points, core modules, data flow. Each cohesive module/concept ≈ one chapter.
- Extract: what each module does, the key functions (`path:line`), and how pieces connect. These become the "translation bridge" cells (abstract concept → real code in this repo).
- Read README / docs / examples first; they usually reveal the intended learning order.
- If the repo already contains **chapter-structured prose** (e.g. `content/<lang>/chN.md`), treat it as the chapter spine and ADOPT it — reuse its sections and existing figure files rather than regenerating from scratch (see notebook-blueprint.md "Adopt existing chapter markdown"). Build on top: add runnable cells, exercises, and translation bridges.
- If the repo is a **reference implementation in one language** (e.g. Go) but the learner wants another, plan to **port** it (see runner-profiles.md "Port a reference implementation").

## PDF / book

- Read with the `pages` parameter (max 20 pages/request; required for PDFs >10 pages). Start with the table of contents to get the chapter spine.
- Per chapter: pull the core claims, definitions, diagrams described in prose, and any worked examples.
- Books are often **prose-only** — no runnable code. This is the high-value case: plan a **concept-simulation** (see runner-profiles.md) so the learner can experiment, not just read.
- Capture page references for citations in the "Further reading" cell.

## Blog posts / URLs

- Use WebFetch per URL (cached 15 min) or WebSearch to find canonical/source-of-truth posts; firecrawl skills for bulk crawl.
- Treat blogs as assisting material: fill gaps, provide the newest numbers, and supply diagrams or code the primary source lacks.
- Always verify a blog's claims against the primary source or official docs before teaching them.

## Output of this phase

A short ordered chapter outline: for each chapter — title, 1-line scope, prerequisites, the primary-source anchor (repo path or book section), and which runner profile its code cells will use. Get buy-in (Phase 3) before generating.
