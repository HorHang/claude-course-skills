"""
Manim scene for Chapter_18a_Muon_Optimizer_Math.ipynb.

Animates the geometric meaning of orthogonalization (the HF "What just happened" intuition):
two skewed, unequal-length column vectors of a 2x2 update matrix morph into PERPENDICULAR,
UNIT-length vectors. This is a schematic of the blog's concrete 2x2 example
([[10, 0.5], [0.5, 0.1]] -> an orthogonal matrix); the exact numbers live in the notebook's
worked-example cell.

Render to a GIF (no LaTeX needed; uses Text/Arrow only). Run from /home/hang/llm.c:
    manim -ql --format=gif -o anim_18a_orthogonalize \
        course/build_ch18a_animation.py OrthogonalizeScene
then copy media/.../anim_18a_orthogonalize.gif to course/figures/.
Source of intuition: https://huggingface.co/blog/onekq/muon-optimizer#what-just-happened
"""
import numpy as np
from manim import (
    ApplyMatrix,
    Arrow,
    Create,
    DEGREES,
    Dot,
    Dot3D,
    DOWN,
    FadeIn,
    FadeOut,
    LEFT,
    ORIGIN,
    RIGHT,
    Scene,
    Sphere,
    Surface,
    Text,
    ThreeDAxes,
    ThreeDScene,
    TracedPath,
    Transform,
    UP,
    VGroup,
    WHITE,
    Write,
)

BLUE = "#2b6cb0"
ORANGE = "#dd6b20"
GREEN = "#2f855a"
GREY = "#718096"
RED = "#c53030"
YELLOW = "#d69e2e"

A, B, C = 3.4445, -4.7750, 2.0315  # Newton-Schulz quintic coefficients (KellerJordan/Muon)


class OrthogonalizeScene(Scene):
    def construct(self):
        # light axes
        x_axis = Arrow(LEFT * 3.2, RIGHT * 3.2, color=GREY, buff=0, stroke_width=2)
        y_axis = Arrow(DOWN * 2.6, UP * 2.6, color=GREY, buff=0, stroke_width=2)
        self.add(x_axis, y_axis)

        title = Text("A weight update is two column vectors", font_size=28).to_edge(UP)
        self.play(Write(title))

        # BEFORE: skewed (nearly parallel) and very unequal in length
        v1 = Arrow(ORIGIN, RIGHT * 2.7 + UP * 0.35, color=BLUE, buff=0, stroke_width=6)
        v2 = Arrow(ORIGIN, RIGHT * 2.2 + UP * 1.1, color=ORANGE, buff=0, stroke_width=6)
        l1 = Text("column 1 (big)", font_size=22, color=BLUE).next_to(v1.get_end(), RIGHT, buff=0.15)
        l2 = Text("column 2 (small, skewed)", font_size=22, color=ORANGE).next_to(v2.get_end(), UP, buff=0.15)
        self.play(Create(v1), Create(v2), FadeIn(l1), FadeIn(l2))
        self.wait(0.6)

        cap_before = Text("Before: skewed, unequal lengths -> a few directions dominate",
                          font_size=24, color=GREY).to_edge(DOWN)
        self.play(FadeIn(cap_before))
        self.wait(1.0)

        # AFTER: perpendicular, equal (unit) length
        v1_new = Arrow(ORIGIN, RIGHT * 2.2, color=BLUE, buff=0, stroke_width=6)
        v2_new = Arrow(ORIGIN, UP * 2.2, color=ORANGE, buff=0, stroke_width=6)
        l1_new = Text("length 1", font_size=22, color=BLUE).next_to(v1_new.get_end(), DOWN, buff=0.15)
        l2_new = Text("length 1", font_size=22, color=ORANGE).next_to(v2_new.get_end(), RIGHT, buff=0.15)
        cap_after = Text("After orthogonalization: perpendicular + equal length -> all directions weighted equally",
                         font_size=22, color=GREEN).to_edge(DOWN)

        new_title = Text("Newton-Schulz orthogonalizes the update", font_size=28).to_edge(UP)
        self.play(
            Transform(v1, v1_new),
            Transform(v2, v2_new),
            Transform(l1, l1_new),
            Transform(l2, l2_new),
            Transform(title, new_title),
            Transform(cap_before, cap_after),
            run_time=2.2,
        )
        self.wait(1.4)

        # right-angle hint
        corner = VGroup(
            Arrow(RIGHT * 0.45, RIGHT * 0.45 + UP * 0.45, color=GREEN, buff=0, stroke_width=3),
            Arrow(UP * 0.45, RIGHT * 0.45 + UP * 0.45, color=GREEN, buff=0, stroke_width=3),
        )
        self.play(Create(corner))
        self.wait(1.2)


