"""Render llm.c's GPT-2 as a Netron graph and crop a legible architecture figure.

This is the *source of truth* for ``figures/gpt2_netron.png`` in the README. It
exports the actual ``GPT`` module from karpathy/llm.c (``train_gpt2.py``) to ONNX,
opens it in Netron's headless server, screenshots the rendered graph with a
render-aware browser, and crops the top region (embeddings + one full transformer
block) so the node labels are readable.

Netron is interactive (web/Electron), so it cannot embed live in GitHub markdown -
this produces the static PNG the README links to. To explore the full model
interactively instead, run ``netron gpt2.onnx`` (or drag the file into netron.app).

Dependencies (heavy; needed only to *regenerate* the committed PNG):
    pip install torch onnx netron playwright pillow
    playwright install chromium

Usage:
    LLMC_PATH=/path/to/llm.c python build_gpt2_netron.py
"""

import os
import time


def build_logits_only(model: "object") -> "object":
    """
    Wrap llm.c's GPT so ONNX export emits a single full-sequence logits output.

    Args:
        model: An instantiated llm.c ``GPT`` module.

    Returns:
        An ``nn.Module`` whose ``forward(idx)`` returns only the logits tensor.
    """
    import torch.nn as nn

    class LogitsOnly(nn.Module):
        def __init__(self, inner: nn.Module) -> None:
            super().__init__()
            self.inner = inner

        def forward(self, idx):  # type: ignore[no-untyped-def]
            logits, _ = self.inner(idx, targets=idx, return_logits=True)
            return logits

    return LogitsOnly(model)


def export_graph(llmc_path: str, out_path: str, n_layer: int = 3, seq_len: int = 8) -> str:
    """
    Export llm.c's GPT module to a graph-only ONNX file.

    Weights are dropped (``export_params=False``) because Netron renders the
    architecture, not weight values - this keeps the file tiny and fast to lay out.
    A reduced ``n_layer`` keeps the graph legible; every block is identical to the
    full 12-layer GPT-2.

    Args:
        llmc_path: Path to a llm.c checkout containing ``train_gpt2.py``.
        out_path: Destination ``.onnx`` path.
        n_layer: Number of transformer blocks to emit (default: 3).
        seq_len: Dummy sequence length for the trace (default: 8).

    Returns:
        The ``out_path`` that was written.
    """
    import sys

    import torch

    sys.path.insert(0, llmc_path)
    from train_gpt2 import GPT, GPTConfig

    config = GPTConfig(block_size=seq_len, vocab_size=50257, n_layer=n_layer, n_head=12, n_embd=768)
    model = build_logits_only(GPT(config)).eval()
    idx = torch.zeros((1, seq_len), dtype=torch.long)
    torch.onnx.export(
        model,
        (idx,),
        out_path,
        input_names=["input_ids"],
        output_names=["logits"],
        opset_version=17,
        dynamo=False,
        export_params=False,
        do_constant_folding=True,
    )
    return out_path


def screenshot_graph(onnx_path: str, out_png: str, width: int = 1500, height: int = 5200) -> str:
    """
    Serve an ONNX file in Netron and capture the rendered graph with headless Chromium.

    Waits for the graph nodes to actually paint (Netron lays out via a web worker
    and disables ``window.eval``, so a CSS-selector wait is used, not script eval).

    Args:
        onnx_path: ONNX file to visualize.
        out_png: Destination screenshot path.
        width: Browser viewport width.
        height: Browser viewport height (tall, to capture the full column).

    Returns:
        The ``out_png`` that was written.
    """
    import netron
    from playwright.sync_api import sync_playwright

    address = netron.start(onnx_path, address=("127.0.0.1", 8131), browse=False)
    url = f"http://{address[0]}:{address[1]}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector("g.node, .node", state="attached", timeout=60000)
            time.sleep(4)
            page.screenshot(path=out_png, full_page=True)
            browser.close()
    finally:
        netron.stop()
    return out_png


def crop_architecture(full_png: str, out_png: str, target_width: int = 1600, top_height: int = 3400) -> str:
    """
    Trim whitespace and crop the top region (embeddings + first block) for legibility.

    Args:
        full_png: The full-graph screenshot.
        out_png: Destination cropped/resized PNG.
        target_width: Output width in pixels.
        top_height: Height of the top region to keep, in source pixels.

    Returns:
        The ``out_png`` that was written.
    """
    from PIL import Image, ImageChops

    image = Image.open(full_png).convert("RGB")
    background = Image.new("RGB", image.size, (255, 255, 255))
    bbox = ImageChops.difference(image, background).getbbox()
    trimmed = image.crop((max(0, bbox[0] - 30), bbox[1], min(image.size[0], bbox[2] + 30), bbox[3]))
    top = trimmed.crop((0, 0, trimmed.size[0], min(trimmed.size[1], top_height)))
    scale = target_width / top.size[0]
    final = top.resize((target_width, int(top.size[1] * scale)), Image.LANCZOS)
    final.save(out_png, optimize=True)
    return out_png


def main() -> None:
    llmc_path = os.environ.get("LLMC_PATH", "/home/hang/llm.c")
    here = os.path.dirname(os.path.abspath(__file__))
    onnx_path = os.path.join(here, "gpt2.onnx")
    full_png = os.path.join(here, "gpt2_netron_full.png")
    out_png = os.path.join(here, "figures", "gpt2_netron.png")

    export_graph(llmc_path, onnx_path)
    screenshot_graph(onnx_path, full_png)
    crop_architecture(full_png, out_png)
    print(f"wrote {out_png}")


if __name__ == "__main__":
    main()
