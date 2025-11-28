import google.generativeai as genai
import os
import json
import typing
import hashlib

def get_content_hash(content):
    """Calculates the MD5 hash of a string."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def analyze_transcript_for_ads(transcript_result, api_key=None, model_name="models/gemini-flash-latest", use_cache=True, cache_dir=None):
    """
    Analyzes the transcript to identify ad segments using Gemini.
    
    Args:
        transcript_result (dict): The result from Whisper transcription.
        api_key (str): Google Gemini API key.
        model_name (str): Gemini model name.
        use_cache (bool): Whether to use cached ad analysis results.
        cache_dir (str): Directory to store cache files. Defaults to .cache in project root.
        
    Returns:
        list: A list of dicts with 'start' and 'end' keys for ad segments.
    """
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not provided.")

    # Prepare the transcript text with timestamps for the LLM
    transcript_text = ""
    for segment in transcript_result['segments']:
        transcript_text += f"[{segment['start']:.2f}-{segment['end']:.2f}] {segment['text']}\n"

    # Caching logic
    if use_cache:
        # Hash includes transcript content and model name to ensure uniqueness
        content_to_hash = transcript_text + model_name
        content_hash = get_content_hash(content_to_hash)
        if not cache_dir:
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"{content_hash}_ads.json")
        
        if os.path.exists(cache_file):
            print(f"Loading cached ad analysis from {cache_file}...")
            with open(cache_file, "r") as f:
                return json.load(f)

    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        print(f"Error loading model {model_name}: {e}")
        return []

    prompt = f"""
    You are an expert audio editor. Your task is to identify advertisement segments in the following podcast transcript.
    The transcript is formatted as: [start_time-end_time] text.
    
    Look for:
    - Host reading a sponsor message (e.g., "This episode is brought to you by...", "Use code...", "Go to website.com").
    - Pre-recorded ad spots (often different tone, but hard to tell from text alone, rely on content).
    - Breaks indicated by music or pauses (though you only have text).
    
    Return a JSON list of objects, where each object has a "start" and "end" float value representing the start and end time of the ad block.
    If there are no ads, return an empty list.
    
    Example output:
    [
        {{"start": 120.5, "end": 180.0}},
        {{"start": 450.0, "end": 510.5}}
    ]
    
    Transcript:
    {transcript_text}
    """

    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    
    ads = []
    try:
        ads = json.loads(response.text)
    except json.JSONDecodeError:
        print("Error decoding JSON from LLM response.")
        print(response.text)
        return []
        
    if use_cache:
        print(f"Saving ad analysis to cache: {cache_file}")
        with open(cache_file, "w") as f:
            json.dump(ads, f)
            
    return ads

if __name__ == "__main__":
    # Mock data for testing
    mock_transcript = {
        'segments': [
            {'start': 0.0, 'end': 10.0, 'text': "Welcome to the podcast."},
            {'start': 10.0, 'end': 30.0, 'text': "This episode is sponsored by MattressCo. Buy a mattress."},
            {'start': 30.0, 'end': 40.0, 'text': "Now back to the show."}
        ]
    }
    # You would need to set GEMINI_API_KEY env var to run this
    # print(analyze_transcript_for_ads(mock_transcript))
