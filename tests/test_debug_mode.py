import sys
import os
import subprocess
import math
import struct
import wave

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from audio import extract_ads

def create_sine_wave_wav(filename, duration=10, sample_rate=44100, frequency=440):
    n_frames = int(duration * sample_rate)
    data = []
    for i in range(n_frames):
        value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        data.append(struct.pack('<h', value))
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(data))

def get_duration(input_file):
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        input_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout.strip())

def test_extract_ads():
    input_file = "tests/test_audio.wav"
    output_file = "tests/test_ads.wav"
    
    print("Generating test WAV file...")
    create_sine_wave_wav(input_file)
    
    # Ad from 2s to 4s
    ads = [{'start': 2.0, 'end': 4.0}]
    
    print("Running extract_ads...")
    try:
        extract_ads(input_file, ads, output_file)
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Check duration
    if os.path.exists(output_file):
        duration = get_duration(output_file)
        print(f"Ad duration: {duration}s")
        
        if 1.9 < duration < 2.1:
            print("SUCCESS: Ad duration is correct.")
        else:
            print("FAILURE: Ad duration is incorrect.")
    else:
        print("Output file not created.")

if __name__ == "__main__":
    test_extract_ads()