def _Rz(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def _Ry(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])


class SVD3DScene(ThreeDScene):
    """SVD as rotate -> scale -> rotate in 3D: the unit sphere becomes an ellipsoid whose
    semi-axis lengths are the singular values; orthogonalizing (all sigma=1) makes it a sphere."""

    def construct(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-50 * DEGREES)
        axes = ThreeDAxes(x_range=[-3.2, 3.2, 1], y_range=[-3.2, 3.2, 1], z_range=[-3.2, 3.2, 1],
                          x_length=6.4, y_length=6.4, z_length=6.4)
        sphere = Sphere(radius=1.0, resolution=(22, 22)).set_color(BLUE).set_opacity(0.55)
        self.add(axes, sphere)

        title = Text("SVD: G = U . S . V^T  (a sphere becomes an ellipsoid)", font_size=26)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)

        Vt = _Rz(35 * np.pi / 180.0)            # V^T : rotate
        Sig = np.diag([3.0, 1.5, 0.6])          # Sigma : stretch by singular values
        U = _Ry(40 * np.pi / 180.0) @ _Rz(25 * np.pi / 180.0)   # U : rotate

        l1 = Text("1) V^T : rotate (sphere looks unchanged)", font_size=24, color=GREEN).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(l1)
        self.play(ApplyMatrix(Vt, sphere), run_time=1.4)
        self.wait(0.3)

        l2 = Text("2) S : stretch axes by singular values (3, 1.5, 0.6)", font_size=23, color=ORANGE).to_edge(DOWN)
        self.play(FadeOut(l1))
        self.add_fixed_in_frame_mobjects(l2)
        self.play(ApplyMatrix(Sig, sphere), run_time=2.0)       # ellipsoid forms
        self.wait(0.4)

        l3 = Text("3) U : rotate the ellipsoid", font_size=24, color=GREEN).to_edge(DOWN)
        self.play(FadeOut(l2))
        self.add_fixed_in_frame_mobjects(l3)
        self.play(ApplyMatrix(U, sphere), run_time=1.6)
        self.wait(0.4)

        l4 = Text("singular values = the ellipsoid's semi-axis lengths (3, 1.5, 0.6)",
                  font_size=23, color=ORANGE).to_edge(DOWN)
        self.play(FadeOut(l3))
        self.add_fixed_in_frame_mobjects(l4)
        self.begin_ambient_camera_rotation(rate=0.35)
        self.wait(2.6)
        self.stop_ambient_camera_rotation()

        l5 = Text("orthogonalize: set every singular value = 1  ->  back to a sphere "
                  "(equal in all directions)", font_size=21, color=GREEN).to_edge(DOWN)
        self.play(FadeOut(l4))
        self.add_fixed_in_frame_mobjects(l5)
        # current sphere = U S V^T applied. Map it to the orthogonalized U V^T (a sphere):
        #   T (U S V^T) = U V^T  =>  T = U S^{-1} U^{-1}
        T = U @ np.linalg.inv(Sig) @ np.linalg.inv(U)
        self.play(ApplyMatrix(T, sphere), run_time=2.0)
        self.wait(1.6)


def _ns(G: np.ndarray, steps: int = 5) -> np.ndarray:
    """Newton-Schulz orthogonalization (same math as build_ch18a_figures._ns)."""
    X = G / (np.linalg.norm(G) + 1e-7)
    transposed = X.shape[-2] > X.shape[-1]
    if transposed:
        X = X.T
    for _ in range(steps):
        AA = X @ X.T
        BB = B * AA + C * (AA @ AA)
        X = A * X + BB @ X
    if transposed:
        X = X.T
    return X


