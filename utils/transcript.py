import os
import re
import whisper
import tempfile
import yt_dlp
import fitz
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import trafilatura
from io import BytesIO
from docx import Document

def extract_text_from_docx(uploaded_file):
    doc = Document(BytesIO(uploaded_file.read()))
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_article_text(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        result = trafilatura.extract(downloaded)
        return result
    return None

def get_transcript_from_url(url: str) -> str:
    video_id = extract_video_id(url)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        print("No transcript available. Falling back to Whisper...")
        return transcribe_with_whisper(video_id)


def extract_video_id(url: str) -> str:
    # Handles various YouTube URL formats
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Invalid YouTube URL")


def transcribe_with_whisper(video_id: str) -> str:
    model = whisper.load_model("base")

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "outtmpl": os.path.join(tempfile.gettempdir(), f"{video_id}.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
        audio_path = os.path.join(tempfile.gettempdir(), f"{video_id}.mp3")

    result = model.transcribe(audio_path)
    return result["text"]
