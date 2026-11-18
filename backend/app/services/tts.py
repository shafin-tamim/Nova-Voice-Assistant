from pathlib import Path
import uuid
from ..config import UPLOAD_DIR

VOICE_MAP = {"bn": "bn-BD-NabanitaNeural", "en": "en-US-AriaNeural"}
async def synthesize(text: str, language: str = "bn") -> str:
    import edge_tts
    voice = VOICE_MAP["en"] if language.lower().startswith("en") else VOICE_MAP["bn"]
    filename = f"{uuid.uuid4().hex}.mp3"
    output = UPLOAD_DIR / filename
    await edge_tts.Communicate(text, voice).save(str(output))
    return filename
