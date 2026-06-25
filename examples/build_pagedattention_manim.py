"""
README hero animation, the manim edition: how PagedAttention fixes the KV-cache
memory problem, step by step — rendered with 3Blue1Brown's manim for a polished,
smooth explainer.

This is the *polish* path of build-course's animation tier. manim (+ ffmpeg) is a
heavy dependency, but it is only needed on the machine that REGENERATES the GIF;
the committed artifact renders for every reader on GitHub. When manim is absent,
build-course degrades to the matplotlib version in build_pagedattention_animation.py
(see skills/build-course/references/interactive-visualization.md — "manim optional
for polish").

Content is faithful to the vLLM / PagedAttention paper (Kwon et al., 2023,
arXiv:2309.06180, Figures 2, 3, 6):

    prompt  = "Four score and seven years ago our"   (7 tokens, block size 4)
    outputs = "fathers", "brought", ...
    block table: logical 0,1,2 -> physical 7,1,3  (allocated on demand)

Render (writes the gif into media/, then move it to examples/figures/):
    manim -ql --fps 18 --format=gif -o pagedattention.gif \
        examples/build_pagedattention_manim.py PagedAttention
"""
from manim import (
    BOLD, DOWN, LEFT, RIGHT, UP, ORIGIN, WHITE,
    Arrow, Brace, Create, FadeIn, FadeOut, Flash, GrowFromCenter, Indicate,
    ManimColor, RoundedRectangle, Scene, SurroundingRectangle, Text,
    TransformFromCopy, VGroup, Write,
)

# --- palette -------------------------------------------------------------
BG = ManimColor("#0f1722")
USED = ManimColor("#2a9d8f")
WASTE = ManimColor("#39414f")
ALLOC = ManimColor("#e76f51")
PHYS = ManimColor("#457b9d")
TABLE = ManimColor("#52808a")
MUTED = ManimColor("#9aa7b4")

PROMPT = ["Four", "score", "and", "seven", "years", "ago", "our"]


def cell(label: str, w: float, h: float, fill: ManimColor, *, fs: int = 22,
         tcol=WHITE, op: float = 1.0, stroke=WHITE, sw: float = 1.4) -> VGroup:
    """A rounded rectangle with an auto-fitting centered label."""
    sq = RoundedRectangle(corner_radius=0.06, width=w, height=h,
                          fill_color=fill, fill_opacity=op,
                          stroke_color=stroke, stroke_width=sw)
    g = VGroup(sq)
    if label:
        t = Text(label, font_size=fs, color=tcol, weight=BOLD)
        if t.width > w * 0.86:
            t.scale_to_fit_width(w * 0.86)
        t.move_to(sq)
        g.add(t)
    return g


FRAME_MAX_W = 13.0  # keep titles/captions clear of the frame's left/right edges


def _fit(t: Text) -> Text:
    """Shrink a line of text so it never runs past the frame edges."""
    if t.width > FRAME_MAX_W:
        t.scale_to_fit_width(FRAME_MAX_W)
    return t


def heading(text: str) -> Text:
    """A title pinned to the top band. Content must sit BELOW it (use under_title)."""
    return _fit(Text(text, font_size=30, weight=BOLD, color=WHITE)).to_edge(UP, buff=0.45)


def caption(text: str, color=MUTED) -> Text:
    return _fit(Text(text, font_size=22, color=color)).to_edge(DOWN, buff=0.4)


def under_title(mob, head, buff: float = 0.5):
    """Anchor a mobject just below the title band so the two never overlap.

    The #1 cause of title/content collisions is positioning content with an
    absolute upward shift (``.shift(UP * k)``) that reaches into the title's row.
    Instead, anchor the topmost content element to the title with this helper,
    then chain the rest downward with ``.next_to(prev, DOWN)``.
    """
    return mob.next_to(head, DOWN, buff=buff)


