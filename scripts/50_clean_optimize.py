# -*- coding: utf-8 -*-
"""
Create cleaned captions from merged tags and prepend activation keyword.
"""

from __future__ import annotations
from scripts.utils.paths import load_config, paths
from scripts.utils.caption_rules import to_caption
import ujson

def main():
    cfg = load_config()
    p = paths(cfg)
    with open(p["tags_merged"], "r", encoding="utf-8") as fin, \
         open(p["captions_clean"], "w", encoding="utf-8") as fout:
        for line in fin:
            row = ujson.loads(line)
            tags = row["tags"]
            cap = to_caption(
                tags,
                lower=bool(cfg["clean"]["lowercase"]),
                replace_underscores=bool(cfg["clean"]["replace_underscores"]),
                strip_nsfb=bool(cfg["clean"]["strip_nsfb_tags"]),
                max_tags=int(cfg["clean"]["max_tags"]),
                prefix=cfg["musubi"].get("caption_prefix", "")
            )
            ujson.dump({"image": row["image"], "caption": cap}, fout)
            fout.write("\n")
    print(f"[clean] wrote: {p['captions_clean']}")

if __name__ == "__main__":
    main()
