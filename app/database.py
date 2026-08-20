from app.repositories.lead_repository import LeadRepository

_repo = LeadRepository()


def init_db():
    _repo.init()


def lead_ekle(isim: str, telefon: str, mesaj: str = "") -> int:
    from app.models.lead import Lead
    return _repo.ekle(Lead(isim=isim, telefon=telefon, mesaj=mesaj))


def tum_leadler() -> list[dict]:
    return _repo.hepsini_getir()


def get_db():
    return _repo._connect()
