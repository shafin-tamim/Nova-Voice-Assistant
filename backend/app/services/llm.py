from starlette.concurrency import run_in_threadpool
from ..config import settings

SYSTEM_PROMPT = """You are NOVA, a helpful Bangla-English voice assistant. Understand Bangla, English and Banglish (Romanized Bangla). Reply in the same language/script the user used unless a reply language is explicitly requested. For voice answers, be concise, natural and easy to speak. Use supplied document context only when relevant; never invent citations or claim to have read unavailable material. Never claim to perform actions outside this application."""

def _generate(message: str, history: list[dict], context: str, reply_language: str) -> str:
    from google import genai
    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = [SYSTEM_PROMPT]
    if reply_language == "bn": prompt.append("Reply in natural Bangla script.")
    elif reply_language == "en": prompt.append("Reply in English.")
    if context:
        prompt.append("Relevant knowledge-base excerpts:\n" + context)
    for item in history[-10:]:
        role = "user" if item["role"] == "user" else "assistant"
        prompt.append(f"{role}: {item['content']}")
    prompt.append("user: " + message)
    response = client.models.generate_content(model=settings.gemini_model, contents="\n\n".join(prompt))
    return response.text or "দুঃখিত, এই মুহূর্তে উত্তর তৈরি করতে পারছি না।"

async def answer(message: str, history: list[dict] | None = None, context: str = "", reply_language: str = "auto") -> str:
    if not settings.gemini_api_key:
        return "Gemini API key সেট করা হয়নি। .env ফাইলে GEMINI_API_KEY যোগ করো।"
    try:
        return await run_in_threadpool(_generate, message, history or [], context, reply_language)
    except Exception as exc:
        return f"AI service error ({type(exc).__name__}). API key, model name ও internet connection পরীক্ষা করো।"
