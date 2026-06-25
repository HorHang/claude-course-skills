"""
Sample chapter build script — the SOURCE OF TRUTH for the notebook.

Run:  python examples/build_02_bpe_tokenizer.py
First run the figures:  python examples/build_02_bpe_tokenizer_figures.py

A second example, this time **repo-primary**: the source is a real codebase,
Andrej Karpathy's minbpe (https://github.com/karpathy/minbpe). The chapter
follows the repo's own functions and includes "translation bridge" cells that map
each concept to where it lives in the source (file + function). Persona:
graduate; runner profile: Python (pure stdlib, so it runs anywhere).

Never hand-edit the generated .ipynb — edit this script and re-run.
"""
import json
import os
from pathlib import Path

CHAPTER = "02"
TITLE = "Byte Pair Encoding — Training a Tokenizer from Scratch"
SLUG = "BPE_Tokenizer"

OUTPUT_DIR = Path(os.environ.get("BUILD_COURSE_OUTPUT_DIR", Path(__file__).parent))
NB_PATH = OUTPUT_DIR / f"Chapter_{CHAPTER}_{SLUG}.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text}


def code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text}


def solution(text: str, lang: str = "python") -> dict:
    body = text.rstrip("\n")
    return {"cell_type": "markdown", "metadata": {},
            "source": f"<details>\n<summary>▶ Show solution</summary>\n\n```{lang}\n{body}\n```\n\n</details>"}


cells = []

# --- 1. Front matter ---
cells.append(md(r"""# Chapter 02 — Byte Pair Encoding: Training a Tokenizer from Scratch

> Course context: a hands-on walk through **[karpathy/minbpe](https://github.com/karpathy/minbpe)** — the chapters follow the repo's own functions.
> Builds on: Python dicts and lists; UTF-8 bytes.
> Audience: **graduate** · depth: standard

Every LLM starts by turning text into integers. **Byte Pair Encoding (BPE)** is
how GPT-2/3/4 do it: start from raw bytes and repeatedly merge the most frequent
adjacent pair into a new token. By the end of this chapter you'll have
re-implemented the core of `minbpe`'s `BasicTokenizer` — `get_stats`, `merge`, and
the training loop — and you'll know exactly which file each piece lives in.

### What you'll learn
- Why subword tokenization beats both word-level and character-level schemes.
- The two primitives BPE is built from: **`get_stats`** (count pairs) and **`merge`** (replace a pair).
- The **training loop** that grows a vocabulary, and how it maps to `minbpe/basic.py`.
"""))

# --- 2. Concept 1: why subword ---
cells.append(md(r"""## 1. From characters to bytes to subwords

A tokenizer must map text to a finite vocabulary of integer IDs. Two naive
choices both fail:

- **Word-level** — the vocabulary is unbounded and chokes on unseen words (**out-of-vocabulary**).
- **Character-level** — tiny vocabulary, but sequences get very long, so the model wastes its limited context.

**Subword** tokenization is the middle path: frequent chunks ("ing", " the",
"tion") become single tokens, rare words still decompose into pieces, and nothing
is ever out-of-vocabulary because the base alphabet is the 256 possible **bytes**.

```mermaid
graph LR
  T["text: 'the the'"] --> B["utf-8 bytes:<br/>116 104 101 32 116 104 101"]
  B --> M["merge frequent pairs<br/>(training)"]
  M --> V["token ids:<br/>compact sequence"]
```

minbpe starts from UTF-8 bytes precisely so the base vocabulary is always exactly
256 symbols, whatever the input language.
"""))

cells.append(code(r'''text = "the the the"
ids = list(text.encode("utf-8"))   # every str -> a list of 0..255 byte values
print("text     :", text)
print("byte ids :", ids)
print("vocab so far:", "0..255 (every possible byte)")

# round-trips losslessly, the property minbpe's decode() relies on
assert bytes(ids).decode("utf-8") == text
print("PASS")
'''))

cells.append(md(r"""Notice the byte `116` (`t`) and `104` (`h`) and `101` (`e`) repeat: the pair
`(116, 104)` ("th") shows up every time "the" does. **That repetition is the
signal BPE exploits** — the most frequent pair is the best candidate to collapse
into one new token.

> **Translation bridge → minbpe.** This byte view is exactly what
> `minbpe/basic.py` does at the top of `BasicTokenizer.train` and `.encode`:
> `text_bytes = text.encode("utf-8"); ids = list(text_bytes)`. The lossless
> round-trip above is what `BasicTokenizer.decode` guarantees.
"""))

# --- 3. Concept 2: get_stats + merge + train ---
cells.append(md(r"""## 2. The two primitives: count pairs, then merge one

BPE training is a loop over two tiny functions:

1. **`get_stats(ids)`** — count how often each adjacent pair occurs.
2. **`merge(ids, pair, idx)`** — replace every occurrence of `pair` with the new id `idx`.

Each iteration: find the most frequent pair, mint a new id for it, merge. Repeat
until the vocabulary reaches the target size. Here is the whole thing, runnable:
"""))

