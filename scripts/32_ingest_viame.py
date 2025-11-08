# -*- coding: utf-8 -*-
"""
Ingest VIAME CSV/kw18-like exports into JSONL.

- We map class/attributes into simple string tags.
"""

from __future__ import annotations
from pathlib import Path
import argparse, csv, ujson
from scripts.utils.paths import load_config, paths
from scripts.utils.tagging_common import norm_tag

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True, help="Path to VIAME CSV")
    args = ap.parse_args()

    cfg = load_config()
    p = paths(cfg)
    out = p["tags_raw"] / "viame.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(args.export, "r", encoding="utf-8") as f, out.open("w", encoding="utf-8") as fout:
        rd = csv.DictReader(f)
        for row in rd:
            image = row.get("image") or row.get("filename") or ""
            if not image:
                continue
            raw = [row.get("class"), row.get("attributes")]
            tags = []
            for s in raw:
                if not s: 
                    continue
                for tok in s.replace(";", ",").split(","):
                    t = norm_tag(tok)
                    if t:
                        tags.append([t, 0.95])
            ujson.dump({"image": image, "tags": tags}, fout)
            fout.write("\n")
    print(f"[viame] wrote: {out}")

if __name__ == "__main__":
    main()
