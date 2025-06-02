import cv2
import os
from pathlib import Path

def create_loop_video(input_path, output_path):
    """
    Create a loop video from input video:
    1. Extract first 48 frames + all frames reversed
    2. Repeat this loop 5 times
    """
    print(f"Processing: {input_path}")
    
    # Open the input video
    cap = cv2.VideoCapture(input_path)
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video properties: {width}x{height} @ {fps} FPS")
    
    # Read all frames
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        if len(frames) == 49:
            break
    
    cap.release()
    
    print(f"Total frames read: {len(frames)}")
    
    # Verify we have 49 frames as expected
    if len(frames) != 49:
        print(f"Warning: Expected 49 frames, but got {len(frames)} frames")
    
    # Create loop: first 48 frames + all frames reversed
    loop_frames = frames[:48] + frames[::-1]
    print(f"Loop frames created: {len(loop_frames)} frames")
    
    # Repeat the loop 5 times
    final_frames = []
    for i in range(3):
        final_frames.extend(loop_frames)
    
    print(f"Final video will have: {len(final_frames)} frames")
    
    # Create output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Write all frames
    for frame in final_frames:
        out.write(frame)
    
    out.release()
    print(f"Saved: {output_path}")
    print()

def main():
    # Get input video path from command line argument
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_video_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Create loops directory if it doesn't exist
    loops_dir = Path("./loops")
    loops_dir.mkdir(exist_ok=True)
    
    # Create output filename
    input_filename = Path(input_path).name
    output_file = loops_dir / f"loop_{input_filename}"
    
    # Skip if output already exists
    if output_file.exists():
        print(f"Skipping {input_path} - output file {output_file} already exists")
        sys.exit(0)
    
    try:
        create_loop_video(input_path, str(output_file))
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        sys.exit(1)
    
    print("Video processed successfully!")

if __name__ == "__main__":
    main()
