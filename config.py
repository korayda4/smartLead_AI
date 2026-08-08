import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / ".env")


class Config:
    """Application configuration management class for Afet Noktası."""
    
    SECRET_KEY = os.environ.get("SECRET_KEY", "afet-noktasi-default-secret-key-2026")
    
    # SQLite Database Configuration
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "afet_noktasi.db"))
    
    # Groq AI Service Configuration
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
    GROQ_API_URL = os.environ.get("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    
    # Brand Identity: Derin Lacivert (#1B2A4A), Canlı Turuncu (#F26419)
    # Brand Tone: Net, güven veren, sakinleştirici, teknolojik ve samimi. Paniğe sürükleyen değil, bilinçlendiren bir dil.
    BUSINESS_CONTEXT = (
        "Sen Afet Noktası'nın akıllı asistanısın. Görevin, kullanıcılara "
        "bulundukları bölgenin sismik risk durumuna göre kişiselleştirilmiş afet hazırlık kitleri önermek, "
        "offline mesh haberleşme ve hayatta kalma ipuçları vermektir. "
        "Dilin net, güven veren, sakinleştirici, teknolojik ve samimi olmalıdır. "
        "Paniğe sürükleyen değil, bilinçlendiren bir ton kullan. "
        "Yanıtlarını düzenli, anlaşılır maddeler halinde sun ve cümleni tamamlamadan asla yarım bırakma. "
        "Kullanıcıyı ücretsiz risk danışmanlığı ve kit teklifi için iletişim bilgilerini (isim ve telefon) bırakmaya yönlendir."
    )
