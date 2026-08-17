import re
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

    def _temizle_yanit(self, text: str) -> str:
        """
        Removes any accidental robotic prefix or label like 'Afet Noktası Asistanı:' or 'Asistan:' from the output.
        """
        if not text:
            return ""
        
        # Regex removing unwanted prefix labels at the start of output
        pattern = r"^(?:Afet\s*Noktas[ıi](?:'n[ıi]n)?\s*(?:Ak[ıi]ll[ıi]\s*)?(?:Asistan[ıi]|Dan[ıi][şs]man[ıi])|Asistan|Assistant|Dan[ıi][şs]man|AI|Bot)\s*:\s*"
        cleaned = re.sub(pattern, "", text.strip(), flags=re.IGNORECASE)
        return cleaned.strip()

    def sohbet_yaniti_al(self, kullanici_mesaji: str, gecmis: list[dict] | None = None) -> str:
        """
        Sends user message and conversation history to NVIDIA NIM API and returns response text.
        
        :param kullanici_mesaji: New input message from visitor.
        :param gecmis: List of past message dicts [{'role': 'user'|'assistant', 'content': '...'}]
        :return: AI response text.
        """
        if not kullanici_mesaji or not str(kullanici_mesaji).strip():
            return "Lütfen sormak istediğiniz konuyu yazın."

        msg_clean = str(kullanici_mesaji).strip()

        # Fallback mode if API key is not configured
        if not self.api_key or self.api_key.strip() == "":
            logger.warning("NVIDIA_API_KEY bulunamadı. Mock yanıt modunda çalışılıyor.")
            return self._mock_yanit_uret(msg_clean, gecmis)

        # Prepare messages payload with system prompt
        messages = [{"role": "system", "content": self.system_prompt}]

        # Append multi-turn history with robust format parsing
        if gecmis and isinstance(gecmis, list):
            for item in gecmis:
                if isinstance(item, dict):
                    # Extract text content from various possible frontend keys
                    content = (
                        item.get("content")
                        or item.get("text")
                        or item.get("mesaj")
                        or item.get("message")
                        or ""
                    )
                    # Extract role/sender
                    raw_role = (
                        item.get("role")
                        or item.get("sender")
                        or item.get("author")
                        or item.get("type")
                        or "user"
                    )
                    role = "user" if str(raw_role).lower() in ["user", "kullanici", "human", "client", "siz", "me"] else "assistant"
                    
                    if content and str(content).strip():
                        messages.append({"role": role, "content": str(content).strip()})

        # Append current user message
        messages.append({"role": "user", "content": msg_clean})

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
                return self._mock_yanit_uret(msg_clean, gecmis)

            data = response.json()
            choices = data.get("choices", [])
            if choices and "message" in choices[0] and "content" in choices[0]["message"]:
                ai_message = choices[0]["message"]["content"]
                return self._temizle_yanit(ai_message)
            else:
                logger.warning("NVIDIA API yanıtında choices içeriği eksik.")
                return self._mock_yanit_uret(msg_clean, gecmis)

        except requests.RequestException as exc:
            logger.error(f"NVIDIA API Bağlantı/Zaman Aşımı Hatası: {exc}")
            return self._mock_yanit_uret(msg_clean, gecmis)
        except Exception as exc:
            logger.error(f"NVIDIA API İşleme Hatası: {exc}")
            return self._mock_yanit_uret(msg_clean, gecmis)

    def _mock_yanit_uret(self, kullanici_mesaji: str, gecmis: list[dict] | None = None) -> str:
        """
        Fallback response generator when API key is missing or testing offline.
        Handles name/phone sharing, multi-turn context and topics gracefully.
        """
        msg_lower = kullanici_mesaji.lower()

        # Check if user shared name or phone number
        has_phone = bool(re.search(r"(?:0\s*5\d{2}|5\d{2})[\s\-\.]?\d{3}[\s\-\.]?\d{2}[\s\-\.]?\d{2}|\b\d{10,11}\b", msg_lower))
        has_name = any(kw in msg_lower for kw in ["adım", "adim", "ismim", "benim adım", "ben "])

        if has_phone or has_name:
            # Extract name if possible
            name_match = re.search(r"(?:adım|adim|ismim)\s+([a-zA-ZçğıöşüÇĞİÖŞÜ]+)", kullanici_mesaji, re.IGNORECASE)
            name_str = f" {name_match.group(1).title()}" if name_match else ""
            return (
                f"Teşekkürler{name_str}, iletişim bilgilerinizi kaydettim.\n\n"
                "Afet ve risk danışmanlarımız bölgenize özel detaylı sismik analiz raporu ve kişiselleştirilmiş "
                "afet hazırlık kit teklifimizi iletmek üzere en kısa sürede sizinle iletişime geçecektir.\n\n"
                "Bu süreçte afet çantası veya offline mesh haberleşme hakkında sormak istediğiniz başka bir detay var mı?"
            )

        if "deprem" in msg_lower or "çanta" in msg_lower or "kit" in msg_lower:
            return (
                "72 saatlik tam donanımlı bir afet ve deprem hazırlık çantası içerisinde;\n\n"
                "- **Temel Yaşam:** Kişi başı günlük en az 3 litre su, yüksek kalorili dayanıklı gıdalar\n"
                "- **İlk Yardım & Sağlık:** Kapsamlı ilk yardım seti, reçeteli ilaçlar, toz maskesi\n"
                "- **Güvenlik & İletişim:** Dinamolu veya pilli el feneri, yüksek sesli düdük, acil durum radyosu, powerbank\n"
                "- **Kişisel:** Kimlik fotokopileri, nakit para ve çok amaçlı çakı\n\n"
                "Ailenizin büyüklüğüne ve bulunduğunuz bölgenin ihtiyaçlarına özel indirimli afet kitlerimizi incelemek ve ücretsiz danışmanlık almak için ekrandaki formdan iletişim bilgilerinizi iletebilirsiniz."
            )
        elif "mesh" in msg_lower or "haberleşme" in msg_lower or "internet" in msg_lower or "bluetooth" in msg_lower or "wifi" in msg_lower or "bt" in msg_lower:
            return (
                "**İnternetsiz Bluetooth (BT) ve Wi-Fi Mesh Haber Ağı**;\n\n"
                "Deprem ve yangın gibi afetlerde GSM şebekeleri ve internet çökse dahi telefonların birbirine doğrudan bağlanarak zincirleme bir iletişim köprüsü kurmasını sağlar.\n\n"
                "- **Afetzede Modu:** Mahsur kalan veya enkaz altındaki vatandaşlar tek tuşla internetsiz SOS, hayati durum ve konum sinyali yayabilir.\n"
                "- **Kurtarıcı Modu:** Arama-kurtarma ekipleri ve yakındaki yardımseverler, afetzedelerin yaydığı Bluetooth/Wi-Fi sinyallerini tarayıp yer tespiti yapabilir ve müdahaleyi koordine edebilir.\n\n"
                "Bu hayati teknoloji ve ailenize özel afet hazırlık çözümlerimiz hakkında detaylı bilgi almak için ekrandaki mini formdan bilgilerinizi iletebilirsiniz."
            )
        elif "yangın" in msg_lower or "yangin" in msg_lower or "risk" in msg_lower or "bölge" in msg_lower or "kadıköy" in msg_lower or "istanbul" in msg_lower or "nerede" in msg_lower:
            return (
                "**Afet Noktası Erken Uyarı ve Risk Analizi**;\n\n"
                "Bulunduğunuz konumun fay hatlarına yakınlığı, zemin yapısı, sismik risk durumu ve yangın tahliye rotalarına dair önceden uyarı ve rehberlik sağlar.\n\n"
                "Bölgenize özel detaylı deprem ve yangın risk analiz raporunu iletmemiz ve uygun önlemleri birlikte planlamamız için ekrandaki mini formdan adınızı ve telefon numaranızı paylaşabilirsiniz."
            )
        else:
            return (
                "Afet öncesi erken uyarı (deprem ve yangın), internetsiz **Bluetooth ve Wi-Fi Mesh** haberleşme ağı (Kurtarıcı ve Afetzede modları) ve 72 saatlik hayatta kalma kitlerimiz hakkında size rehberlik etmek için buradayım.\n\n"
                "Ailenize ve bölgenize özel ücretsiz afet risk raporu ve kit teklifi almak için ekrandaki mini formu doldurabilir veya ad-soyad ve telefon numaranızı iletebilirsiniz."
            )
