import logging
from config import Config
from app.services.ai_client import NvidiaClient
from app.services.fallback_service import FallbackService

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    def __init__(self, message: str, original_exception: Exception | None = None):
        super().__init__(message)
        self.original_exception = original_exception


class AIService:
    def __init__(self, api_key: str | None = None, model: str | None = None, api_url: str | None = None):
        key = api_key or Config.NVIDIA_API_KEY
        self._use_api = bool(key and key.strip())
        self._client = NvidiaClient(key or "", model or Config.NVIDIA_MODEL, api_url or Config.NVIDIA_API_URL)
        self._fallback = FallbackService()
        self._system_prompt = Config.BUSINESS_CONTEXT

    def sohbet_yaniti_al(self, kullanici_mesaji: str, gecmis: list[dict] | None = None) -> str:
        msg = str(kullanici_mesaji).strip() if kullanici_mesaji else ""
        if not msg:
            return "Lütfen sormak istediğiniz konuyu yazın."

        if not self._use_api:
            return self._fallback.get(msg)

        messages = [{"role": "system", "content": self._system_prompt}]
        for item in (gecmis or [])[-2:]:
            if not isinstance(item, dict):
                continue
            content = item.get("content") or item.get("text") or item.get("mesaj") or ""
            raw_role = item.get("role") or item.get("sender") or "user"
            role = "user" if str(raw_role).lower() in {"user", "kullanici", "human", "client", "siz", "me"} else "assistant"
            if content and str(content).strip():
                messages.append({"role": role, "content": str(content).strip()})
        messages.append({"role": "user", "content": msg})

        result = self._client.post(messages)
        if result:
            return NvidiaClient.clean(result)

        logger.warning("API yanıt vermedi, fallback devreye girdi.")
        return self._fallback.get(msg)
