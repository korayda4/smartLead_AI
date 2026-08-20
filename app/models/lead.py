from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Lead:
    isim: str
    telefon: str
    mesaj: str = ""
    status: str = "Yeni"
    id: Optional[int] = field(default=None)
    created_at: Optional[str] = field(default=None)
