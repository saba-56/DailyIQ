import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from models.affair import Affair

load_dotenv()

GEMINI_MODEL = "gemini-3.5-flash-lite"


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from backend/.env")
    return genai.Client(api_key=api_key)


def build_system_instruction(db: Session | None = None) -> str:
    news_context = ""

    if db:
        try:
            recent_affairs = (
                db.query(Affair)
                .order_by(Affair.published_at.desc(), Affair.id.desc())
                .limit(10)
                .all()
            )

            if recent_affairs:
                bullets = []
                for item in recent_affairs:
                    bullets.append(
                        f"• [{item.category or 'General'}] {item.title}: {item.summary}"
                    )
                news_context = "\n".join(bullets)
        except Exception as exc:
            print("Failed to pull news context for Ask AI:", exc)

    instruction = (
        "You are DailyIQ's AI News and Knowledge Companion. "
        "Your purpose is to help students, learners, and competitive exam aspirants "
        "understand daily current affairs, breaking news, history, science, geopolitics, "
        "economics, and general knowledge.\n\n"
        "RESPONSE GUIDELINES:\n"
        "1. Write in clear, structured, and student-friendly Markdown (use short paragraphs, bullet points, and bold text for key names/concepts).\n"
        "2. Break down complex news events by explaining the background, what happened, and why it matters.\n"
        "3. Maintain an objective, balanced, and informative tone.\n"
        "4. If asked about today's news or recent headlines, reference the latest DailyIQ news items provided below when applicable.\n"
        "5. Be concise yet thorough—avoid unnecessary filler.\n"
    )

    if news_context:
        instruction += f"\nRECENT NEWS HEADLINES IN DAILYIQ DATABASE:\n{news_context}\n"

    return instruction


def ask_ai_chat(message: str, history: list[dict] | None = None, db: Session | None = None) -> str:
    """
    Generate an AI response given a message and conversation history.
    history is a list of objects: [{"role": "user"|"model", "content": "..."}]
    """
    client = get_gemini_client()
    system_instruction = build_system_instruction(db)

    gemini_history = []
    if history:
        for turn in history:
            role = turn.get("role")
            content = turn.get("content", "")
            if role in {"user", "model"} and content:
                gemini_history.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=content)]
                    )
                )

    try:
        chat = client.chats.create(
            model=GEMINI_MODEL,
            history=gemini_history,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.6,
            }
        )

        response = chat.send_message(message)
        if response and response.text:
            return response.text.strip()

        return "I couldn't generate a response for that. Please try rephrasing your question."

    except Exception as exc:
        print("Ask AI error:", exc)
        return (
            "I'm having trouble connecting to the knowledge service right now. "
            "Please check back in a moment or try again."
        )
