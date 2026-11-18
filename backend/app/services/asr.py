from functools import lru_cache
from ..config import settings

@lru_cache(maxsize=1)
def get_model():
    from faster_whisper import WhisperModel
    return WhisperModel(settings.whisper_model, device=settings.whisper_device, compute_type=settings.whisper_compute_type)

def transcribe(path: str) -> dict:
    model = get_model()
    segments, info = model.transcribe(path, beam_size=3, vad_filter=True)
    text = " ".join(s.text.strip() for s in segments).strip()
    return {"text": text, "language": info.language, "language_probability": round(info.language_probability, 3)}
