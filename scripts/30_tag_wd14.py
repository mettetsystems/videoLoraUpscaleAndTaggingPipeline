# -*- coding: utf-8 -*-
"""
Run WD14 (ONNX) over extracted frames to produce automatic tags.

- This file includes a STUB inference function to keep the repo runnable end-to-end.
- Replace `dummy_wd14_infer` with a real onnxruntime session using your preferred WD14 model(s).
- Output: data/tags_raw/wd14.jsonl  with rows: {"image": str, "tags": [["tag", score], ...]}
"""

from __future__ import annotations
from pathlib import Path
import ujson
from tqdm import tqdm
from scripts.utils.paths import load_config, paths

def dummy_wd14_infer(image_path: Path):
    """
    Placeholder that returns a few generic tags with confidences.
    Swap in real ONNX inference:
      - import onnxruntime as ort
      - session = ort.InferenceSession('models/wd14/<model>.onnx', providers=['CUDAExecutionProvider'])
      - preprocess image -> input tensor
      - outputs -> decode -> list[(tag, score)]
    """
    return [("outdoor", 0.92), ("landscape", 0.88), ("tree", 0.81)]

def main():
    cfg = load_config()
    p = paths(cfg)
    out = p["tags_raw"] / "wd14.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    images = sorted(Path(p["frames_root"]).glob("*/*.jpg"))
    with out.open("w", encoding="utf-8") as f:
        for img in tqdm(images, desc="WD14 tagging (stub)"):
            tags = dummy_wd14_infer(img)
            ujson.dump({"image": str(img), "tags": tags}, f)
            f.write("\n")
    print(f"[wd14] wrote: {out}")

if __name__ == "__main__":
    main()
