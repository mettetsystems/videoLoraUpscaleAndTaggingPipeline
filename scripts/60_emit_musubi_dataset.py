# -*- coding: utf-8 -*-
"""
Emit a Musubi‑Tuner dataset for WAN 2.1 training:
- Copies frames to dataset/images/<video_id>/
- Writes captions.txt with "<relpath>\\t<caption>" lines
"""

from __future__ import annotations
from pathlib import Path
import shutil, ujson
from scripts.utils.paths import load_config, paths

def main():
    cfg = load_config()
    p = paths(cfg)
    out_root = p["musubi_root"]

    img_root = out_root / "images"
    out_root.mkdir(parents=True, exist_ok=True)
    img_root.mkdir(parents=True, exist_ok=True)

    # Copy frames preserving subfolders
    for frame in (p["frames_root"]).glob("*/*.jpg"):
        rel_dir = frame.parent.name
        dst_dir = img_root / rel_dir
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / frame.name
        if not dst.exists():
            shutil.copy2(frame, dst)

    # Build captions.txt
    cap_map = {}
    with open(p["captions_clean"], "r", encoding="utf-8") as f:
        for line in f:
            row = ujson.loads(line)
            src = Path(row["image"])
            rel_dir = src.parent.name
            rel = Path("images") / rel_dir / src.name
            cap_map[str(rel).replace("\\", "/")] = row["caption"]

    with open(out_root / "captions.txt", "w", encoding="utf-8") as f:
        for rel, cap in sorted(cap_map.items()):
            f.write(f"{rel}\t{cap}\n")

    print(f"[musubi] dataset ready at: {out_root}")

if __name__ == "__main__":
    main()
