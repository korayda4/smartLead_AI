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
        """
        if not kullanici_mesaji or not kullanici_mesaji.strip():
            return "Lütfen sormak istediğiniz konuyu yazın."

        # Fallback mode if API key is not configured
        if not self.api_key or self.api_key.strip() == "":
            logger.warning("NVIDIA_API_KEY bulunamadı. Mock yanıt modunda çalışılıyor.")
            return self._mock_yanit_uret(kullanici_mesaji)

        # Prepare messages payload
        messages = [{"role": "system", "content": self.system_prompt}]

        if gecmis:
            for item in gecmis:
                if isinstance(item, dict) and "role" in item and "content" in item:
                    # Sanitize roles
                    role = "user" if item["role"] in ["user", "kullanici"] else "assistant"
                    messages.append({"role": role, "content": item["content"]})

        messages.append({"role": "user", "content": kullanici_mesaji.strip()})

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
                timeout=18
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"NVIDIA API Hatası [{response.status_code}]: {error_detail}")
                return self._mock_yanit_uret(kullanici_mesaji)

            data = response.json()
            choices = data.get("choices", [])
            if choices and "message" in choices[0] and "content" in choices[0]["message"]:
                ai_message = choices[0]["message"]["content"]
                return ai_message.strip()
            else:
                logger.warning("NVIDIA API yanıtında choices içeriği eksik.")
                return self._mock_yanit_uret(kullanici_mesaji)

        except requests.RequestException as exc:
            logger.error(f"NVIDIA API Bağlantı/Zaman Aşımı Hatası: {exc}")
            return self._mock_yanit_uret(kullanici_mesaji)
        except Exception as exc:
            logger.error(f"NVIDIA API İşleme Hatası: {exc}")
            return self._mock_yanit_uret(kullanici_mesaji)

    def _mock_yanit_uret(self, kullanici_mesaji: str) -> str:
        """
        Fallback response generator when API key is missing or testing offline.
        """
        msg_lower = kullanici_mesaji.lower()
        if "deprem" in msg_lower or "çanta" in msg_lower or "kit" in msg_lower:
            return (
                "Afet Noktası Akıllı Asistanı: 72 saatlik deprem ve afet kiti içerisinde "
                "kişi başı su, dayanıklı gıda, ilk yardım seti, el feneri, düdük ve acil durum radyosu yer almalıdır.\n\n"
                "Bölgenize ve ailenize özel afet hazırlık setlerimiz hakkında detaylı bilgi almak ve size özel teklif sunmamız "
                "için İsim ve Telefon numaranızı form üzerinden bizimle paylaşabilirsiniz."
            )
        elif "mesh" in msg_lower or "haberleşme" in msg_lower or "internet" in msg_lower:
            return (
                "Afet Noktası Offline Mesh Teknolojisi, afet anında GSM baz istasyonları ve internet çökse dahi "
                "cihazların birbirine bağlanarak yerel, kesintisiz bir iletişim ağı kurmasını sağlar.\n\n"
                "Bu teknoloji ve hazırlık çözümlerimiz hakkında detaylı bilgi için iletişim bilgilerinizi iletebilirsiniz."
            )
        elif "risk" in msg_lower or "bölge" in msg_lower or "kadıköy" in msg_lower or "istanbul" in msg_lower or "nerede" in msg_lower:
            return (
                "Afet Noktası olarak bulunduğunuz konumun zemin durumu ve sismik risk analizini yapıyoruz.\n\n"
                "Uzman ekibimizin sizinle iletişime geçip detaylı risk raporu sunması için adınızı ve "
                "telefon numaranızı form alanından bizimle paylaşabilirsiniz."
            )
        else:
            return (
                "Merhaba! Ben Afet Noktası'nın resmi Afet Hazırlık ve Güvenlik Danışmanıyım.\n\n"
                "Bulunduğunuz bölgeye özel sismik risk değerlendirmesi yapabilir, 72 saatlik afet kitleri ve "
                "offline mesh haberleşme teknolojimiz hakkında bilgi verebilirim.\n\n"
                "Size özel ücretsiz risk raporu ve kit teklifimiz için adınızı ve telefon numaranızı bırakmak ister misiniz?"
            )
