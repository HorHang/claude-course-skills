"""
Sample chapter build script — the SOURCE OF TRUTH for the notebook.

Run:  python examples/build_01_quorum_consistency.py
First run the figures:  python examples/build_01_quorum_consistency_figures.py

This is a real, runnable example produced by the `build-course` skill, kept in
the repo so visitors can see the output. It teaches quorum consistency in
leaderless replication (Designing Data-Intensive Applications, ch. 5) for a
GRADUATE persona, using the Python "concept-simulation" runner profile: the idea
is prose in the book, so here it becomes a small runnable model.

Never hand-edit the generated .ipynb — edit this script and re-run.
"""
import json
import os
from pathlib import Path

CHAPTER = "01"
TITLE = "Quorum Consistency in Leaderless Replication"
SLUG = "Quorum_Consistency"

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
cells.append(md(r"""# Chapter 01 — Quorum Consistency in Leaderless Replication

> Course context: an active-learning companion to *Designing Data-Intensive Applications* (Kleppmann), chapter 5, "Replication".
> Builds on: basic probability; the idea that data is copied across several nodes.
> Audience: **graduate** · depth: standard

A leaderless datastore (Dynamo-style: Cassandra, Riak, Voldemort) has no single
node that owns the truth. A write goes to several replicas, a read asks several
replicas — and the system stays consistent **only if those two sets are
guaranteed to overlap**. This chapter turns that one inequality into something
you can run, break, and measure.

### What you'll learn
- Why `n`, `w`, and `r` (replicas, write quorum, read quorum) are the knobs of a leaderless store.
- The quorum condition **w + r > n**, and *why* it guarantees a read sees the latest write.
- How to measure the probability of a stale read when the condition does **not** hold.
"""))

# --- 2. Concept 1: overlap ---
cells.append(md(r"""## 1. Replicas, and the read-your-writes problem

Replication buys **availability** and **read throughput**: keep `n` copies of each
key, and the system survives nodes going down. But it raises a question the
single-node world never had — *after I write, will my next read see it?*

In a leaderless store the client itself talks to replicas. A write is sent to all
`n` and is considered done once **`w`** replicas acknowledge it. A read is sent to
all `n` and returns once **`r`** replicas respond. The **key terms**:

- **n** — number of replicas per key.
- **w** — write quorum: acknowledgements required for a write to succeed.
- **r** — read quorum: responses required for a read to succeed.

```mermaid
graph LR
  C(("client")) -->|write v2| A["replica 1 · v2"]
  C -->|write v2| B["replica 2 · v2"]
  C -. lagging .-> D["replica 3 · v1"]
  C -->|read r=2| B
  C -->|read r=2| D
```

If a read happens to land only on replicas that missed the latest write, it
returns a **stale** value. Whether that can happen is decided entirely by how
`w` and `r` relate to `n`.
"""))

cells.append(md(r"""The naive choice **w = 1, r = 1** is fastest (one ack, one response) but offers
no guarantee: the one replica you read may not be the one you wrote. Let's make
the overlap concrete by simulating *every* possible write set and read set."""))

cells.append(code(r'''from itertools import combinations

def overlap_guaranteed(n: int, w: int, r: int) -> bool:
    """True iff EVERY write quorum of size w intersects EVERY read quorum of
    size r. Brute-forced over all subsets so we can SEE the guarantee, not just
    assert the formula."""
    replicas = range(n)
    for write_set in combinations(replicas, w):
        ws = set(write_set)
        for read_set in combinations(replicas, r):
            if ws.isdisjoint(read_set):
                return False  # a read that misses the write entirely
    return True

n = 5
for w, r in [(1, 1), (3, 3), (4, 2), (1, 5)]:
    print(f"n={n}  w={w}  r={r}  ->  overlap guaranteed: {overlap_guaranteed(n, w, r)}")

assert overlap_guaranteed(5, 3, 3) is True
assert overlap_guaranteed(5, 1, 1) is False
print("PASS")
'''))

cells.append(md(r"""Read the output against the formula: overlap is guaranteed exactly when
**w + r > n**. With `n = 5`, `(3,3)` and `(4,2)` and `(1,5)` all clear the bar;
`(1,1)` does not. The brute force agrees with the inequality because there is no
room for a disjoint pair once the two sets are big enough to be forced to share a
replica (pigeonhole)."""))

# --- 3. Concept 2: the condition + measuring staleness ---
cells.append(md(r"""## 2. w + r > n, and the cost of breaking it

The condition has a one-line intuition: a write touches `w` replicas, a read
touches `r`; if `w + r > n` the two sets are too large to fit into `n` slots
without colliding, so they **must** share at least one replica — and that shared
replica carries the latest write.

When you *violate* it (to go faster), staleness isn't all-or-nothing; it has a
probability. If the latest write reached `w` replicas and a reader picks `r`
replicas uniformly at random, the read is stale only when its `r` picks avoid all
`w` up-to-date ones:

$$P(\text{stale}) = \dfrac{\binom{n-w}{r}}{\binom{n}{r}} \quad (0 \text{ when } w + r > n)$$

![Stale-read probability falls to zero once w + r > n (n=5, w=3)](figures/fig_01_stale_read.png)
"""))

