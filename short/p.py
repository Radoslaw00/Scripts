#!/usr/bin/env python3
# -*- coding: cp1250 -*-
"""
Auto-converts all image files in the same folder to WebP format.
No user prompts - fully automated.
"""
import sys
import os
from pathlib import Path

try:
    from PIL import Image
except Exception:
    print("Pillow not installed. Install: pip install pillow")
    sys.exit(1)

TARGET_FORMAT = "webp"


def convert_file(path: Path, target_ext: str) -> bool:
    try:
        with Image.open(path) as img:
            # Skip if already in target extension
            if path.suffix.lower() == f'.{target_ext}':
                return False
            target_path = path.with_suffix(f'.{target_ext}')

            # JPEG/JPG doesn't support alpha channel
            if target_ext in ("jpg", "jpeg") and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            save_params = {}
            fmt = target_ext.upper()
            if fmt == 'JPG':
                fmt = 'JPEG'
            if fmt == 'WEBP':
                save_params['quality'] = 90

            img.save(target_path, fmt, **save_params)
            print(f"Converted: {path.name} -> {target_path.name}")
            return True
    except Exception as e:
        print(f"Error converting {path.name}: {e}")
        return False


def main():
    folder = Path(__file__).resolve().parent
    files = [p for p in folder.iterdir() if p.is_file() and p.name != Path(__file__).name]

    if not files:
        print("No files to process in the folder.")
        return

    converted = 0
    skipped = 0
    for f in files:
        # attempt to open with PIL to detect image files
        try:
            with Image.open(f):
                pass
        except Exception:
            # not an image – skip
            skipped += 1
            continue

        if convert_file(f, TARGET_FORMAT):
            converted += 1
        else:
            skipped += 1

    print(f"\nDone! Converted: {converted}. Skipped: {skipped}.")


if __name__ == '__main__':
    main()