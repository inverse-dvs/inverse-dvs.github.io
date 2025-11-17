#!/usr/bin/env python3
"""
Script to compress all videos in the videos/ directory for web optimization.
Uses imageio-ffmpeg (which should be installed) to compress videos.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional, Tuple

try:
    import imageio_ffmpeg as ffmpeg
except ImportError:
    print("Error: imageio-ffmpeg is not installed.")
    print("Please install it: pip install imageio-ffmpeg")
    sys.exit(1)

# Compression settings
CRF = 26  # Constant Rate Factor: 18-28 range, 26 is more aggressive for smaller files
PRESET = "fast"  # Encoding speed: ultrafast, fast, medium, slow, slower, veryslow
MAX_WIDTH = 1920
MAX_HEIGHT = 1080
AUDIO_BITRATE = "96k"  # Reduced audio bitrate for web

# Video extensions to process
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.webm', '.mkv'}


def get_ffmpeg_path() -> str:
    """Get the path to the ffmpeg binary from imageio-ffmpeg."""
    return ffmpeg.get_ffmpeg_exe()


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def compress_video(input_path: Path, ffmpeg_exe: str) -> Tuple[bool, Optional[str]]:
    """
    Compress a video file.
    Returns: (success, error_message)
    """
    # Skip if already compressed or is a backup
    if "_compressed" in input_path.name or input_path.suffix == ".backup":
        return True, None
    
    # Get original file size
    original_size = input_path.stat().st_size
    
    # Create temporary output file
    output_path = input_path.parent / f"{input_path.stem}_compressed{input_path.suffix}"
    
    # Build ffmpeg command
    cmd = [
        ffmpeg_exe,
        "-i", str(input_path),
        "-c:v", "libx264",
        "-crf", str(CRF),
        "-preset", PRESET,
        "-vf", f"scale='if(gt(iw,ih),min({MAX_WIDTH},iw),-1)':'if(gt(iw,ih),-1,min({MAX_HEIGHT},ih))'",
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-movflags", "+faststart",
        "-y",  # Overwrite output file
        str(output_path)
    ]
    
    # Run ffmpeg
    import subprocess
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except subprocess.CalledProcessError as e:
        return False, f"FFmpeg error: {e.stderr.decode()}"
    except Exception as e:
        return False, f"Error: {str(e)}"
    
    # Check if output file was created
    if not output_path.exists():
        return False, "Output file was not created"
    
    # Check file sizes
    new_size = output_path.stat().st_size
    
    if new_size >= original_size:
        # Compressed file is not smaller, remove it
        output_path.unlink()
        return True, None  # Not an error, just not beneficial
    
    # Replace original with compressed version
    backup_path = input_path.with_suffix(input_path.suffix + ".backup")
    shutil.move(str(input_path), str(backup_path))
    shutil.move(str(output_path), str(input_path))
    
    savings = (1 - new_size / original_size) * 100
    print(f"  Original: {format_size(original_size)}")
    print(f"  Compressed: {format_size(new_size)}")
    print(f"  Savings: {savings:.1f}%")
    
    return True, None


def main():
    """Main function to compress all videos."""
    videos_dir = Path("videos")
    
    if not videos_dir.exists():
        print(f"Error: {videos_dir} directory not found!")
        sys.exit(1)
    
    # Get ffmpeg executable
    try:
        ffmpeg_exe = get_ffmpeg_path()
        print(f"Using ffmpeg: {ffmpeg_exe}")
    except Exception as e:
        print(f"Error getting ffmpeg: {e}")
        sys.exit(1)
    
    # Find all video files
    video_files = []
    for ext in VIDEO_EXTENSIONS:
        video_files.extend(videos_dir.rglob(f"*{ext}"))
    
    total = len(video_files)
    print(f"\nFound {total} video files to compress\n")
    print("=" * 50)
    
    # Statistics
    processed = 0
    compressed = 0
    skipped = 0
    failed = 0
    not_beneficial = 0
    
    # Process each video
    for idx, video_path in enumerate(video_files, 1):
        print(f"\n[{idx}/{total}] Processing: {video_path}")
        
        # Skip if already compressed or is backup
        if "_compressed" in video_path.name or video_path.suffix == ".backup":
            print("  Skipping (already compressed or backup)")
            skipped += 1
            continue
        
        success, error = compress_video(video_path, ffmpeg_exe)
        
        if not success:
            print(f"  Error: {error}")
            failed += 1
        elif error is None and video_path.exists():
            # Check if we actually compressed it (backup exists)
            backup_path = video_path.with_suffix(video_path.suffix + ".backup")
            if backup_path.exists():
                compressed += 1
            else:
                not_beneficial += 1
                print("  Compressed file was not smaller, keeping original")
        
        processed += 1
    
    # Print summary
    print("\n" + "=" * 50)
    print("Compression complete!")
    print(f"  Processed: {processed} files")
    print(f"  Compressed: {compressed} files")
    print(f"  Not beneficial: {not_beneficial} files")
    print(f"  Skipped: {skipped} files")
    print(f"  Failed: {failed} files")
    print("=" * 50)
    print("\nNote: Original files have been backed up with .backup extension")
    print("You can remove backups with: find videos/ -name '*.backup' -delete")


if __name__ == "__main__":
    main()