def _landscape_problem() -> dict:
    """Rebuild the SAME ill-conditioned least-squares problem and SGD-momentum / Muon
    trajectories as build_ch18a_figures.fig_loss_landscape (seed 0). Returns the on-plane
    loss function and both projected paths so the 3D surface and the two descending walks
    sit on exactly the figure's PCA plane (Li et al. trajectory method)."""
    rng = np.random.default_rng(0)
    d, n = 24, 80
    W_true = rng.standard_normal((d, d))
    Uc, _ = np.linalg.qr(rng.standard_normal((d, d)))
    cond = np.geomspace(1.0, 0.01, d)          # 100x stretch -> a long narrow valley
    X = (Uc * cond) @ rng.standard_normal((d, n))
    Y = W_true @ X

    def loss(W: np.ndarray) -> float:
        r = W @ X - Y
        return 0.5 * float(np.sum(r * r)) / n

    def grad(W: np.ndarray) -> np.ndarray:
        return ((W @ X - Y) @ X.T) / n

    def muon_update(g: np.ndarray, M: np.ndarray, beta: float = 0.95) -> np.ndarray:
        M[:] = beta * M + (1 - beta) * g
        look = beta * M + (1 - beta) * g
        o = _ns(look, 5)
        return o * (max(1, o.shape[-2] / o.shape[-1]) ** 0.5)

    def train(kind: str, steps: int, lr: float) -> np.ndarray:
        W = np.zeros((d, d))
        M = np.zeros_like(W)
        path = [W.ravel().copy()]
        for _ in range(steps):
            g = grad(W)
            if kind == "sgd":
                M = 0.95 * M + g
                W = W - lr * M
            else:
                W = W - lr * muon_update(g, M)
            path.append(W.ravel().copy())
        return np.array(path)

    P_sgd = train("sgd", 80, 0.6)
    P_muon = train("muon", 80, 0.5)
    w_star = W_true.ravel()

    deltas = np.vstack([P_sgd - w_star, P_muon - w_star])
    _, _, Vt = np.linalg.svd(deltas, full_matrices=False)
    dir1, dir2 = Vt[0], Vt[1]
    D1, D2 = dir1.reshape(d, d), dir2.reshape(d, d)

    def proj(P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        Dl = P - w_star
        return Dl @ dir1, Dl @ dir2

    a_sgd, b_sgd = proj(P_sgd)
    a_muon, b_muon = proj(P_muon)

    def loss_on_plane(a: float, b: float) -> float:
        return loss(W_true + a * D1 + b * D2)

    return {
        "loss_on_plane": loss_on_plane,
        "a_sgd": a_sgd, "b_sgd": b_sgd,
        "a_muon": a_muon, "b_muon": b_muon,
        "loss_sgd": loss(P_sgd[-1].reshape(d, d)),
        "loss_muon": loss(P_muon[-1].reshape(d, d)),
    }


class LossLandscapeWalkScene(ThreeDScene):
    """The §3d loss landscape in 3D. The ill-conditioned least-squares problem becomes a
    long, narrow valley; SGD-momentum (grey) and Muon (orange) start at the same point and
    walk down it for the same number of steps. SGD stalls climbing the steep wall side-to-side;
    Muon orthogonalizes its step and flows along the valley floor to a lower loss. Twin of
    course/figures/fig_18a_loss_landscape.png, now animated and in 3D."""

    def construct(self):
        data = _landscape_problem()
        loss_on_plane = data["loss_on_plane"]
        a_sgd, b_sgd = data["a_sgd"], data["b_sgd"]
        a_muon, b_muon = data["a_muon"], data["b_muon"]

        # grid extent = path extent + padding (same convention as the 2D figure)
        a_all = np.concatenate([a_sgd, a_muon, [0.0]])
        b_all = np.concatenate([b_sgd, b_muon, [0.0]])
        pa = 0.12 * (a_all.max() - a_all.min())
        pb = 0.12 * (b_all.max() - b_all.min())
        a_lo, a_hi = a_all.min() - pa, a_all.max() + pa
        b_lo, b_hi = b_all.min() - pb, b_all.max() + pb

        # height = log-compressed loss, normalized to [0, H] (valley low, walls high)
        gx = np.linspace(a_lo, a_hi, 36)
        gy = np.linspace(b_lo, b_hi, 36)
        zgrid = np.maximum(np.array([[loss_on_plane(a, b) for a in gx] for b in gy]), 1e-4)
        lz = np.log10(zgrid)
        lz_min, lz_max = float(lz.min()), float(lz.max())
        H = 3.4

        def height(a: float, b: float) -> float:
            return (np.log10(max(loss_on_plane(a, b), 1e-4)) - lz_min) / (lz_max - lz_min) * H

        # map the plane's (a, b) into a tidy [-3, 3] cube so the surface looks balanced
        def nx(a: float) -> float:
            return (a - a_lo) / (a_hi - a_lo) * 6 - 3

        def ny(b: float) -> float:
            return (b - b_lo) / (b_hi - b_lo) * 6 - 3

        axes = ThreeDAxes(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[0, H, 1],
            x_length=6.6, y_length=6.6, z_length=3.6,
        )
        surface = Surface(
            lambda u, v: axes.c2p(nx(u), ny(v), height(u, v)),
            u_range=[a_lo, a_hi], v_range=[b_lo, b_hi],
            resolution=(36, 36), fill_opacity=0.82, stroke_width=0.4,
        )
        surface.set_fill_by_value(
            axes=axes, axis=2,
            colorscale=[(BLUE, 0.0), (GREEN, 0.45 * H), (YELLOW, 0.7 * H), (ORANGE, 0.88 * H), (RED, H)],
        )
        surface.set_stroke(WHITE, width=0.4, opacity=0.18)

        self.set_camera_orientation(phi=64 * DEGREES, theta=-52 * DEGREES, zoom=0.95)

        title = Text("The loss landscape: an ill-conditioned valley", font_size=30, weight="BOLD")
        title.to_edge(UP, buff=0.35)
        if title.width > 13:
            title.scale_to_fit_width(13)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1.0)

        self.play(Create(surface), run_time=2.4)

        def pt(a: float, b: float, lift: float = 0.10):
            return axes.c2p(nx(a), ny(b), height(a, b) + lift)

        minimum = Dot3D(pt(0.0, 0.0, lift=0.04), radius=0.10, color=RED)
        start = Dot3D(pt(a_sgd[0], b_sgd[0]), radius=0.09, color=WHITE)
        self.play(FadeIn(minimum), FadeIn(start))

        # legend + caption, fixed in frame so the rotating camera never skews them
        legend = VGroup(
            Dot(color=GREY, radius=0.09), Text("SGD-momentum", font_size=22, color=GREY),
            Dot(color=ORANGE, radius=0.09), Text("Muon", font_size=22, color=ORANGE),
        ).arrange_in_grid(rows=2, cols=2, col_widths=[0.5, 2.6], buff=0.18)
        legend.to_corner(UP + LEFT, buff=0.4).shift(DOWN * 0.95)  # clear the title band
        self.add_fixed_in_frame_mobjects(legend)
        self.play(FadeIn(legend))

        # subsample the 80-step paths to keep the walk crisp and the render light
        idx = np.linspace(0, len(a_sgd) - 1, 26).round().astype(int)
        sgd_pts = [pt(a_sgd[i], b_sgd[i]) for i in idx]
        muon_pts = [pt(a_muon[i], b_muon[i]) for i in idx]

        sgd_dot = Dot3D(sgd_pts[0], radius=0.085, color=GREY)
        muon_dot = Dot3D(muon_pts[0], radius=0.085, color=ORANGE)
        sgd_trail = TracedPath(sgd_dot.get_center, stroke_color=GREY, stroke_width=4)
        muon_trail = TracedPath(muon_dot.get_center, stroke_color=ORANGE, stroke_width=4)
        self.add(sgd_trail, muon_trail, sgd_dot, muon_dot)

        cap = Text("Same start, same step budget: watch where each spends its travel",
                   font_size=24, color=GREY).to_edge(DOWN, buff=0.35)
        if cap.width > 13:
            cap.scale_to_fit_width(13)
        self.add_fixed_in_frame_mobjects(cap)
        self.play(FadeIn(cap))

        self.begin_ambient_camera_rotation(rate=0.10)
        for k in range(1, len(idx)):
            self.play(
                sgd_dot.animate.move_to(sgd_pts[k]),
                muon_dot.animate.move_to(muon_pts[k]),
                run_time=0.16, rate_func=lambda t: t,
            )
        self.wait(0.3)
        self.stop_ambient_camera_rotation()

        outcome = Text(
            f"Muon flows down the valley floor — final loss {data['loss_muon']:.2f} "
            f"vs SGD's {data['loss_sgd']:.2f}",
            font_size=23, color=GREEN,
        ).to_edge(DOWN, buff=0.35)
        if outcome.width > 13:
            outcome.scale_to_fit_width(13)
        self.play(FadeOut(cap))
        self.add_fixed_in_frame_mobjects(outcome)
        self.play(FadeIn(outcome))

        self.begin_ambient_camera_rotation(rate=0.18)
        self.wait(3.0)
        self.stop_ambient_camera_rotation()
