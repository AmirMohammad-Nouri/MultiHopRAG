# llm.py
import requests, json, re
from config import LLM_MODEL, EMBED_MODEL

def llm_call(prompt, model=LLM_MODEL, temperature=0.0, json_mode=False):
    """
    json_mode=True constrains Ollama's output to valid JSON at generation time
    (supported in modern Ollama versions), which meaningfully reduces parse
    failures compared to just asking nicely in the prompt.
    """
    payload = {
        "model": model, "prompt": prompt, "stream": False,
        "options": {"temperature": temperature}
    }
    if json_mode:
        payload["format"] = "json"

    r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
    try:
        data = r.json()
    except json.JSONDecodeError:
        raise RuntimeError(f"Ollama returned non-JSON HTTP response: {r.text[:200]}")

    if "response" not in data:
        raise RuntimeError(f"Ollama generate call failed: {data}")
    return data["response"]


def embed(text, model=EMBED_MODEL):
    if not text or not text.strip():
        raise ValueError("embed() called with empty text")
    r = requests.post("http://localhost:11434/api/embeddings", json={
        "model": model, "prompt": text
    }, timeout=60)
    data = r.json()
    if "embedding" not in data:
        raise RuntimeError(f"Ollama embedding call failed for text (len={len(text)}): {text[:100]!r}\nResponse: {data}")
    return data["embedding"]


def safe_json_extract(raw_output):
    """Defensive fallback for when json_mode isn't used or still misbehaves."""
    match = re.search(r'\{.*\}', raw_output, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def llm_call_json(prompt, model=LLM_MODEL, temperature=0.0, retries=2):
    """
    Combines json_mode with a retry loop and defensive parsing —
    tries the constrained path first, falls back to regex extraction,
    retries once more on total failure before giving up.
    """
    for attempt in range(retries + 1):
        try:
            raw = llm_call(prompt, model=model, temperature=temperature, json_mode=True)
            parsed = safe_json_extract(raw)
            if parsed is not None:
                return parsed
        except Exception as e:
            if attempt == retries:
                print(f"[WARN] llm_call_json failed after {retries+1} attempts: {e}")
                return None
    return None