"""
SortEverything.py

Creates folders for common photo and video file extensions and sorts files
into those folders based on extension.

Usage:
	python SortEverything.py [target_dir] [--recursive] [--copy] [--dry-run]

Examples:
	python SortEverything.py . --recursive --dry-run
	python SortEverything.py "C:/Users/radoslaw/Desktop/ToSort"

The script uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import os
import shutil
from collections import defaultdict
from typing import Iterable


# Common image/photo and video extensions (lowercase, without dot)
PHOTO_EXTS = {
	"jpg",
	"jpeg",
	"png",
	"gif",
	"bmp",
	"tif",
	"tiff",
	"heic",
	"heif",
	"raw",
	"cr2",
	"nef",
	"arw",
	"orf",
	"dng",
	"webp",
	"psd",
	"svg",
}

VIDEO_EXTS = {
	"mp4",
	"mov",
	"avi",
	"mkv",
	"wmv",
	"mpeg",
	"mpg",
	"m4v",
	"flv",
	"webm",
	"3gp",
	"mts",
	"m2ts",
}

ALL_KNOWN_EXTS = PHOTO_EXTS | VIDEO_EXTS


def ensure_dir(path: str) -> None:
	if not os.path.exists(path):
		os.makedirs(path, exist_ok=True)


def unique_path(path: str) -> str:
	"""If `path` exists, return a new path with a numeric suffix to avoid collision."""
	base, ext = os.path.splitext(path)
	counter = 1
	candidate = path
	while os.path.exists(candidate):
		candidate = f"{base}_{counter}{ext}"
		counter += 1
	return candidate


def iter_files(target_dir: str, recursive: bool) -> Iterable[str]:
	if recursive:
		for root, dirs, files in os.walk(target_dir):
			# skip the extension-folders we create (they are direct children of target_dir)
			# but still allow deeper folders if user desires.
			for f in files:
				yield os.path.join(root, f)
	else:
		for entry in os.listdir(target_dir):
			path = os.path.join(target_dir, entry)
			if os.path.isfile(path):
				yield path


def sort_files(target_dir: str, recursive: bool = False, do_copy: bool = False, dry_run: bool = False) -> dict:
	"""Sort files in `target_dir` into folders named by extension.

	Returns a dict mapping extension -> count moved/copied.
	"""
	counts = defaultdict(int)
	target_dir = os.path.abspath(target_dir)

	for filepath in iter_files(target_dir, recursive):
		# skip files inside the extension folders to avoid infinite loop
		rel = os.path.relpath(filepath, target_dir)
		parts = rel.split(os.sep)
		if parts and parts[0].lower() in ALL_KNOWN_EXTS:
			continue

		_, ext = os.path.splitext(filepath)
		if not ext:
			continue
		ext = ext.lstrip(".").lower()
		if ext in ALL_KNOWN_EXTS:
			dest_folder = os.path.join(target_dir, ext)
			ensure_dir(dest_folder)
			dest_path = os.path.join(dest_folder, os.path.basename(filepath))
			dest_path = unique_path(dest_path)

			if dry_run:
				action = "copy" if do_copy else "move"
				print(f"[DRY-RUN] {action}: '{filepath}' -> '{dest_path}'")
			else:
				if do_copy:
					shutil.copy2(filepath, dest_path)
				else:
					shutil.move(filepath, dest_path)

			counts[ext] += 1

	return dict(counts)


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Sort photo and video files into extension folders.")
	p.add_argument("target", nargs="?", default=".", help="Target directory to sort (default: current dir)")
	p.add_argument("--recursive", "-r", action="store_true", help="Recursively process subdirectories")
	p.add_argument("--copy", action="store_true", help="Copy files instead of moving")
	p.add_argument("--dry-run", action="store_true", help="Show what would be done without changing files")
	return p.parse_args()


def main() -> None:
	args = parse_args()
	target = args.target
	if not os.path.isdir(target):
		print(f"Target is not a directory: {target}")
		return

	print(f"Sorting files in: {os.path.abspath(target)}")
	if args.dry_run:
		print("Dry-run mode: no files will be moved or copied.")

	counts = sort_files(target, recursive=args.recursive, do_copy=args.copy, dry_run=args.dry_run)

	total = sum(counts.values())
	print("\nSummary:")
	print(f"  Total files processed: {total}")
	for ext, cnt in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
		print(f"  {ext}: {cnt}")


if __name__ == "__main__":
	main()

