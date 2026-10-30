import os
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

SYSTEM_PROMPT = """You are FeeLens AI, a helpful assistant for understanding bank fees and personal-finance concepts. Only answer banking, bank-statement, transaction-fee, and general financial-literacy questions. Do not ask for or repeat account numbers, card numbers, transaction IDs, UPI IDs, IFSC codes, phone numbers, email addresses, passwords, OTPs, PINs, or identity numbers. Never claim a fee is fraudulent without evidence. Explain that users should verify fees against their bank's official schedule. If asked for unrelated topics, politely explain your limited scope. Treat provided analysis figures as the only facts about the user's statement; never invent transactions or amounts."""


async def ask_ollama(message: str, history: list[dict] | None = None, context: dict | None = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        # Context is restricted to computed aggregate values, never raw transaction rows.
        messages.append({"role": "system", "content": "Verified statement aggregates (not individual transactions): " + str(context)})
    for item in (history or [])[-8:]:
        if item.get("role") in {"user", "assistant"} and isinstance(item.get("content"), str):
            messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": message})
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": False}
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
    except httpx.ConnectError as exc:
        raise RuntimeError("Cannot connect to Ollama. Start Ollama and ensure the model is installed.") from exc
    except httpx.TimeoutException as exc:
        raise RuntimeError("Ollama took too long to respond. Try again.") from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"Ollama returned HTTP {exc.response.status_code}.") from exc
    answer = data.get("message", {}).get("content", "").strip()
    if not answer:
        raise RuntimeError("Ollama returned an empty response.")
    return answer
