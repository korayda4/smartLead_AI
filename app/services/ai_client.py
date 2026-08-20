import re
import time
import logging
import requests

logger = logging.getLogger(__name__)


class NvidiaClient:
    def __init__(self, api_key: str, model: str, api_url: str):
        self._api_key = api_key
        self._model = model
        self._api_url = api_url
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def post(self, messages: list[dict]) -> str | None:
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.3,
            "top_p": 0.85,
            "max_tokens": 200,
            "frequency_penalty": 0.3,
            "stream": False,
        }
        for attempt in range(2):
            try:
                resp = requests.post(self._api_url, headers=self._headers, json=payload, timeout=10)
                if resp.status_code == 503 and attempt == 0:
                    logger.warning("Model 503 — retry in 2s")
                    time.sleep(2)
                    continue
                if resp.status_code != 200:
                    logger.error(f"API {resp.status_code}: {resp.text[:200]}")
                    return None
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content")
                return None
            except requests.Timeout:
                logger.warning(f"Timeout attempt {attempt + 1}")
                if attempt == 0:
                    time.sleep(1)
                    continue
                return None
            except requests.RequestException as exc:
                logger.error(f"Request error: {exc}")
                return None
        return None

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""
        pattern = r"^(?:Afet\s*Noktas[ıi](?:'n[ıi]n)?\s*(?:Ak[ıi]ll[ıi]\s*)?(?:Asistan[ıi]|Dan[ıi][şs]man[ıi])|Asistan|Assistant|Dan[ıi][şs]man|AI|Bot)\s*:\s*"
        return re.sub(pattern, "", text.strip(), flags=re.IGNORECASE).strip()
