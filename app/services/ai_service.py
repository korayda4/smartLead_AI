import logging
import requests
from config import Config

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception raised when NVIDIA NIM AI API service fails."""
    def __init__(self, message: str, original_exception: Exception | None = None):
        super().__init__(message)
        self.original_exception = original_exception


class AIService:
    """
    NVIDIA NIM AI Service wrapper handling LLM communication for Afet Noktası sales assistant.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None, api_url: str | None = None):
        self.api_key = api_key if api_key is not None else Config.NVIDIA_API_KEY
        self.model = model or Config.NVIDIA_MODEL
        self.api_url = api_url or Config.NVIDIA_API_URL
        self.system_prompt = Config.BUSINESS_CONTEXT

    def sohbet_yaniti_al(self, kullanici_mesaji: str, gecmis: list[dict] | None = None) -> str:
        """
        Sends user message and conversation history to NVIDIA NIM API and returns response text.
        
        :param kullanici_mesaji: New input message from visitor.
        :param gecmis: List of past message dicts [{'role': 'user'|'assistant', 'content': '...'}]
        :return: AI response text.
        :raises AIServiceError: When API call fails or encounters network error.
        """
        if not kullanici_mesaji or not kullanici_mesaji.strip():
            raise AIServiceError("Kullanıcı mesajı boş olamaz.")

        # Prepare messages payload
        messages = [{"role": "system", "content": self.system_prompt}]

        if gecmis:
            for item in gecmis:
                if isinstance(item, dict) and "role" in item and "content" in item:
                    # Sanitize roles
                    role = "user" if item["role"] in ["user", "kullanici"] else "assistant"
                    messages.append({"role": role, "content": item["content"]})

        messages.append({"role": "user", "content": kullanici_mesaji.strip()})

        # Fallback mode if API key is not configured
        if not self.api_key or self.api_key.strip() == "":
            logger.warning("NVIDIA_API_KEY bulunamadı. Mock yanıt modunda çalışılıyor.")
            return self._mock_yanit_uret(kullanici_mesaji)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.55,
            "top_p": 0.95,
            "max_tokens": 4096,
            "stream": False
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"NVIDIA API Hatası [{response.status_code}]: {error_detail}")
                raise AIServiceError(f"NVIDIA API isteği başarısız oldu (Status {response.status_code}): {error_detail}")

            data = response.json()
            ai_message = data["choices"][0]["message"]["content"]
            return ai_message.strip()

        except requests.RequestException as exc:
            logger.error(f"NVIDIA API Bağlantı Hatası: {exc}")
            raise AIServiceError("NVIDIA AI servisine bağlanırken ağ hatası oluştu.", original_exception=exc)
        except (KeyError, IndexError, ValueError) as exc:
            logger.error(f"NVIDIA API Yanıt Parse Hatası: {exc}")
            raise AIServiceError("Yapay zeka yanıtı işlenirken bir biçim hatası oluştu.", original_exception=exc)

    def _mock_yanit_uret(self, kullanici_mesaji: str) -> str:
        """
        Fallback response generator when API key is missing or testing offline.
        """
        msg_lower = kullanici_mesaji.lower()
        if "deprem" in msg_lower or "çanta" in msg_lower or "kit" in msg_lower:
            return (
                "Afet Noktası Akıllı Asistanı: Deprem hazırlık kiti içerisinde 72 saatlik su, "
                "dayanıklı gıda, ilk yardım çantası, el feneri ve düdük bulunmalıdır. "
                "Bölgenize özel afet hazırlık setlerimiz hakkında detaylı bilgi ve size özel teklif "
                "sunmamız için İsim ve Telefon numaranızı bırakmak ister misiniz?"
            )
        elif "risk" in msg_lower or "bölge" in msg_lower or "nerede" in msg_lower:
            return (
                "Afet Noktası olarak bölgenizin zemin durumu ve deprem risk analizini çıkarabiliriz. "
                "Uzman ekibimizin sizinle iletişime geçip risk raporunu iletmesi için adınızı ve "
                "telefon numaranızı form alanından bizimle paylaşabilirsiniz."
            )
        else:
            return (
                "Merhaba! Ben Afet Noktası'nın akıllı asistanıyım. Bulunduğunuz bölgeye göre "
                "afet hazırlık kitleri önerebilir ve hayatta kalma ipuçları verebilirim. "
                "Size özel çözümlerimiz için adınızı ve telefon numaranızı bırakmak ister misiniz?"
            )