cells.append(code(r'''def get_stats(ids):
    """Count adjacent pairs: minbpe/base.py -> get_stats()."""
    counts = {}
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair, 0) + 1
    return counts

def merge(ids, pair, idx):
    """Replace each `pair` with `idx`: minbpe/base.py -> merge()."""
    out, i = [], 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            out.append(idx); i += 2
        else:
            out.append(ids[i]); i += 1
    return out

def train(text, vocab_size):
    """Grow a vocabulary by merging: minbpe/basic.py -> BasicTokenizer.train()."""
    assert vocab_size >= 256
    ids = list(text.encode("utf-8"))
    merges = {}
    for i in range(vocab_size - 256):
        stats = get_stats(ids)
        if not stats:
            break
        top = max(stats, key=stats.get)   # most frequent pair (ties: first seen)
        idx = 256 + i
        ids = merge(ids, top, idx)
        merges[top] = idx
    return ids, merges

corpus = "the cat sat on the mat. the cat ran. " * 8
ids_before = list(corpus.encode("utf-8"))
ids_after, merges = train(corpus, vocab_size=256 + 10)   # 10 merges

print(f"bytes before : {len(ids_before)}")
print(f"tokens after : {len(ids_after)}  ({len(ids_before) / len(ids_after):.2f}x shorter)")
print(f"learned merges: {len(merges)}")

assert len(ids_after) < len(ids_before)      # merging always shortens
assert len(merges) == 10                     # we asked for 10 new tokens
print("PASS")
'''))

cells.append(md(r"""![Each merge shortens the token sequence, with diminishing returns](figures/fig_02_compression.png)

The figure shows the payoff over many merges on a larger text: the sequence keeps
shrinking, but with **diminishing returns** — early merges capture the most common
pairs (big wins), later ones are rarer. This is why `vocab_size` is a knob you
tune, not a number you maximize.

> **Translation bridge → minbpe.** Our three functions are the heart of the repo:
> `get_stats` and `merge` live in `minbpe/base.py`; the training loop is
> `BasicTokenizer.train` in `minbpe/basic.py`. The real `train` also stores a
> `vocab` dict (id → bytes) so `decode` can reverse it — try adding that next.
"""))

# --- 4. Exercises ---
cells.append(md(r"""## Exercise 1 — implement `get_stats`

Count every adjacent pair. **Predict** the counts for `[1, 2, 1, 2, 1]` before
running, then make the asserts pass.
"""))
cells.append(code(r'''def get_stats(ids):
    raise NotImplementedError  # your turn

assert get_stats([1, 2, 1, 2, 1]) == {(1, 2): 2, (2, 1): 2}
assert get_stats([5]) == {}            # no pairs in a single element
assert get_stats([]) == {}
print("PASS")
'''))
cells.append(solution(r'''def get_stats(ids):
    counts = {}
    for pair in zip(ids, ids[1:]):     # zip stops at the shorter -> no index errors
        counts[pair] = counts.get(pair, 0) + 1
    return counts
'''))

cells.append(md(r"""## Exercise 2 — implement `merge`

Replace every occurrence of `pair` with the single new id `idx`, scanning left to
right. **Predict** the result of merging `(1, 2)` into `99` over `[1, 2, 1, 2, 1]`.
"""))
cells.append(code(r'''def merge(ids, pair, idx):
    raise NotImplementedError  # your turn

assert merge([1, 2, 1, 2, 1], (1, 2), 99) == [99, 99, 1]
assert merge([1, 2, 3], (4, 5), 99) == [1, 2, 3]     # pair absent -> unchanged
assert merge([1, 1, 1], (1, 1), 9) == [9, 1]         # no overlapping double-merge
print("PASS")
'''))
cells.append(solution(r'''def merge(ids, pair, idx):
    out, i = [], 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            out.append(idx); i += 2     # skip BOTH elements of the merged pair
        else:
            out.append(ids[i]); i += 1
    return out
'''))

cells.append(md(r"""## Exercise 3 — the training loop

Using your `get_stats` and `merge`, implement `train_bpe(text, num_merges)` that
returns the final token list. **Predict** the length after 1 merge on `"ababab"`
(its bytes are `[97, 98, 97, 98, 97, 98]`).
"""))
cells.append(code(r'''def train_bpe(text, num_merges):
    raise NotImplementedError  # your turn

out1 = train_bpe("ababab", 1)            # merges (97,98) -> 256 three times
assert out1 == [256, 256, 256]
assert len(train_bpe("ababab", 2)) <= len(out1)   # more merges never lengthens
print("PASS")
'''))
cells.append(solution(r'''def train_bpe(text, num_merges):
    ids = list(text.encode("utf-8"))
    for i in range(num_merges):
        stats = get_stats(ids)
        if not stats:
            break
        top = max(stats, key=stats.get)
        ids = merge(ids, top, 256 + i)
    return ids
'''))

# --- 5. Further reading ---
cells.append(md(r"""## Further reading

**Source of truth**
- [karpathy/minbpe](https://github.com/karpathy/minbpe) — `minbpe/base.py` (`get_stats`, `merge`) and `minbpe/basic.py` (`BasicTokenizer`).

**Going deeper**
- Sennrich, Haddow & Birch, *Neural Machine Translation of Rare Words with Subword Units* (2016) — the paper that brought BPE to NLP.
- Karpathy, *Let's build the GPT Tokenizer* (YouTube) — the video companion to minbpe.
"""))

# --- 6. Recap ---
cells.append(md(r"""## Recap
- Subword tokenization avoids both out-of-vocabulary words and overly long character sequences.
- BPE starts from the **256 byte values** so nothing is ever out-of-vocabulary.
- Training is a loop of two primitives: **`get_stats`** (count adjacent pairs) and **`merge`** (replace the most frequent pair with a new id) — `minbpe/base.py`.
- The loop that grows the vocabulary is `BasicTokenizer.train` in `minbpe/basic.py`; `vocab_size` trades sequence length against vocabulary size.

Next: `encode`/`decode` — applying learned merges to new text, and reversing them losslessly.
"""))


notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py", "mimetype": "text/x-python", "name": "python",
            "nbconvert_exporter": "python", "pygments_lexer": "ipython3", "version": "3.11",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
NB_PATH.write_text(json.dumps(notebook, indent=1))
print(f"wrote {NB_PATH} ({len(cells)} cells)")
