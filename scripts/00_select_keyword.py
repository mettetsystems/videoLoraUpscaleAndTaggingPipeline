# -*- coding: utf-8 -*-
"""
Prompt once for the LoRA activation keyword and persist it in config.yaml.

- Stored under musubi.caption_prefix
- Applied later in 50_clean_optimize.py
"""

from __future__ import annotations
from pathlib import Path
import yaml

CFG = Path("config.yaml")

def main() -> None:
    key = input("Enter activation keyword (e.g., trueroots-style): ").strip()
    if not key:
        print("No keyword provided; nothing changed.")
        return
    with CFG.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg.setdefault("musubi", {})
    cfg["musubi"]["caption_prefix"] = key
    with CFG.open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)
    print(f"Saved activation keyword: {key}")

if __name__ == "__main__":
    main()
