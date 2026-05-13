from flask import Flask, render_template, request, jsonify
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import requests
import uuid
import os
from dotenv import load_dotenv

app = Flask(__name__)
# ============================================
# 🔐 ADD YOUR AZURE CREDENTIALS HERE
# ============================================


load_dotenv()

SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

LANGUAGE_KEY = os.getenv("LANGUAGE_KEY")
LANGUAGE_ENDPOINT = os.getenv("LANGUAGE_ENDPOINT")

TRANSLATOR_KEY = os.getenv("TRANSLATOR_KEY")
TRANSLATOR_REGION = os.getenv("TRANSLATOR_REGION")
TRANSLATOR_ENDPOINT = os.getenv("TRANSLATOR_ENDPOINT")

def speech_to_text():
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    else:
        return None


# ======================================================
# 🧠 SENTIMENT ANALYSIS FUNCTION
# ======================================================

def analyze_sentiment(text):
    credential = AzureKeyCredential(LANGUAGE_KEY)
    client = TextAnalyticsClient(
        endpoint=LANGUAGE_ENDPOINT,
        credential=credential
    )

    response = client.analyze_sentiment([text])[0]

    return {
        "sentiment": response.sentiment,
        "positive": response.confidence_scores.positive,
        "neutral": response.confidence_scores.neutral,
        "negative": response.confidence_scores.negative
    }


# ======================================================
# 🌍 TRANSLATION FUNCTION
# ======================================================

def translate_text(text, target_language="hi"):
    path = "/translate"
    params = {
        "api-version": "3.0",
        "to": target_language
    }

    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": TRANSLATOR_REGION,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4())
    }

    body = [{"text": text}]

    response = requests.post(
        TRANSLATOR_ENDPOINT + path,
        params=params,
        headers=headers,
        json=body
    )

    result = response.json()

    return result[0]["translations"][0]["text"]

import os
import uuid
import azure.cognitiveservices.speech as speechsdk

def text_to_speech(text, language_code):

    voices = {
        "en": "en-IN-PrabhatNeural",
        "hi": "hi-IN-MadhurNeural",
        "ta": "ta-IN-ValluvarNeural",
        "mr": "mr-IN-ManoharNeural",
        "bn": "bn-IN-BashkarNeural"
    }

    # Create speech configuration
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    # Set voice safely
    speech_config.speech_synthesis_voice_name = voices.get(
        language_code,
        "en-IN-PrabhatNeural"
    )

    # Optional: Set audio format explicitly
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )

    # Ensure static folder exists
    static_folder = os.path.join(app.root_path, "static")
    os.makedirs(static_folder, exist_ok=True)

    # Generate unique filename to avoid browser caching
    audio_file = f"{uuid.uuid4()}.mp3"
    file_path = os.path.join(static_folder, audio_file)

    # Create audio config
    audio_config = speechsdk.audio.AudioOutputConfig(filename=file_path)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    # Perform synthesis
    result = synthesizer.speak_text_async(text).get()

    # Proper error handling
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("TTS Success")
        return audio_file

    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("TTS Cancelled:", cancellation_details.reason)
        if cancellation_details.error_details:
            print("Error details:", cancellation_details.error_details)
        return None

    else:
        print("Unexpected TTS result:", result.reason)
        return None
# ======================================================
# 🚀 ROUTES
# ======================================================

from bs4 import BeautifulSoup
import requests

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        url = request.form.get("url")
        paragraph = request.form.get("paragraph")
        selected_language = request.form.get("language", "en")

        if not url and not paragraph:
            return render_template("index.html", error="Please provide a URL or paste content.")

        text_to_summarize = ""

        # If URL provided → fetch article
        if url:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

                paragraphs = soup.find_all("p")
                text_to_summarize = " ".join([p.get_text() for p in paragraphs])

            except Exception:
                return render_template("index.html", error="Failed to fetch article from URL.")

        # If paragraph pasted → use directly
        elif paragraph:
            text_to_summarize = paragraph

        if not text_to_summarize.strip():
            return render_template("index.html", error="Could not extract meaningful content.")

        # Azure safety trim
        text_to_summarize = text_to_summarize[:12000]

        # 🔹 Generate Summary
        summary = summarize_text(text_to_summarize)

        if not summary:
            return render_template("index.html", error="Summary generation failed.")

        # 🔹 Translate if not English
        if selected_language == "en":
            translated_text = summary
        else:
            translated_text = translate_text(summary, selected_language)
            if not translated_text:
                return render_template("index.html", error="Translation failed.")

        # 🔹 Generate Speech Audio
        audio_file = text_to_speech(translated_text, selected_language)

        return render_template(
            "index.html",
            summary=summary,
            hindi_summary=translated_text,
            audio_file=audio_file
        )

    return render_template("index.html")

def summarize_text(text):

    credential = AzureKeyCredential(LANGUAGE_KEY)
    client = TextAnalyticsClient(
        endpoint=LANGUAGE_ENDPOINT,
        credential=credential
    )

    poller = client.begin_extract_summary([text])
    results = poller.result()

    for doc in results:
        if doc.is_error:
            return None

        summary_sentences = [sentence.text for sentence in doc.sentences]
        return " ".join(summary_sentences)

    return None

# ======================================================
# ▶ RUN APP
# ======================================================

if __name__ == "__main__":
    app.run(debug=True)