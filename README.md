# WanderAI — AI-powered text summarizer & TTS demo

This small Flask demo summarizes text (or a webpage), optionally translates the summary, and generates speech audio using Azure Cognitive Services.

Key capabilities (implemented in `language.py`):

- Extractive summarization using Azure Text Analytics (extractive summarization)
- Translation using Azure Translator (REST API)
- Text-to-speech (TTS) using Azure Speech SDK
- Speech-to-text helper (uses microphone via Azure Speech SDK)
- A single Flask route (`/`) that accepts a URL or pasted paragraph, returns a summary, translated text (if requested), and a generated audio MP3 saved to `static/`.

## How it works (quick)

- The web form (in `templates/index.html`) accepts either a URL or a pasted paragraph.
- If a URL is provided, the backend fetches the page and extracts paragraph text with BeautifulSoup.
- The app trims input for safety, calls Azure Text Analytics to extract a summary, optionally translates it, and synthesizes speech using the Azure Speech SDK into an MP3 saved under `static/`.

## Required environment variables

Create a `.env` file or set these environment variables before running the app. `language.py` expects the following names:

- SPEECH_KEY — Azure Speech subscription key
- SPEECH_REGION — Azure Speech region (for the SDK)
- LANGUAGE_KEY — Azure Text Analytics key (for summarization / sentiment)
- LANGUAGE_ENDPOINT — Azure Text Analytics endpoint (full URL)
- TRANSLATOR_KEY — Azure Translator subscription key
- TRANSLATOR_REGION — Translator region (used in request headers)
- TRANSLATOR_ENDPOINT — Translator endpoint (base URL, e.g. https://api.cognitive.microsofttranslator.com)

Example `.env` (do NOT commit this file):

```
SPEECH_KEY=your_speech_key
SPEECH_REGION=your_speech_region
LANGUAGE_KEY=your_text_analytics_key
LANGUAGE_ENDPOINT=https://your-text-analytics-resource.cognitiveservices.azure.com/
TRANSLATOR_KEY=your_translator_key
TRANSLATOR_REGION=your_translator_region
TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
```

## Dependencies

The app depends on the following Python packages. A `requirements.txt` file is provided in the repo.

- Flask
- python-dotenv
- requests
- beautifulsoup4
- azure-cognitiveservices-speech
- azure-ai-textanalytics

## Quick setup (Windows PowerShell)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Configure environment variables (create `.env` as shown above) and run the app:

```powershell
# Run directly (language.py contains an if __name__ == "__main__" block)
python language.py

# or use flask run
$env:FLASK_APP = "language.py"
flask run --host=0.0.0.0 --port=5000
```

Open http://localhost:5000 in your browser.

## File map (important files)

- `language.py` — main Flask app and Azure integration (summarization, translation, TTS)
- `templates/index.html` — frontend form and UI
- `static/` — CSS and generated/packaged MP3s used by the frontend

## Notes and tips

- The app uses the Azure Speech SDK to write MP3 files into `static/` so generated audio is served by Flask static middleware. Generated filenames are UUID-based to avoid browser caching.
- Keep credentials out of version control. Use a local `.env` for development and a secure secrets store in production.
- The Translator call in `language.py` uses the REST endpoint directly — ensure your Translator resource region and endpoint are correct if you get 401/403 errors.
- If you run into 429 (too many requests) from Azure services, add retry/backoff logic or increase provisioned throughput.

## Acknowledgements

Thank you to Abhimanyu Sharma Sir for mentorship, and to Ajay Kumar Singh Sir, Zaina fakhre alam Ma'am, and SUDHANSHU SINGH Sir for encouragement.

---

If you'd like, I can also:

- add a `.env.example` with the exact keys
- add a `run.ps1` helper for PowerShell development
- pin dependency versions in `requirements.txt`

Tell me which of those you'd like next.
