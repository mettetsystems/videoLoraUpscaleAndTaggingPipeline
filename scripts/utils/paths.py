# -*- coding: utf-8 -*-
"""
Utility helpers for resolving paths used across the pipeline.

- Centralizes path handling and config loading.
- Creates working directories on demand, so downstream scripts can assume they exist.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import yaml

def load_config(cfg_path: Path = Path("config.yaml")) -> Dict[str, Any]:
    """Load YAML config once; downstream scripts import this to keep behavior consistent."""
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_dir(p: Path) -> Path:
    """Create directory if missing and return it for chaining."""
    p.mkdir(parents=True, exist_ok=True)
    return p

def paths(cfg: Dict[str, Any]) -> Dict[str, Path]:
    """Compute canonical working paths used across the pipeline."""
    work_root = Path(cfg["paths"]["work_root"]).resolve()
    p = {
        "input_videos": Path(cfg["paths"]["input_videos"]).resolve(),
        "work_root": work_root,
        "normalized_videos": ensure_dir(work_root / "normalized_videos"),
        "frames_root": ensure_dir(work_root / "frames"),
        "tags_raw": ensure_dir(work_root / "tags_raw"),
        "tags_merged_dir": ensure_dir(work_root / "tags_merged"),
        "tags_merged": ensure_dir(work_root / "tags_merged") / "merged.jsonl",
        "captions_clean": work_root / "captions_clean.jsonl",

        "musubi_root": ensure_dir(Path(cfg["musubi"]["dataset_root"]).resolve()),
    }
    return p
