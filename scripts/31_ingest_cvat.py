# -*- coding: utf-8 -*-
"""
Ingest CVAT exports and convert into our unified JSONL format.

Usage:
  python scripts/31_ingest_cvat.py --export exporters_examples/cvat_export_example.zip --format cvat

Notes:
  - Adjust `parse_cvat_zip` to match your chosen export format (CVAT XML, COCO, etc.).
  - We expect to produce lines: {"image": "<rel or abs path>", "tags": [["tag", 0.99], ...]}
"""

from __future__ import annotations
from pathlib import Path
import argparse, zipfile, json, ujson
from scripts.utils.paths import load_config, paths

def parse_cvat_zip(zp: Path):
    """Return mapping image_path -> set(tags). This is a minimal demo parser for a captions.json inside the zip."""
    tags_by_image = {}
    with zipfile.ZipFile(zp, "r") as zf:
        for name in zf.namelist():
            if name.endswith("captions.json"):
                data = json.loads(zf.read(name).decode("utf-8"))
                for rec in data:
                    tags_by_image.setdefault(rec["image"], set()).update(rec["tags"])
    return tags_by_image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True, help="Path to CVAT export .zip")
    ap.add_argument("--format", default="cvat")
    args = ap.parse_args()

    cfg = load_config()
    p = paths(cfg)
    out = p["tags_raw"] / "cvat.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    mapping = parse_cvat_zip(Path(args.export))
    with out.open("w", encoding="utf-8") as f:
        for img, tags in mapping.items():
            ujson.dump({"image": img, "tags": [[t, 0.99] for t in sorted(tags)]}, f)
            f.write("\n")
    print(f"[cvat] wrote: {out}")

if __name__ == "__main__":
    main()
