from pathlib import Path
import subprocess, yaml

ROOT = Path(__file__).resolve().parents[1]
CFG  = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))

IN_DIR  = ROOT / CFG["paths"].get("split_clips_dir", "data/clips_5s")
OUT_DIR = ROOT / CFG["paths"].get("upscaled_256_dir", "data/upscaled_256")

FPS  = int(CFG.get("video", {}).get("fps", 60))     # <- 60 fps
SIZE = int(CFG.get("video", {}).get("upscale_size", 256))

# Keep aspect ratio, then pad to 256x256; output is locked to 60 fps.
VF = (
    f"fps={FPS},"
    f"scale={SIZE}:{SIZE}:flags=lanczos:force_original_aspect_ratio=decrease,"
    f"pad={SIZE}:{SIZE}:(ow-iw)/2:(oh-ih)/2:black"
)

def transcode(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src),
        "-an",
        "-vf", VF,
        "-r", str(FPS),                         # enforce 60 fps timebase on output
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(dst),
    ]
    subprocess.run(cmd, check=True)

def main():
    if not IN_DIR.exists():
        print(f"[upscale] Input folder not found: {IN_DIR}")
        return 2
    for video_dir in sorted([p for p in IN_DIR.iterdir() if p.is_dir()]):
        out_dir = OUT_DIR / video_dir.name
        for clip in sorted(video_dir.glob("clip_*.mp4")):
            out_path = out_dir / clip.name
            print(f"[upscale] {clip} → {out_path}")
            transcode(clip, out_path)
    print("[upscale] Done.")

if __name__ == "__main__":
    main()
