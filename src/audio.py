import subprocess
import os
import json

def get_duration(input_file):
    """Get the duration of the audio file using ffprobe."""
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        input_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        raise RuntimeError(f"Could not determine duration of {input_file}. Error: {result.stderr}")

def remove_ads(input_file, ad_segments, output_file):
    """
    Removes ad segments from the audio file using ffmpeg directly.
    
    Args:
        input_file (str): Path to the input audio file.
        ad_segments (list): List of dicts with 'start' and 'end' (in seconds).
        output_file (str): Path to save the modified audio.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Sort segments
    ad_segments.sort(key=lambda x: x['start'])
    
    # Calculate keep segments
    keep_segments = []
    current_pos = 0.0
    total_duration = get_duration(input_file)
    
    for ad in ad_segments:
        start = ad['start']
        end = ad['end']
        
        if start > current_pos:
            keep_segments.append((current_pos, start))
        
        current_pos = max(current_pos, end)
        
    if current_pos < total_duration:
        keep_segments.append((current_pos, total_duration))
        
    if not keep_segments:
        print("No audio to keep!")
        return

    # Create a complex filter for ffmpeg
    # [0:a]atrim=start=0:end=10,asetpts=PTS-STARTPTS[a0];
    # [0:a]atrim=start=20:end=30,asetpts=PTS-STARTPTS[a1];
    # [a0][a1]concat=n=2:v=0:a=1[out]
    
    filter_complex = ""
    for i, (start, end) in enumerate(keep_segments):
        filter_complex += f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}];"
    
    concat_inputs = "".join([f"[a{i}]" for i in range(len(keep_segments))])
    filter_complex += f"{concat_inputs}concat=n={len(keep_segments)}:v=0:a=1[out]"
    
    cmd = [
        "ffmpeg",
        "-y", # Overwrite output
        "-i", input_file,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        output_file
    ]
    
    print(f"Running ffmpeg to splice audio...")
    subprocess.run(cmd, check=True)
    print(f"Created {output_file}")

def extract_ads(input_file, ad_segments, output_file):
    """
    Extracts ad segments from the audio file and concatenates them.
    
    Args:
        input_file (str): Path to the input audio file.
        ad_segments (list): List of dicts with 'start' and 'end' (in seconds).
        output_file (str): Path to save the extracted ads.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    if not ad_segments:
        print("No ads to extract.")
        return

    # Sort segments
    ad_segments.sort(key=lambda x: x['start'])
    
    # Create a complex filter for ffmpeg
    filter_complex = ""
    for i, ad in enumerate(ad_segments):
        start = ad['start']
        end = ad['end']
        filter_complex += f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}];"
    
    concat_inputs = "".join([f"[a{i}]" for i in range(len(ad_segments))])
    filter_complex += f"{concat_inputs}concat=n={len(ad_segments)}:v=0:a=1[out]"
    
    cmd = [
        "ffmpeg",
        "-y", # Overwrite output
        "-i", input_file,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        output_file
    ]
    
    print(f"Running ffmpeg to extract ads...")
    subprocess.run(cmd, check=True)
    print(f"Created {output_file}")

if __name__ == "__main__":
    pass
