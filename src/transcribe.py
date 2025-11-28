import whisper
import os
import hashlib
import json
import sys

def get_file_hash(file_path):
    """Calculates the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def transcribe_audio(file_path, model_size="base", use_cache=True, cache_dir=None):
    """
    Transcribes the audio file using OpenAI Whisper.
    
    Args:
        file_path (str): Path to the audio file.
        model_size (str): Whisper model size (tiny, base, small, medium, large).
        use_cache (bool): Whether to use cached transcripts.
        cache_dir (str): Directory to store cache files. Defaults to .cache in project root.
        
    Returns:
        dict: The full transcription result containing segments and text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Caching logic
    if use_cache:
        file_hash = get_file_hash(file_path)
        if not cache_dir:
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"{file_hash}_{model_size}.json")
        
        if os.path.exists(cache_file):
            print(f"Loading cached transcript from {cache_file}...")
            with open(cache_file, "r") as f:
                return json.load(f)

    print(f"Loading Whisper model: {model_size}...")
    model = whisper.load_model(model_size)
    
    print(f"Transcribing {file_path} (this may take a while)...")
    # verbose=True prints progress to stdout
    result = model.transcribe(file_path, verbose=True)
    
    if use_cache:
        print(f"Saving transcript to cache: {cache_file}")
        with open(cache_file, "w") as f:
            json.dump(result, f)
    
    return result

if __name__ == "__main__":
    # Simple test
    if len(sys.argv) > 1:
        res = transcribe_audio(sys.argv[1])
        # Output is already printed by verbose=True, but let's print summary
        print(f"Transcribed {len(res['segments'])} segments.")
