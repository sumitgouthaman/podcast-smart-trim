# podcast-smart-trim

**podcast-smart-trim** is an AI-powered CLI tool that automatically identifies and removes advertisement segments from podcasts. It leverages OpenAI's Whisper for high-accuracy transcription and Google's Gemini LLM for intelligent ad detection.

## Features

- **AI Transcription**: Uses `openai-whisper` to generate accurate transcripts with timestamps.
- **Smart Ad Detection**: Uses Google Gemini (`models/gemini-flash-latest`) to analyze context and identify ad breaks.
- **Precision Cutting**: Uses `ffmpeg` to surgically remove ad segments.
- **Caching**: Caches transcripts and ad analysis results to speed up repeated runs.
- **Debug Mode**: Option to extract detected ads to a separate file for verification.

## Prerequisites

- **Python 3.10+**
- **ffmpeg**: Required for audio processing.
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
- **Google Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/podcast-smart-trim.git
   cd podcast-smart-trim
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your API key (optional, can also be passed via CLI):
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

## Usage

Run the tool on a podcast audio file:

```bash
python src/main.py path/to/podcast.mp3
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `input_file` | Path to the input audio file (required) | N/A |
| `-o`, `--output` | Path to the output file | `input_cleaned.mp3` |
| `--api_key` | Google Gemini API Key | `GEMINI_API_KEY` env var |
| `--model` | Whisper model size (tiny, base, small, medium, large) | `base` |
| `--gemini_model` | Gemini model name | `models/gemini-flash-latest` |
| `--no-cache` | Disable transcription and analysis caching | `False` |
| `--cache_dir` | Custom directory for cache files | `.cache` |
| `--debug` | Extract detected ads to a separate file | `False` |

### Examples

**Basic usage:**
```bash
python src/main.py episode1.mp3
```

**Using a larger Whisper model for better accuracy:**
```bash
python src/main.py episode1.mp3 --model medium
```

**Debug mode (verifying ads):**
```bash
python src/main.py episode1.mp3 --debug
# Creates episode1_cleaned.mp3 AND episode1_ads.mp3
```

**Custom cache location:**
```bash
python src/main.py episode1.mp3 --cache_dir /tmp/podcache
```

## How It Works

1.  **Transcribe**: The audio is transcribed using OpenAI Whisper locally.
2.  **Analyze**: The transcript (with timestamps) is sent to Google Gemini with a prompt to identify ad segments based on context (sponsor reads, tone changes, etc.).
3.  **Process**: The original audio is split and stitched back together using `ffmpeg`, skipping the identified ad segments.
