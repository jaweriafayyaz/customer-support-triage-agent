import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from config import GROQ_API_KEY, GROQ_MODEL, MOCK_MODE
from schemas import ClassificationResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("llm_client")

CLASSIFY_SYSTEM_PROMPT = """You are a support ticket classifier. Given a ticket
subject and body, respond with ONLY a JSON object like:
{"category": "Billing", "confidence": 0.9}
Valid categories: Billing, Refund, Shipping, Technical, General, Unroutable.
If the ticket is empty, spam, or nonsensical, use "Unroutable" with low confidence."""

DRAFT_SYSTEM_PROMPT = """You are a helpful, concise customer support agent.
Write a short (2-4 sentence) reply to the ticket using the provided policy
context if given. Do not invent policies not present in the context."""


def _mock_classify(subject: str, body: str) -> dict:
    text = f"{subject} {body}".lower()

    if not body.strip():
        return {"category": "Unroutable", "confidence": 0.10}
    if "charged twice" in text or "duplicate charge" in text:
        return {"category": "Billing", "confidence": 0.93}
    if "refund" in text or "damaged" in text:
        return {"category": "Refund", "confidence": 0.88}
    if "delivered" in text or "did not receive" in text or "never got it" in text:
        return {"category": "Shipping", "confidence": 0.90}
    if "crash" in text or "login" in text or "error" in text or "bug" in text or "not working" in text:
        return {"category": "Technical", "confidence": 0.87}
    return {"category": "General", "confidence": 0.55}


def _mock_draft(subject: str, context: str | None) -> str:
    if context:
        return (f"Hi, thanks for reaching out about '{subject}'. Based on our policy: "
                f"{context} We'll follow up shortly with next steps.")
    return (f"Hi, thanks for reaching out about '{subject}'. A member of our team "
            f"will review your message and get back to you shortly.")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _call_groq(system_prompt: str, user_prompt: str) -> str:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def classify_ticket(subject: str, body: str) -> ClassificationResult:
    if MOCK_MODE:
        raw = _mock_classify(subject, body)
    else:
        try:
            user_prompt = f"Subject: {subject}\nBody: {body}"
            content = _call_groq(CLASSIFY_SYSTEM_PROMPT, user_prompt)
            raw = json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Classifier LLM call/parse failed: {e}. Falling back to Unroutable.")
            raw = {"category": "Unroutable", "confidence": 0.0}

    try:
        return ClassificationResult(**raw)
    except Exception as e:
        logger.error(f"Classifier output failed schema validation: {e}. Raw: {raw}")
        return ClassificationResult(category="Unroutable", confidence=0.0)


def draft_reply(subject: str, body: str, context: str | None) -> str:
    if MOCK_MODE:
        return _mock_draft(subject, context)

    try:
        context_note = f"\nPolicy context: {context}" if context else ""
        user_prompt = f"Subject: {subject}\nBody: {body}{context_note}"
        return _call_groq(DRAFT_SYSTEM_PROMPT, user_prompt).strip()
    except Exception as e:
        logger.error(f"Drafter LLM call failed after retries: {e}. Using safe fallback reply.")
        return (f"Hi, thanks for reaching out about '{subject}'. A member of our "
                f"team will review your message and get back to you shortly.")