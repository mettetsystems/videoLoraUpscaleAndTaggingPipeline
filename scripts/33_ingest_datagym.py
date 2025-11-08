# -*- coding: utf-8 -*-
"""
Ingest datagym-core JSON exports into JSONL.
"""

from __future__ import annotations
from pathlib import Path
import argparse, json, ujson
from scripts.utils.paths import load_config, paths
from scripts.utils.tagging_common import norm_tag

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True, help="Path to datagym-core JSON export")
    args = ap.parse_args()

    cfg = load_config()
    p = paths(cfg)
    out = p["tags_raw"] / "datagym.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(Path(args.export).read_text(encoding="utf-8"))
    with out.open("w", encoding="utf-8") as f:
        for item in data:
            image = item.get("image") or item.get("filename")
            if not image:
                continue
            tags = []
            for t in item.get("labels", []):
                tag = norm_tag(str(t))
                if tag:
                    tags.append([tag, 0.97])
            ujson.dump({"image": image, "tags": tags}, f)
            f.write("\n")
    print(f"[datagym] wrote: {out}")

if __name__ == "__main__":
    main()
