# -*- coding: utf-8 -*-
"""
Caption rule-set used to convert merged (tag, score) lists into a final caption line.

- De-duplicate
- Order by score/frequency (already done in merge stage; here we limit and reformat)
- Optionally strip NSFW-like tags
- Prepend activation keyword from config
"""

from __future__ import annotations
from typing import Iterable, Tuple, List, Set

NSFB = {"rating_explicit", "nsfw", "censored"}  # extend per policy

def to_caption(
    tags: Iterable[Tuple[str, float]],
    *,
    lower: bool = True,
    replace_underscores: bool = True,
    strip_nsfb: bool = True,
    max_tags: int = 64,
    prefix: str = ""
) -> str:
    seen: Set[str] = set()
    ordered: List[str] = []
    for t, _s in tags:
        tag = t.strip()
        if not tag:
            continue
        if strip_nsfb and tag in NSFB:
            continue
        if lower:
            tag = tag.lower()
        if replace_underscores:
            tag = tag.replace("_", " ")
        if tag in seen:
            continue
        seen.add(tag)
        ordered.append(tag)
        if len(ordered) >= max_tags:
            break
    return f"{prefix}, " + ", ".join(ordered) if prefix else ", ".join(ordered)
