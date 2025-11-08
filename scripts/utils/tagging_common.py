# -*- coding: utf-8 -*-
"""
Shared helpers for tagging/annotation ingestion.

- Normalizes tag strings (lowercase, underscores → spaces handled later in captioning).
- Provides small utilities for confidence handling and merging.
"""

from __future__ import annotations

def norm_tag(tag: str) -> str:
    """Normalize tag into a canonical 'snake' form for merging."""
    return tag.strip().lower().replace(" ", "_")
