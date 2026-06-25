import importlib.util
import os
from pathlib import Path

CHAPTER = "99"
OUTPUT_DIR = Path(os.environ.get("BUILD_COURSE_OUTPUT_DIR", "course"))
FIG_DIR = OUTPUT_DIR / "figures"

_asset = Path(__file__).resolve().parents[2] / "skills/build-course/assets/figures-template.py"
_spec = importlib.util.spec_from_file_location("figtpl", _asset)
_figtpl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_figtpl)
_figtpl.CHAPTER = CHAPTER
_figtpl.OUTPUT_DIR = OUTPUT_DIR
_figtpl.FIG_DIR = FIG_DIR


def main():
    gif = _figtpl.animate_to_gif(
        lambda ax, i: (ax.plot([0, 1], [0, i / 4.0]), ax.set_ylim(0, 3)),
        n_frames=6, name="descent")
    _figtpl.loss_surface(lambda a, b: a ** 2 + 0.5 * b ** 2, name="bowl", n=20)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    (FIG_DIR / "descent.ext").write_text(gif.suffix)  # ".gif" or ".png"
    print(f"descent artifact: {gif.name}")


if __name__ == "__main__":
    main()
