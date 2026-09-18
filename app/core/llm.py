from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings


def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.model_name,
        google_api_key=settings.gemini_api_key,
        temperature=0,
    )