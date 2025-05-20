# NexLearn-AI: AI-Powered Flashcard Generator

NexLearn-AI is a web-based application built with Streamlit that harnesses the power of Large Language Models (LLMs) via Ollama to automatically generate interactive Q&A flashcards from diverse content sources. Designed to enhance learning efficiency and knowledge retention, it’s an ideal tool for students, professionals, and lifelong learners.

## Features

### Multi-Source Input: 

- Generate flashcards from:
  -  YouTube Video URLs: Automatically fetches transcripts.
  - Web Article Links: Extracts text efficiently.
  - Uploaded Documents: Supports PDF, DOCX, and DOC files.
  -  Pasted Text or Notes: Create flashcards from your own content.
  - Combined Sources: Merge multiple inputs into one flashcard set.
- Powered Generation: Leverages Llama 3 (via Ollama) for smart, high-quality Q&A pairs.

### Interactive UI:

- Engaging flip-card interface for active review on the generation page.
- Dedicated section to review and flip through all session-generated cards.
- Customizable Output: Adjust the number of flashcards to generate (1-50).
- Session-Based Storage: Flashcards are saved for the current session (cleared once per session, then appended).

### Multiple Export Options: 

Download your flashcard sets as:
- CSV (Comma-Separated Values)
- TSV (Tab-Separated Values, Anki-compatible)
- PDF (Printable format)

### Tech Stack

- Frontend: Streamlit (Python)
- AI Model Backend: Ollama with Llama 3
- Content Extraction:
  -  youtube-transcript-api
  -  trafilatura
  -  PyMuPDF (fitz)
  -  python-docx
  -  openai-whisper (with yt-dlp for audio fallback)
  -  Database: SQLite (for session-based storage)
  -  PDF Generation: fpdf2
  -  FFmpeg: Needed for openai-whisper and yt-dlp audio processing.
  -  Core Language: Python 3.11 or later

## Prerequisites

Python: Version 3.11.x or later.
- Install via Homebrew on macOS:
> brew install python@3.11
- Verify with:
> python3 --version

### Ollama: Required for LLM integration.

- Install: https://ollama.ai/download
- Pull Llama 3:
> ollama run llama3
- Start the server: ollama serve (runs on http://localhost:11434 by default)

## Getting Started

### Clone the Repository: 
> git clone [https://github.com/bvishnuvamsi/AI-Flashcard-Generator.git](https://github.com/bvishnuvamsi/AI-Flashcard-Generator.git)

> cd YOUR_REPOSITORY_NAME

### Create and Activate a Virtual Environment:

> python3.11 -m venv venv
#### On Mac:
> source venv/bin/activate

#### On Windows: 
> venv\Scripts\activate

### Install Dependencies:

Ensure requirements.txt is up-to-date in the repository.
> pip install -r requirements.txt

Note: If openai-whisper installation fails due to torch, install PyTorch separately: PyTorch Installation Guide.

(Optional - Already present in Github Repository) Install Fonts:
Create a fonts folder in the project root.
Download NotoSans-Regular.ttf and NotoSans-Bold.ttf from Google Fonts (Noto Sans).
Place the .ttf files in the fonts folder.

### Run the Streamlit Application:

> streamlit run app.py

- Opens in your browser at http://localhost:8501 by default.

## How to Use

- Navigate to the Home Page: Default landing page for flashcard generation.
- Select Input Type(s): Choose one or more sources (YouTube URL, Web Article, Document Upload, Paste Text).

### Provide Input:

- Enter URLs for YouTube videos or web articles.
- Upload PDF or Word documents.
- Paste text into the text area.
- Specify Flashcard Count: Use the slider to set the number (1-50).
- Generate: Click "Generate Flashcards" to create your set.
- Review & Flip: Explore the flashcards below with navigation and flip options.

### Export:

- Click "Export" in the header to access the export page.
- Download as CSV, TSV, or PDF to review offline.

## Future Vision

We’re excited to expand NexLearn-AI with:

- User accounts for persistent flashcard storage.
- Advanced customization (e.g., question types, difficulty).
- Integration with Spaced Repetition Systems (SRS).
- Image support for flashcards.
- Wider LLM support and collaboration features.
- A browser extension for web content capture.

Check the "About" page in the app for more details about the application!

# Happy Learning with NexLearn-AI! 

License : This project is licensed under the MIT License - see the LICENSE.md file for details.

