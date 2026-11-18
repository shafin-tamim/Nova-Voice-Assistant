# NOVA — Bangla-English Voice AI Assistant

NOVA is a local-first portfolio MVP built with FastAPI, HTML/CSS/Vanilla JS, Faster-Whisper ASR, Gemini, Edge TTS, SQLite conversation history and document Q&A.

## Included and wired features
- Responsive browser dashboard with text chat and push-to-talk microphone recording.
- Audio upload to FastAPI; Faster-Whisper transcription (CPU INT8 default).
- Gemini answers with recent conversation history and optional document context.
- Bangla/English TTS voice selection and configurable reply language.
- SQLite conversation persistence and history restoration in the browser.
- PDF, DOCX and TXT ingestion with overlapping chunks and Bangla-aware lexical retrieval.
- Health endpoint, WebSocket connectivity acknowledgement, API docs and a basic test.

## Honest limitations
This is an end-to-end **MVP**, not production-grade real-time voice or telephony. Voice is push-to-talk: the browser records a clip and uploads it after Stop. `/ws/status` is only a connectivity test, not streaming audio. The document retriever is lexical, not embedding/vector RAG. There is no VAD barge-in, streaming ASR, diarization, sentiment model, SIP/VoIP, authentication, multi-user document isolation or production security hardening. Banglish recognition is best-effort and must be evaluated with real speakers.

## Requirements
- Python 3.11 recommended
- FFmpeg installed and available on PATH
- Internet for Gemini and Edge TTS
- Gemini API key in `.env`

## Windows setup
```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
# Edit .env and set GEMINI_API_KEY
uvicorn backend.app.main:app --reload
```
Open http://127.0.0.1:8000 and allow microphone access. Browser microphone access requires localhost or HTTPS.

## First run
Faster-Whisper downloads its model on the first voice request. Start with `WHISPER_MODEL=base` for faster CPU tests; `small` can improve accuracy but takes longer. GTX 1650 4GB is not required because CPU INT8 is the default.

## API
- `GET /health`
- `POST /api/chat` JSON: `{"message":"তুমি কেমন আছো?","session_id":"demo","reply_language":"auto"}`
- `GET /api/history/{session_id}`
- `POST /api/voice/ask` multipart: `audio`, optional `session_id`, optional `reply_language`
- `GET /api/voice/audio/{filename}`
- `POST /api/documents/upload` multipart: `file` (PDF/DOCX/TXT)
- `WS /ws/status` connectivity smoke test only
- Interactive docs: `/docs`

## Tests
```powershell
pytest -q
```

## Docker
```bash
cp .env.example .env
# Add GEMINI_API_KEY
 docker compose up --build
```

## Next engineering milestones
1. WebSocket binary audio streaming and incremental transcription.
2. VAD, endpoint detection and interruption/barge-in.
3. Multilingual embedding RAG (e.g. multilingual-e5 + FAISS/Chroma).
4. Bangla/Banglish evaluation set with WER/CER metrics.
5. Speaker diarization, intent/sentiment analytics and SIP/VoIP.
6. Authentication, per-user data isolation, rate limits, retention policy, HTTPS and deployment monitoring.

## Privacy
Audio is uploaded to this server for transcription and temporary source files are deleted after processing. Gemini receives recognized text; Edge TTS receives generated text. Do not upload sensitive documents without reviewing provider privacy policies. Add authentication and access controls before exposing this app publicly.
