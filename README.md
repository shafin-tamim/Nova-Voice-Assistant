# NOVA Voice Assistant

NOVA is a local-first Bangla, English, and Banglish voice assistant. It provides a browser-based chat and push-to-talk interface backed by FastAPI, Faster-Whisper, Google Gemini, Edge TTS, SQLite, and a lightweight document knowledge base.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4)
![License](https://img.shields.io/badge/License-Not%20specified-lightgrey)

## Features

- Text chat with Bangla, English, or automatic reply language selection
- Push-to-talk browser recording with pause and stop controls
- Speech-to-text with Faster-Whisper
- Natural generated replies through Google Gemini
- Spoken Bangla or English replies through Microsoft Edge TTS
- SQLite conversation history, restored for the browser session
- PDF, DOCX, and TXT document ingestion
- Overlapping document chunks and lexical context retrieval
- Interactive API documentation at `/docs`
- Health and WebSocket connectivity endpoints

## Technology

| Component | Technology |
| --- | --- |
| Web framework | FastAPI and Uvicorn |
| Frontend | HTML, CSS, and vanilla JavaScript |
| Speech recognition | Faster-Whisper |
| Language model | Google Gemini API |
| Text-to-speech | Edge TTS |
| Conversation and document storage | SQLite and SQLAlchemy |
| Document parsing | PyPDF and python-docx |

## Requirements

- Windows 10/11 or Linux
- Python 3.11
- FFmpeg available on `PATH`
- A Google Gemini API key
- Internet access for Gemini and Edge TTS
- A modern browser with microphone support

FFmpeg is included in the Docker image. For native Windows or Linux setup, install FFmpeg separately.

## Quick Start on Windows

```powershell
git clone https://github.com/shafin-tamim/Nova-Voice-Assistant.git
cd Nova-Voice-Assistant

py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env
```

Open `.env` and set `GEMINI_API_KEY`:

```dotenv
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
WHISPER_MODEL=small
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
TTS_PROVIDER=edge
MAX_UPLOAD_MB=20
```

Start the server:

```powershell
uvicorn backend.app.main:app --reload
```

Open <http://127.0.0.1:8000>. Allow microphone access when prompted.

> Microphone access normally requires `localhost` or HTTPS. Do not use `http://192.168.x.x` for microphone testing unless the browser is served over HTTPS.

## First Run

The first voice request downloads the configured Faster-Whisper model. The default model is `small`; use `base` for faster testing on limited hardware:

```dotenv
WHISPER_MODEL=base
```

CPU with `int8` computation is the default. A discrete GPU is not required.

## Docker

Create your environment file, set `GEMINI_API_KEY`, and run:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open <http://localhost:8000>.

To stop and remove the containers:

```powershell
docker compose down
```

The compose configuration persists `nova.db` and mounts `uploads/` and `knowledge_base/` for the container.

## Using NOVA

### Text chat

1. Open the application.
2. Enter a message in the conversation panel.
3. Choose **Match detected language**, **বাংলা**, or **English**.
4. NOVA returns and stores the reply.

The browser keeps a session identifier in local storage, so recent history is restored after a refresh.

### Voice chat

1. Select the microphone button.
2. Speak in Bangla, English, or Banglish.
3. Use **Pause** if needed, then select **Stop & send**.
4. NOVA displays the transcript and reply, then plays the generated speech.

### Document Q&A

Upload a PDF, DOCX, or TXT file from the Knowledge Base panel. NOVA extracts and indexes text in overlapping chunks. Relevant chunks are added to future chat and voice prompts.

Document retrieval is lexical rather than vector/embedding-based.

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `GEMINI_API_KEY` | empty | Required for Gemini responses |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model identifier |
| `WHISPER_MODEL` | `small` | Faster-Whisper model size |
| `WHISPER_DEVICE` | `cpu` | Whisper device, such as `cpu` or `cuda` |
| `WHISPER_COMPUTE_TYPE` | `int8` | Whisper compute type |
| `TTS_PROVIDER` | `edge` | Reserved TTS provider setting |
| `MAX_UPLOAD_MB` | `20` | Maximum audio and document upload size |

The SQLite database is created automatically at `nova.db`.

## API Reference

Interactive documentation is available at:

- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>

### Core endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Browser interface |
| `GET` | `/health` | Service health check |
| `POST` | `/api/chat` | Text chat |
| `GET` | `/api/history/{session_id}` | Restore a conversation |
| `POST` | `/api/voice/ask` | Upload audio and receive text plus speech |
| `GET` | `/api/voice/audio/{filename}` | Download a generated MP3 |
| `POST` | `/api/documents/upload` | Index a PDF, DOCX, or TXT file |
| `WS` | `/ws/status` | Connectivity acknowledgement test |

### Text chat example

```powershell
$body = @{
    message = "তুমি কেমন আছো?"
    session_id = "demo"
    reply_language = "auto"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/chat" -ContentType "application/json" -Body $body
```

Valid `reply_language` values are `auto`, `bn`, and `en`.

### Voice upload example

```powershell
curl.exe -F "audio=@recording.webm" -F "session_id=demo" -F "reply_language=bn" http://127.0.0.1:8000/api/voice/ask
```

## Tests

Run the test suite from the project root:

```powershell
pytest -q
```

The current tests cover application startup and the `/health` endpoint.

## Project Structure

```text
Nova-Voice-Assistant/
├── backend/app/
│   ├── api/              # Chat, voice, and document routes
│   ├── services/         # Gemini, Whisper, Edge TTS, and RAG logic
│   ├── templates/        # FastAPI HTML template
│   ├── config.py         # Environment configuration
│   ├── database.py       # SQLite models and session setup
│   └── main.py           # Application entry point
├── static/
│   ├── css/              # Interface styles
│   └── js/               # Browser and microphone behavior
├── tests/                # Pytest coverage
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Troubleshooting

### No Gemini response

- Confirm `GEMINI_API_KEY` is set in `.env`.
- Verify that the model in `GEMINI_MODEL` is available to the API key.
- Confirm that internet access is available.

### Microphone unavailable

- Open <http://127.0.0.1:8000>, not an insecure remote IP.
- Grant microphone permission in the browser.
- Check whether another application is exclusively using the microphone.

### FFmpeg or audio errors

- Confirm FFmpeg is on `PATH`:

  ```powershell
  ffmpeg -version
  ```

- Restart the terminal after installing FFmpeg.
- Try uploading WAV or WebM audio if browser recording fails.

### Slow speech transcription

Use a smaller model:

```dotenv
WHISPER_MODEL=base
```

The first run may take longer because Faster-Whisper downloads model files.

### Docker cannot find `.env`

Copy `.env.example` to `.env` in the repository root before starting Compose.

## Current Limitations

- Voice mode is push-to-talk, not continuous streaming.
- `/ws/status` confirms WebSocket connectivity only.
- There is no streaming ASR, voice activity detection, barge-in, or diarization.
- Document search is lexical and does not provide vector similarity or citations.
- Conversation and document data are shared in local SQLite storage.
- Banglish recognition quality depends on accent and recording quality.
- The **Clear** button clears the browser panel but does not delete persisted SQLite history.
- Authentication, per-user isolation, rate limits, retention controls, and production hardening are not included.

## Privacy and Security

Uploaded source audio is removed after transcription. Gemini receives the recognized text and generated text is sent to Edge TTS for voice synthesis. Uploaded documents are parsed and stored as text chunks in the local SQLite database.

Do not upload sensitive or confidential data until provider privacy policies and local data handling requirements have been reviewed. Add authentication, access controls, HTTPS, retention policies, and secret management before public deployment.