class PagedAttention(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        self.intro()
        self.act_problem()
        self.act_idea()
        self.act_mechanism()
        self.act_payoff()

    # -- intro ------------------------------------------------------------
    def intro(self) -> None:
        title = Text("PagedAttention", font_size=66, weight=BOLD, color=USED)
        sub = Text("how vLLM stops wasting GPU memory on the KV cache",
                   font_size=28, color=MUTED).next_to(title, DOWN, buff=0.35)
        self.play(Write(title), run_time=1.1)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(0.8)
        self.play(FadeOut(title), FadeOut(sub))

    # -- act 1: the problem ----------------------------------------------
    def act_problem(self) -> None:
        head = heading("The problem: a contiguous KV cache wastes most of GPU memory")
        self.play(FadeIn(head, shift=DOWN * 0.2))

        used = 5
        reserved = 12
        cw = 0.92
        cells = VGroup(*[
            cell(PROMPT[i] if i < used else "", cw, 0.82,
                 USED if i < used else WASTE, fs=16,
                 stroke=WHITE if i < used else MUTED)
            for i in range(reserved)
        ]).arrange(RIGHT, buff=0.07).shift(UP * 1.0)
        label_a = Text("Request A reserves 12 slots — its max possible length",
                       font_size=22, color=WHITE).next_to(cells, UP, buff=0.3)

        self.play(Write(label_a))
        self.play(*[GrowFromCenter(cells[i]) for i in range(used)],
                  lag_ratio=0.12, run_time=1.3)
        self.play(*[FadeIn(cells[i]) for i in range(used, reserved)],
                  lag_ratio=0.04, run_time=0.8)

        brace = Brace(cells[used:], DOWN, color=ALLOC)
        btext = Text("reserved + internal fragmentation — never used",
                     font_size=20, color=ALLOC).next_to(brace, DOWN, buff=0.15)
        self.play(GrowFromCenter(brace), FadeIn(btext))
        self.wait(0.4)

        # request B can't fit the leftover gap -> external fragmentation
        need, gap = 6, 4
        rowb = VGroup(*[
            cell("", cw, 0.82, WASTE if i < gap else ALLOC, op=0.85,
                 stroke=MUTED if i < gap else ALLOC)
            for i in range(need)
        ]).arrange(RIGHT, buff=0.07)
        rowb.next_to(cells, DOWN, buff=1.7).align_to(cells, LEFT)
        label_b = Text("Request B needs 6 — only a 4-slot gap is free",
                       font_size=22, color=WHITE).next_to(rowb, UP, buff=0.25)
        self.play(FadeOut(brace), FadeOut(btext))
        self.play(Write(label_b), FadeIn(rowb))
        xfit = Text("✗ can't fit → external fragmentation", font_size=22,
                    color=ALLOC, weight=BOLD).next_to(rowb, RIGHT, buff=0.4)
        self.play(Indicate(rowb[gap:], color=ALLOC), Write(xfit))

        cap = caption("Only 20–38% of KV-cache memory holds real tokens — "
                      "60–80% is wasted.  (vLLM, Fig. 2)", color=ALLOC)
        self.play(FadeIn(cap))
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in (head, label_a, cells, rowb, label_b,
                                         xfit, cap)])

    # -- act 2: the idea --------------------------------------------------
    def act_idea(self) -> None:
        head = heading("The idea: page the cache into fixed-size blocks")
        self.play(FadeIn(head, shift=DOWN * 0.2))

        def make_block(toks, fill):
            slots = VGroup(*[cell(t, 1.05, 0.6, fill if t else WASTE, fs=16)
                             for t in toks]).arrange(RIGHT, buff=0.05)
            box = SurroundingRectangle(slots, color=WHITE, buff=0.08, stroke_width=2)
            return VGroup(box, slots)

        # Title-safe layout: anchor the first label BELOW the title, then chain
        # everything downward. No content uses an absolute upward shift.
        b0 = make_block(["Four", "score", "and", "seven"], USED)
        b1 = make_block(["years", "ago", "our", ""], USED)
        llabel = under_title(Text("Logical blocks (B = 4)", font_size=22, color=WHITE),
                             head, buff=0.55)
        logical = VGroup(b0, b1).arrange(RIGHT, buff=0.8).next_to(llabel, DOWN, buff=0.3)
        self.play(Write(llabel), FadeIn(logical, shift=DOWN * 0.2))
        self.wait(0.3)

        # scatter blocks to non-contiguous physical memory
        glabel = Text("Physical GPU memory (any block, anywhere)",
                      font_size=22, color=WHITE).next_to(logical, DOWN, buff=0.7)
        grid = VGroup(*[cell(f"#{i}", 1.1, 0.7, WASTE, fs=16, op=0.7,
                            stroke=MUTED, tcol=MUTED) for i in range(9)])\
            .arrange(RIGHT, buff=0.12).next_to(glabel, DOWN, buff=0.3)
        self.play(Write(glabel), FadeIn(grid))

        targets = {0: 6, 1: 2}
        self.play(*[grid[gi][0].animate.set_fill(PHYS, 1.0).set_stroke(WHITE)
                    for gi in targets.values()])
        arrows = VGroup(*[
            Arrow(logical[bi].get_bottom(), grid[gi].get_top(), buff=0.15,
                  stroke_width=3, color=PHYS, max_tip_length_to_length_ratio=0.12)
            for bi, gi in targets.items()
        ])
        self.play(*[Create(a) for a in arrows])
        cap = caption("Blocks live anywhere — like pages in OS virtual memory. "
                      "A block table maps logical → physical.")
        self.play(FadeIn(cap))
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in (head, llabel, logical, glabel, grid,
                                         arrows, cap)])

    # -- act 3: the mechanism (the paper's running example) ---------------
    def act_mechanism(self) -> None:
        head = heading('How it runs: prompt "Four score and seven years ago our"')
        self.play(FadeIn(head, shift=DOWN * 0.2))

        def lblock(name, toks, fresh_idx=None):
            slots = VGroup(*[
                cell(t, 0.95, 0.5,
                     ALLOC if (fresh_idx == i and t) else (USED if t else WASTE),
                     fs=13)
                for i, t in enumerate(toks)
            ]).arrange(RIGHT, buff=0.04)
            tag = Text(name, font_size=16, color=MUTED).next_to(slots, LEFT, buff=0.15)
            return VGroup(tag, slots)

        def pblock(idx, toks, highlight=False):
            slots = VGroup(*[cell(t, 0.8, 0.5, PHYS if t else WASTE, fs=12)
                             for t in toks]).arrange(RIGHT, buff=0.04)
            box = SurroundingRectangle(
                slots, color=ALLOC if highlight else PHYS, buff=0.06,
                stroke_width=4 if highlight else 2)
            tag = Text(f"#{idx}", font_size=16, color=MUTED)\
                .next_to(box, LEFT, buff=0.15)
            return VGroup(tag, box, slots)

        def trow(a, b, c, fill):
            return VGroup(*[cell(v, 1.05, 0.5, fill, fs=15)
                            for v in (a, b, c)]).arrange(RIGHT, buff=0.05)

        # ---- logical blocks (left) ----
        b0 = lblock("L0", ["Four", "score", "and", "seven"])
        b1 = lblock("L1", ["years", "ago", "our", ""])
        logical = VGroup(b0, b1).arrange(DOWN, buff=0.35)\
            .to_edge(LEFT, buff=0.5).shift(UP * 0.6)
        ltitle = Text("Logical blocks", font_size=20, weight=BOLD, color=WHITE)\
            .next_to(logical, UP, buff=0.3)

        # ---- physical blocks (right) ----
        p7 = pblock(7, ["Four", "score", "and", "seven"])
        p1 = pblock(1, ["years", "ago", "our", ""])
        physical = VGroup(p7, p1).arrange(DOWN, buff=0.4)\
            .to_edge(RIGHT, buff=0.5).shift(UP * 0.7)
        ptitle = Text("Physical KV blocks (non-contiguous)", font_size=20,
                      weight=BOLD, color=WHITE).next_to(physical, UP, buff=0.3)

        # ---- block table (center) ----
        thead = trow("logical", "physical", "#fill", ManimColor("#22303c"))
        r0 = trow("0", "7", "4", TABLE)
        r1 = trow("1", "1", "3", TABLE)
        table = VGroup(thead, r0, r1).arrange(DOWN, buff=0.08).move_to(ORIGIN + UP * 0.6)
        ttitle = Text("Block table", font_size=20, weight=BOLD, color=WHITE)\
            .next_to(table, UP, buff=0.3)

        sub = Text("Prefill: 7 prompt tokens fill L0–L1 → physical blocks 7 and 1",
                   font_size=22, color=MUTED).to_edge(DOWN, buff=0.5)

        self.play(FadeIn(ltitle), FadeIn(ttitle), FadeIn(ptitle))
        self.play(FadeIn(logical), FadeIn(thead))
        self.play(FadeIn(r0), TransformFromCopy(b0[1], p7[2]))
        self.play(FadeIn(r1), TransformFromCopy(b1[1], p1[2]))
        a0 = Arrow(r0.get_right(), p7.get_left(), buff=0.15, color=PHYS, stroke_width=3)
        a1 = Arrow(r1.get_right(), p1.get_left(), buff=0.15, color=PHYS, stroke_width=3)
        self.play(Create(a0), Create(a1), FadeIn(sub))
        self.wait(0.8)

        # decode step 1: generate "fathers" into the last free slot of L1
        sub1 = Text('Decode ①: generate "fathers" into L1\'s last free slot — no new memory',
                    font_size=22, color=USED).to_edge(DOWN, buff=0.5)
        fathers_l = Text("fathers", font_size=13, color=WHITE, weight=BOLD)
        fathers_l.scale_to_fit_width(0.95 * 0.86).move_to(b1[1][3])
        fathers_p = fathers_l.copy().move_to(p1[2][3])
        self.play(FadeOut(sub), FadeIn(sub1))
        self.play(b1[1][3][0].animate.set_fill(USED, 1.0),
                  p1[2][3][0].animate.set_fill(PHYS, 1.0),
                  FadeIn(fathers_l), FadeIn(fathers_p))
        new_fill = cell("4", 1.05, 0.5, TABLE, fs=15).move_to(r1[2])
        self.play(Indicate(r1[2], color=USED), FadeIn(new_fill))
        self.wait(0.8)

        # decode step 2: L1 full -> allocate a NEW physical block (3) for "brought"
        sub2 = Text('Decode ②: L1 is full → allocate a NEW block (#3) on demand for "brought"',
                    font_size=22, color=ALLOC).to_edge(DOWN, buff=0.5)
        b2 = lblock("L2", ["brought", "", "", ""], fresh_idx=0)\
            .next_to(b1, DOWN, buff=0.35).align_to(b1, LEFT)
        p3 = pblock(3, ["brought", "", "", ""], highlight=True)\
            .next_to(p1, DOWN, buff=0.4).align_to(p1, LEFT)
        r2 = trow("2", "3", "1", ALLOC).next_to(r1, DOWN, buff=0.08)
        self.play(FadeOut(sub1), FadeIn(sub2))
        self.play(FadeIn(b2, shift=RIGHT * 0.2))
        self.play(GrowFromCenter(p3), Flash(p3, color=ALLOC, line_length=0.3))
        a2 = Arrow(r2.get_right(), p3.get_left(), buff=0.15, color=ALLOC, stroke_width=3)
        self.play(FadeIn(r2), Create(a2))
        self.wait(1.3)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # -- act 4: the payoff ------------------------------------------------
    def act_payoff(self) -> None:
        head = heading("The payoff: pack memory tight → batch more → serve faster")
        self.play(FadeIn(head, shift=DOWN * 0.2))

        bar_w, bar_h = 9.0, 0.9
        cont_bg = RoundedRectangle(corner_radius=0.06, width=bar_w, height=bar_h,
                                   fill_color=WASTE, fill_opacity=1.0,
                                   stroke_color=MUTED, stroke_width=1.5)
        cont_used = RoundedRectangle(corner_radius=0.06, width=bar_w * 0.3,
                                     height=bar_h, fill_color=USED,
                                     fill_opacity=1.0, stroke_width=0)
        cont = VGroup(cont_bg, cont_used).shift(UP * 1.1)
        cont_used.align_to(cont_bg, LEFT)
        clabel = Text("Contiguous — ~30% used, few requests fit",
                      font_size=22, color=WHITE).next_to(cont, UP, buff=0.25)
        self.play(Write(clabel), FadeIn(cont_bg))
        self.play(GrowFromCenter(cont_used))
        self.wait(0.4)

        n = 16
        blocks = VGroup(*[
            RoundedRectangle(corner_radius=0.04, width=bar_w / n - 0.06,
                             height=bar_h, fill_color=USED if i % 2 == 0 else PHYS,
                             fill_opacity=1.0, stroke_color=BG, stroke_width=1.5)
            for i in range(n)
        ]).arrange(RIGHT, buff=0.06).shift(DOWN * 0.9)
        plabel = Text("PagedAttention — packed, many more requests batched",
                      font_size=22, color=USED).next_to(blocks, UP, buff=0.25)
        self.play(Write(plabel))
        self.play(*[GrowFromCenter(b) for b in blocks], lag_ratio=0.06, run_time=1.4)

        cap = caption("Near-zero waste → up to 2–4× more sequences per batch → "
                      "higher throughput.  (vLLM)", color=USED)
        self.play(FadeIn(cap))
        self.wait(1.6)
        self.play(*[FadeOut(m) for m in self.mobjects])