cells.append(code(r'''import random
from math import comb

def prob_stale_exact(n: int, w: int, r: int) -> float:
    """Closed form: chance an r-read misses all w up-to-date replicas."""
    if r > n - w:
        return 0.0
    return comb(n - w, r) / comb(n, r)

def prob_stale_monte_carlo(n: int, w: int, r: int, trials: int = 200_000, seed: int = 0) -> float:
    """Same quantity, measured by simulation, to confirm the formula."""
    rng = random.Random(seed)
    replicas = list(range(n))
    up_to_date = set(range(w))            # the w replicas that got the latest write
    stale = 0
    for _ in range(trials):
        read = rng.sample(replicas, r)    # r replicas chosen uniformly
        if up_to_date.isdisjoint(read):
            stale += 1
    return stale / trials

n, w = 5, 3
for r in range(1, n + 1):
    exact = prob_stale_exact(n, w, r)
    sim = prob_stale_monte_carlo(n, w, r)
    print(f"r={r}  exact={exact:.3f}  simulated={sim:.3f}")

# the simulation must track the closed form, and w+r>n must be exactly 0
assert abs(prob_stale_monte_carlo(5, 3, 2) - prob_stale_exact(5, 3, 2)) < 0.01
assert prob_stale_exact(5, 3, 3) == 0.0
print("PASS")
'''))

cells.append(md(r"""Two things to take away from the table. First, the Monte-Carlo column tracks the
closed form — the formula isn't magic, it's just counting. Second, the moment
`r` reaches `3` (so `w + r = 6 > 5`) the probability snaps to exactly `0`: that is
the guarantee from section 1, now visible as the cliff in the figure.

> **Idealization (say it out loud):** this models a single write that already
> reached exactly `w` replicas and uniform random reads. Real systems add
> concurrent writes, read repair, hinted handoff, and clock skew — quorums make
> stale reads *unlikely*, not *impossible* in practice. See the book for the
> caveats."""))

# --- 4. Exercises ---
cells.append(md(r"""## Exercise 1 — the quorum condition from scratch

Implement `quorum_guarantees_consistency(n, w, r)` returning `True` exactly when a
read is guaranteed to see the latest acknowledged write. **Predict** the four
results below before running, then make the asserts pass.
"""))
cells.append(code(r'''def quorum_guarantees_consistency(n: int, w: int, r: int) -> bool:
    raise NotImplementedError  # your turn

assert quorum_guarantees_consistency(5, 3, 3) is True
assert quorum_guarantees_consistency(5, 4, 2) is True
assert quorum_guarantees_consistency(5, 1, 1) is False
assert quorum_guarantees_consistency(3, 2, 2) is True
print("PASS")
'''))
cells.append(solution(r'''def quorum_guarantees_consistency(n: int, w: int, r: int) -> bool:
    # the whole rule, one line: the two quorums must be forced to overlap
    return w + r > n
'''))

cells.append(md(r"""## Exercise 2 — minimum read quorum

For a fixed `n` and `w`, what is the **smallest** read quorum `r` that still
guarantees consistency? Implement `min_consistent_r(n, w)`. (Assume `1 <= w <= n`.)
"""))
cells.append(code(r'''def min_consistent_r(n: int, w: int) -> int:
    raise NotImplementedError  # your turn

assert min_consistent_r(5, 3) == 3
assert min_consistent_r(5, 1) == 5   # tiny write quorum forces reading everyone
assert min_consistent_r(3, 3) == 1   # writing to all means reading one is enough
print("PASS")
'''))
cells.append(solution(r'''def min_consistent_r(n: int, w: int) -> int:
    # need w + r > n  =>  r > n - w  =>  smallest integer r is n - w + 1,
    # but never fewer than 1 read and never more than n.
    return max(1, min(n, n - w + 1))
'''))

cells.append(md(r"""## Exercise 3 — read availability vs consistency

A pure consistency knob ignores availability. If `f` replicas are down, a read of
`r` succeeds only when `r <= n - f`. Implement `max_tolerated_failures(n, w)`:
the largest `f` such that, using the **minimum consistent r** from Exercise 2,
reads still succeed. **Predict** whether a write-heavy config (`w=5`) tolerates
more or fewer failures than a balanced one (`w=3`).
"""))
cells.append(code(r'''def max_tolerated_failures(n: int, w: int) -> int:
    raise NotImplementedError  # your turn

# n=5, w=3 -> min r = 3 -> reads need 3 up -> can lose 2
assert max_tolerated_failures(5, 3) == 2
# n=5, w=5 -> min r = 1 -> reads need 1 up -> can lose 4 on reads
assert max_tolerated_failures(5, 5) == 4
print("PASS")
'''))
cells.append(solution(r'''def max_tolerated_failures(n: int, w: int) -> int:
    r = max(1, min(n, n - w + 1))   # minimum consistent read quorum (Exercise 2)
    return n - r                    # reads need r replicas up, so n - r may be down
'''))

# --- 5. Further reading ---
cells.append(md(r"""## Further reading

**Source of truth**
- Kleppmann, *Designing Data-Intensive Applications*, ch. 5 — "Quorums for reading and writing" and "Limitations of quorum consistency".

**Going deeper**
- DeCandia et al., *Dynamo: Amazon's Highly Available Key-value Store* (2007) — the origin of the n/w/r model.
- Apache Cassandra docs — tunable consistency levels (`ONE`, `QUORUM`, `ALL`) map directly onto `r` and `w`.
"""))

# --- 6. Recap ---
cells.append(md(r"""## Recap
- A leaderless store is tuned by three numbers: **n** replicas, **w** write quorum, **r** read quorum.
- **w + r > n** forces every read quorum to overlap every write quorum, so a read sees the latest write (pigeonhole).
- Breaking the condition trades consistency for speed/availability; the stale-read probability is `C(n-w, r) / C(n, r)`, which the simulation confirmed.
- The same knobs trade off against failure tolerance — a bigger `w` lets reads tolerate more down nodes, and vice versa.

Next: read repair and anti-entropy — how stale replicas catch up *after* a quorum read detects the divergence.
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
