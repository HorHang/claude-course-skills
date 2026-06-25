# Installation & setup

These are [Agent Skills](https://www.anthropic.com/news/agent-skills). This repo is also a **Claude Code plugin marketplace**, so the cleanest install is the plugin system; manual copy works everywhere else.

## Claude Code — as a plugin (recommended)

In Claude Code, run:

```
/plugin marketplace add HorHang/claude-course-skills
/plugin install course-skills@claude-course-skills
```

`/build-course`, `/teach-course`, and `/update-course` are available immediately. The plugin bundles all three skills, so you manage them as one unit:

- **Update** to the latest version: `/plugin update course-skills`
- **Disable / enable / remove**: from the `/plugin` menu, or `claude plugin uninstall course-skills@claude-course-skills`
- **Refresh the catalog** after the repo changes: `/plugin marketplace update claude-course-skills`

> The marketplace name is `claude-course-skills`; the plugin inside it is `course-skills` — hence `course-skills@claude-course-skills`.

## Claude Code — manual copy

Prefer not to use the plugin system (or want project-scoped skills)?

**User-level (available in every project):**

```bash
git clone https://github.com/HorHang/claude-course-skills.git
cp -r claude-course-skills/skills/* ~/.claude/skills/
```

**Project-level (shared with your team via git):**

```bash
cp -r claude-course-skills/skills/* /path/to/your-repo/.claude/skills/
```

Start a new Claude Code session; `/build-course`, `/teach-course`, and `/update-course` are now available.

### Stay up to date

```bash
cd claude-course-skills && git pull
cp -r skills/* ~/.claude/skills/
```

Prefer a symlink if you want changes to apply without re-copying:

```bash
ln -s "$(pwd)/skills/build-course"  ~/.claude/skills/build-course
ln -s "$(pwd)/skills/teach-course"  ~/.claude/skills/teach-course
ln -s "$(pwd)/skills/update-course" ~/.claude/skills/update-course
```

## Other agent hosts

Agent Skills are portable. Copy the same `skills/*` folders into the host's skills directory:

| Host | Skills directory (typical) |
|------|----------------------------|
| Cursor | the agent/skills folder in your workspace config |
| Codex | your configured skills directory |
| Copilot CLI | auto-discovered from installed plugins |
| Gemini CLI | activated via skill metadata at session start |

`teach-course` and `update-course` need nothing extra. `build-course` runs Python build/figure scripts, so it needs a Python toolchain (below).

## Requirements

| Skill | Needs |
|-------|-------|
| `build-course` | Python 3.11+, `matplotlib`; `nvcc` (NVIDIA CUDA toolkit) only for CUDA chapters |
| `teach-course` | Nothing beyond the agent host (reads `.ipynb` JSON) |
| `update-course` | Python 3.11+ and the chapter's `build_<ch>.py` |

Notebook verification uses `subprocess`, not Jupyter/nbconvert, so it runs anywhere Python does. To view generated notebooks, any of VS Code, JupyterLab, Jupyter Notebook, GitHub, or nbviewer works — Mermaid diagrams and collapsible solutions render in all of them.

## Verify the install

In a new session, ask your agent:

```
/build-course
```

If the skill responds by asking about your source and learner persona, you're set.

## Troubleshooting

- **Skill not found / not triggering** — confirm the folder landed at `~/.claude/skills/<name>/SKILL.md`, then restart the session. Skills are discovered at session start.
- **`matplotlib` import error** — `pip install matplotlib` (or add it to your environment).
- **CUDA chapter won't compile** — install the NVIDIA CUDA toolkit so `nvcc` is on `PATH`; non-CUDA chapters don't need it.
- **Collapsible solutions show open** — view the notebook in VS Code / JupyterLab / GitHub; the skill uses an HTML `<details>` block rather than `source_hidden` for exactly this reason.
