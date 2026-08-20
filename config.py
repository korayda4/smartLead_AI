import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "afet-noktasi-default-secret-key-2026")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "afet_noktasi.db"))
    NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY") or os.environ.get("GROQ_API_KEY") or "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"
    NVIDIA_MODEL = os.environ.get("NVIDIA_MODEL", "minimaxai/minimax-m3")
    NVIDIA_API_URL = os.environ.get("NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
    BUSINESS_CONTEXT = (
        "Afet Noktası danışmanısın. Ürünler: deprem/yangın erken uyarı, internetsiz BT/Wi-Fi Mesh haberleşme, 72s afet kiti.\n"
        "Kurallar:\n"
        "1. Max 2-3 kısa cümle. Etiket/unvan kullanma. 'Siz' dili kullan.\n"
        "2. Kullanıcıdan hiçbir kişisel bilgi (ad, soyad, telefon, e-posta vb.) ASLA isteme.\n"
        "3. Sadece ürün ve hizmetler hakkında bilgi ver."
    )
