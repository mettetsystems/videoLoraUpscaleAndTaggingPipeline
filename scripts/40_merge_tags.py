# -*- coding: utf-8 -*-
"""
Merge tag sources into a single JSONL with confidence-aware de-duplication.

- For each image: keep the highest confidence per tag.
- Tie-break with source frequency (tags seen from multiple tools rank higher).
"""

from __future__ import annotations
from pathlib import Path
import ujson, glob
from collections import defaultdict, Counter
from scripts.utils.paths import load_config, paths

def main():
    cfg = load_config()
    p = paths(cfg)
    min_conf = float(cfg["merge"]["min_confidence"])

    merged = defaultdict(lambda: {"tags": {}, "counts": Counter()})

    for src in glob.glob(str(p["tags_raw"] / "*.jsonl")):
        src_name = Path(src).stem
        with open(src, "r", encoding="utf-8") as f:
            for line in f:
                row = ujson.loads(line)
                img = row["image"]
                for tag, score in row["tags"]:
                    if score < min_conf:
                        continue
                    t = tag.strip().lower().replace(" ", "_")
                    cur = merged[img]["tags"].get(t, 0.0)
                    if score > cur:
                        merged[img]["tags"][t] = score
                    merged[img]["counts"][t] += 1

    outp = p["tags_merged"]
    with open(outp, "w", encoding="utf-8") as f:
        for img, d in merged.items():
            tags = sorted(d["tags"].items(), key=lambda x: (-x[1], -d["counts"][x[0]], x[0]))
            ujson.dump({"image": img, "tags": tags}, f)
            f.write("\n")
    print(f"[merge] wrote: {outp}")

if __name__ == "__main__":
    main()
