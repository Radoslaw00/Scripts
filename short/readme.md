# Image Batch Processor

Automated image processing tool that converts, resizes, optimizes, and organizes images - all with a single click.

## Features

- **Convert to WebP**: All images automatically converted to WebP format (90% quality)
- **Auto-Resize**: Detects image dimensions and intelligently resizes to 1000px max width while maintaining aspect ratio
- **Optimize**: Reduces file size without quality loss (75% quality for WebP, optimized compression for others)
- **Organize by Type**: Files automatically sorted into folders by extension (WEBP, PNG, JPG, etc.)
- **Preserve Originals**: All original files kept intact
- **Quick Access**: Shortcuts created for optimized files

## File Structure

```
Your Folder/
├── x.bat (Run this to start)
├── run.py (Processing engine)
├── WEBP/
│   ├── original_image.webp (original)
│   └── RESIZED/
│       ├── original_image.webp (resized 1000px)
│       └── OPTIMIZED/
│           └── original_image.webp (optimized, smaller file)
├── JPG/
│   ├── original.jpg (original)
│   └── RESIZED/
│       ├── original.jpg (resized)
│       └── OPTIMIZED/
│           └── original.jpg (optimized)
└── OPTIMIZED & RESIZED (WEBP).lnk (shortcut to optimized images)
```

## How to Use

1. **Copy images** to the same folder as `x.bat` and `run.py`
2. **Double-click `x.bat`**
3. **Wait** - the fancy terminal will show progress
4. **Done!** All images processed, organized, and optimized

## Processing Steps

1. ✅ Convert all images to WebP (90% quality)
2. ✅ Sort files by type into folders
3. ✅ Resize images to 1000px max width (aspect ratio preserved)
4. ✅ Optimize for file size reduction
5. ✅ Create shortcuts to optimized files

## What Gets Processed

- Images: JPEG, PNG, BMP, TIFF, GIF, WebP
- All other file types sorted by extension
- Original files NEVER deleted

## Speed

The entire process runs automatically with no prompts or menus - just click and done!

## Notes

- All originals are preserved in the main folder
- Resized versions in `RESIZED/` subfolder
- Further optimized versions in `OPTIMIZED/` subfolder
- Shortcuts created for direct access to optimized images