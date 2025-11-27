#!/usr/bin/env python3
"""
Smart Quality Upscale Pre-pass
- Scans images for quality using simple no-ref metrics
- Selects low-quality candidates
- Smart scaling: >=500x500 get scale 1 (AI enhancement only), <500x500 get scale 2 (AI enhancement + 2x upscale)
- Writes a JSON report/manifest and can build a merged input directory that prefers upscaled outputs

Usage (example):
  python3 quality_upscale_smart.py \
    --input input_images \
    --output-upscaled upscaled_raw \
    --report quality_report.json \
    --model upscayl-standard-4x \
    --min-dim 500 --laplacian-thresh 150 \
    --max-workers 1 --limit 10 --output-format jpg \
    --threads 2:4:2 --tile-size 0

Notes:
- OpenCV (cv2) is optional. If not available, the script falls back to size-only heuristic.
- Upscayl CLI can be either 'upscayl-ncnn' (long flags) or the macOS app's 'upscayl-bin' (short flags).
"""

import argparse
import json
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image
from tqdm import tqdm

try:
    import cv2  # type: ignore
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


def list_images(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            files.append(p)
    return sorted(files)


def variance_of_laplacian(pil_img: Image.Image) -> Optional[float]:
    if not HAS_CV2:
        return None
    try:
        gray = np.array(pil_img.convert("L"))
        lap = cv2.Laplacian(gray, cv2.CV_64F, ksize=3)
        return float(lap.var())
    except Exception:
        return None


def compute_metrics(img_path: Path) -> Dict:
    with Image.open(img_path) as im:
        width, height = im.size
        vol = variance_of_laplacian(im)
        return {
            "width": width,
            "height": height,
            "min_dim": min(width, height),
            "laplacian_var": vol,
        }


def decide_candidate(metrics: Dict, min_dim_thresh: int, lap_thresh: Optional[float]) -> bool:
    # Always select low-quality images for AI enhancement
    if metrics["min_dim"] < min_dim_thresh:
        return True
    if lap_thresh is not None and metrics.get("laplacian_var") is not None:
        return metrics["laplacian_var"] < lap_thresh
    return False


def get_smart_scale(metrics: Dict) -> int:
    """Determine scale based on image dimensions:
    - >= 500x500: scale 1 (AI enhancement only)
    - < 500x500: scale 2 (AI enhancement + 2x upscale)
    """
    if metrics["min_dim"] >= 500:
        return 1  # AI enhancement only
    else:
        return 2  # AI enhancement + 2x upscale


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def upscale_with_upscayl(upscayl_bin: str, model_path: Optional[str], in_path: Path, out_path: Path, model: str, scale: int, output_format: str, extra_args: List[str]) -> Tuple[bool, str]:
    ensure_dir(out_path.parent)
    try:
        if "upscayl-bin" in os.path.basename(upscayl_bin):
            # macOS packaged CLI short flags
            cmd = [
                upscayl_bin,
                "-i", str(in_path),
                "-o", str(out_path),
                "-s", str(scale),
                "-n", model,
                "-f", output_format,
                "-g", "0",  # GPU acceleration
                "-j", "2:4:2",  # threads
                "-t", "0",  # tile size
            ]
            if model_path:
                cmd += ["-m", model_path]
        else:
            # generic ncnn CLI (long flags)
            cmd = [
                upscayl_bin,
                "--input", str(in_path),
                "--output", str(out_path),
                "--model", model,
                "--scale", str(scale),
            ]
            # not all builds support format flag; keep output_path extension authoritative
        cmd += extra_args
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        ok = res.returncode == 0 and out_path.exists()
        msg = res.stderr.decode("utf-8", errors="ignore") if res.stderr else res.stdout.decode("utf-8", errors="ignore")
        return ok, msg.strip()
    except FileNotFoundError:
        return False, f"Upscayl binary not found: {upscayl_bin}"
    except Exception as e:
        return False, str(e)


def build_merged_input(original_root: Path, upscaled_root: Path, merged_root: Path) -> Dict[str, int]:
    stats = {"linked_upscaled": 0, "linked_original": 0}
    if merged_root.exists():
        shutil.rmtree(merged_root)
    ensure_dir(merged_root)

    orig_files = list_images(original_root)
    for of in tqdm(orig_files, desc="Building merged input"):
        rel = of.relative_to(original_root)
        up = (upscaled_root / rel).with_suffix(".png") if of.suffix.lower() == ".png" else (upscaled_root / rel)
        target = None
        if up.exists():
            target = up
        else:
            alt1 = up.with_suffix(".jpg")
            alt2 = up.with_suffix(".png")
            if alt1.exists():
                target = alt1
            elif alt2.exists():
                target = alt2
        link_src = target if target is not None else of
        link_dst = merged_root / rel
        ensure_dir(link_dst.parent)
        try:
            if link_dst.exists() or link_dst.is_symlink():
                link_dst.unlink()
            os.symlink(link_src, link_dst)
            if target is not None:
                stats["linked_upscaled"] += 1
            else:
                stats["linked_original"] += 1
        except OSError:
            shutil.copy2(link_src, link_dst)
            if target is not None:
                stats["linked_upscaled"] += 1
            else:
                stats["linked_original"] += 1
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Smart Quality pre-pass with intelligent scaling")
    parser.add_argument("--input", default="input_images", help="Root folder with images to scan")
    parser.add_argument("--output-upscaled", default="upscaled_raw", help="Where to write upscaled images")
    parser.add_argument("--report", default="quality_report.json", help="Path to JSON report")
    parser.add_argument("--model", default="upscayl-standard-4x", help="Upscayl model name (e.g., upscayl-standard-4x)")
    parser.add_argument("--model-path", default="/Applications/Upscayl.app/Contents/Resources/models", help="Path to Upscayl models directory")
    parser.add_argument("--upscayl-bin", default="/Applications/Upscayl.app/Contents/Resources/bin/upscayl-bin", help="Upscayl CLI binary name/path")
    parser.add_argument("--extra-args", default="", help="Extra args for Upscayl CLI, raw string")
    parser.add_argument("--min-dim", type=int, default=500, help="Min shorter side to avoid upscale")
    parser.add_argument("--laplacian-thresh", type=float, default=150.0, help="Variance of Laplacian threshold; lower is blurrier")
    parser.add_argument("--max-workers", type=int, default=1, help="Parallel upscales (be mindful of GPU)")
    parser.add_argument("--limit", type=int, default=0, help="Process only first N candidates (0 = all)")
    parser.add_argument("--output-format", default="jpg", choices=["jpg", "png", "webp"], help="Output image format for upscaled files")
    parser.add_argument("--dry-run", action="store_true", help="Only generate report, do not call Upscayl")
    parser.add_argument("--merged-input", default="", help="Optional: build merged input dir that prefers upscaled files")

    args = parser.parse_args()

    input_root = Path(args.input)
    out_root = Path(args.output_upscaled)
    ensure_dir(out_root)

    files = list_images(input_root)
    if not files:
        print(f"No images found in: {input_root}")
        return

    report: Dict = {
        "total": len(files),
        "scanned_root": str(input_root),
        "upscaled_root": str(out_root),
        "settings": {
            "model": args.model,
            "model_path": args.model_path,
            "min_dim": args.min_dim,
            "laplacian_thresh": args.laplacian_thresh,
            "upscayl_bin": args.upscayl_bin,
            "has_cv2": HAS_CV2,
            "output_format": args.output_format,
            "limit": args.limit,
        },
        "items": [],
        "summary": {},
        "errors": [],
        "missing_cli": False,
    }

    candidates: List[Tuple[Path, Dict, int]] = []  # (path, metrics, scale)
    for p in tqdm(files, desc="Scanning quality"):
        try:
            metrics = compute_metrics(p)
            need = decide_candidate(metrics, args.min_dim, args.laplacian_thresh if HAS_CV2 else None)
            scale = get_smart_scale(metrics) if need else 0
            report["items"].append({
                "path": str(p),
                "metrics": metrics,
                "selected": need,
                "scale": scale,
            })
            if need:
                candidates.append((p, metrics, scale))
        except Exception as e:
            report["errors"].append(f"{p}: {e}")

    print(f"Candidates for upscale: {len(candidates)}/{len(files)}")
    
    # Group by scale for reporting
    scale_1_count = sum(1 for _, _, scale in candidates if scale == 1)
    scale_2_count = sum(1 for _, _, scale in candidates if scale == 2)
    print(f"  - Scale 1 (AI enhancement only): {scale_1_count}")
    print(f"  - Scale 2 (AI enhancement + 2x upscale): {scale_2_count}")

    selected_cands = candidates[: args.limit] if args.limit and args.limit > 0 else candidates

    upscayl_bin = shutil.which(args.upscayl_bin) or args.upscayl_bin
    if not (shutil.which(args.upscayl_bin) or Path(args.upscayl_bin).exists()):
        report["missing_cli"] = True
        print(f"Warning: Upscayl CLI '{args.upscayl_bin}' not found in PATH. You can still use --dry-run to produce the report.")

    processed, failed = 0, 0
    if not args.dry_run and (shutil.which(args.upscayl_bin) or Path(args.upscayl_bin).exists()):
        extra = [s for s in args.extra_args.split(" ") if s]
        
        # Per-file processing with smart scaling
        def task(item: Tuple[Path, Dict, int]) -> Tuple[Path, bool, str, Path]:
            in_path, metrics, scale = item
            rel = in_path.relative_to(input_root)
            out_path = (out_root / rel).with_suffix(f".{args.output_format}")
            ok, msg = upscale_with_upscayl(upscayl_bin, args.model_path, in_path, out_path, args.model, scale, args.output_format, extra)
            return (in_path, ok, msg, out_path)

        with ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as ex:
            futures = [ex.submit(task, it) for it in selected_cands]
            for fut in tqdm(as_completed(futures), total=len(futures), desc="Smart upscaling"):
                in_path, ok, msg, out_path = fut.result()
                if ok:
                    processed += 1
                else:
                    failed += 1
                    report["errors"].append(f"{in_path}: {msg}")
    
    report["summary"] = {
        "candidates": len(candidates),
        "selected": len(selected_cands),
        "scale_1_count": scale_1_count,
        "scale_2_count": scale_2_count,
        "upscaled_ok": processed,
        "upscaled_failed": failed,
    }

    if args.merged_input:
        stats = build_merged_input(input_root, out_root, Path(args.merged_input))
        report["merged_input"] = {"path": args.merged_input, **stats}

    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Report saved to: {args.report}")
    if args.merged_input:
        print(f"Merged input built at: {args.merged_input}")


if __name__ == "__main__":
    main()
