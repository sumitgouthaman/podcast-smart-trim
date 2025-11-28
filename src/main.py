import argparse
import os
from transcribe import transcribe_audio
from analyze import analyze_transcript_for_ads
from audio import remove_ads, extract_ads
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="podcast-smart-trim: AI-powered Podcast Ad Remover")
    
    # Input/Output
    parser.add_argument("input_file", help="Path to the input podcast audio file")
    parser.add_argument("--output", "-o", help="Path to the output file (default: input_cleaned.mp3)")
    
    # Models & API
    parser.add_argument("--api_key", help="Gemini API Key (overrides env var GEMINI_API_KEY)")
    parser.add_argument("--model", default="base", help="Whisper model size (default: base)")
    parser.add_argument("--gemini_model", default="models/gemini-flash-latest", help="Gemini model name (default: models/gemini-flash-latest)")
    
    # Caching
    parser.add_argument("--no-cache", action="store_true", help="Disable transcription caching")
    parser.add_argument("--cache_dir", help="Custom directory for cache files (default: .cache)")
    
    # Debugging
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (extracts ads to a separate file)")
    
    args = parser.parse_args()
    
    input_path = args.input_file
    if not args.output:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_cleaned.mp3"
    else:
        output_path = args.output
        
    print(f"Processing {input_path}...")
    
    # 1. Transcribe
    try:
        transcript_result = transcribe_audio(input_path, model_size=args.model, use_cache=not args.no_cache, cache_dir=args.cache_dir)
    except Exception as e:
        print(f"Error during transcription: {e}")
        return

    # 2. Analyze
    print(f"Analyzing transcript for ads using {args.gemini_model}...")
    try:
        # Pass use_cache based on no_cache flag
        ads = analyze_transcript_for_ads(transcript_result, api_key=args.api_key, model_name=args.gemini_model, use_cache=not args.no_cache, cache_dir=args.cache_dir)
    except Exception as e:
        print(f"Error during analysis: {e}")
        return
        
    if not ads:
        print("No ads detected.")
        return

    print(f"Found {len(ads)} ad segments:")
    for ad in ads:
        print(f"  - {ad['start']:.2f}s to {ad['end']:.2f}s")
        
    # 3. Remove Ads
    try:
        remove_ads(input_path, ads, output_path)
    except Exception as e:
        print(f"Error during audio processing: {e}")
        return
        
    print(f"Successfully created {output_path}")

    # 4. Debug: Extract Ads
    if args.debug:
        base, ext = os.path.splitext(input_path)
        ads_output_path = f"{base}_ads{ext}"
        print(f"Debug mode enabled. Extracting ads to {ads_output_path}...")
        try:
            extract_ads(input_path, ads, ads_output_path)
        except Exception as e:
            print(f"Error extracting ads: {e}")

if __name__ == "__main__":
    main()
