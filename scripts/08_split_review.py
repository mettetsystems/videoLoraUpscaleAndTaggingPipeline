"""
Split review videos into <=5s clips at a fixed 60 fps for smooth, uniform training samples.
- Re-encodes with keyframes every 5s so each segment boundary is clean.
- Produces data/clips_5s/<video>/clip_0001.mp4, clip_0002.mp4, ...
"""
import subprocess, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG  = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))

IN_DIR  = ROOT / CFG["paths"].get("input_videos_dir", "data/input_videos")
OUT_DIR = ROOT / CFG["paths"].get("split_clips_dir",  "data/clips_5s")

MAX_SEC    = int(CFG.get("video", {}).get("clip_max_seconds", 5))
TARGET_FPS = int(CFG.get("video", {}).get("fps", 60))     # <- 60 fps
FAST_COPY  = bool(CFG.get("video", {}).get("split_fast_copy", False))

def split_video(src: Path, dst_dir: Path) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    out_pattern = str(dst_dir / "clip_%04d.mp4")

    if FAST_COPY:
        # Fast copy (no re-encode). Keeps source fps; not recommended when enforcing 60 fps globally.
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(src),
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", str(MAX_SEC),
            "-reset_timestamps", "1",
            out_pattern,
        ]
    else:
        # Re-encode at 60 fps and force keyframes every 5 seconds.
        gop = max(1, TARGET_FPS * MAX_SEC)        # 60 * 5 = 300
        force_kf = f"expr:gte(t,n_forced*{MAX_SEC})"
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(src),
            "-an",
            "-r", str(TARGET_FPS),                 # normalize to 60 fps here
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-g", str(gop), "-keyint_min", str(gop), "-sc_threshold", "0",
            "-force_key_frames", force_kf,
            "-f", "segment", "-segment_time", str(MAX_SEC),
            "-reset_timestamps", "1",
            "-movflags", "+faststart",
            out_pattern,
        ]

    subprocess.run(cmd, check=True)

def main() -> int:
    if not IN_DIR.exists():
        print(f"[split] Input folder not found: {IN_DIR}", file=sys.stderr)
        return 2
    videos = [p for p in IN_DIR.iterdir() if p.is_file()]
    if not videos:
        print(f"[split] No files in {IN_DIR}")
        return 0
    for src in videos:
        base = src.stem
        dst  = OUT_DIR / base
        print(f"[split] {src.name} → {dst}")
        split_video(src, dst)
    print("[split] Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
