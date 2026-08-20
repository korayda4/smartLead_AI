import re
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app.repositories.lead_repository import LeadRepository
from app.models.lead import Lead
from app.services.ai_service import AIService

main_bp = Blueprint("main", __name__)
_ai = AIService()
_leads = LeadRepository()

_ADMIN_EMAIL = "koray@afetnoktasi.com"
_ADMIN_PASSWORD = "123"
_WIX_URL = "https://koraydemirmc.wixsite.com/afet-noktas/"
_PHONE_RE = re.compile(r"(?:0\s*5\d{2}|5\d{2})[\s\-\.]?\d{3}[\s\-\.]?\d{2}[\s\-\.]?\d{2}|\b\d{10,11}\b")
_NAME_RE = re.compile(r"(?:adım|adim|ismim)\s+([a-zA-ZçğıöşüÇĞİÖŞÜ]+)", re.IGNORECASE)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/hakkimizda")
def hakkimizda():
    return render_template("hakkimizda.html")


@main_bp.route("/kvkk")
def kvkk():
    return render_template("kvkk.html")


@main_bp.route("/gizlilik")
def gizlilik():
    return render_template("gizlilik.html")


@main_bp.route("/cerez-politikasi")
def cerez():
    return render_template("cerez.html")


@main_bp.route("/kullanim-kosullari")
def kullanim_kosullari():
    return render_template("kullanim_kosullari.html")


@main_bp.route("/anasayfa")
def anasayfa_redirect():
    return redirect(_WIX_URL, 302)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect(url_for("main.dashboard")) if session.get("user") else render_template("login.html")
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    if email == _ADMIN_EMAIL and password == _ADMIN_PASSWORD:
        session["user"] = email
        return redirect(url_for("main.dashboard"))
    return render_template("login.html", hata="Hatalı e-posta veya şifre."), 401


@main_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("main.login"))


@main_bp.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("main.login"))
    return render_template("dashboard.html")


@main_bp.route("/api/sohbet", methods=["POST", "OPTIONS"])
def api_sohbet():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json(silent=True) or {}
    mesaj = (data.get("mesaj") or data.get("message") or data.get("prompt") or data.get("text") or "").strip()
    gecmis = data.get("gecmis") or data.get("history") or data.get("messages") or []

    if not mesaj:
        return jsonify({"ok": False, "hata": "Lütfen geçerli bir mesaj yazın."}), 400

    try:
        phone_match = _PHONE_RE.search(mesaj)
        if phone_match:
            name_match = _NAME_RE.search(mesaj)
            name = name_match.group(1).title() if name_match else "Sohbet Ziyaretçisi"
            phone = phone_match.group(0).replace(" ", "").replace("-", "").replace(".", "")
            _leads.ekle(Lead(isim=name, telefon=phone, mesaj=f"Sohbet: {mesaj}"))
    except Exception:
        pass

    try:
        yanit = _ai.sohbet_yaniti_al(kullanici_mesaji=mesaj, gecmis=gecmis)
        return jsonify({"ok": True, "yanit": yanit}), 200
    except Exception:
        return jsonify({"ok": True, "yanit": "Şu anda kısa süreli bir yoğunluk var, lütfen tekrar deneyin."}), 200


@main_bp.route("/api/leads", methods=["POST", "OPTIONS"])
def api_lead_olustur():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json(silent=True) or {}
    isim = data.get("isim", "").strip()
    telefon = data.get("telefon", "").strip()
    mesaj = data.get("mesaj", "").strip()

    if not isim or not telefon:
        return jsonify({"ok": False, "hata": "İsim ve Telefon alanları zorunludur."}), 400

    try:
        lead_id = _leads.ekle(Lead(isim=isim, telefon=telefon, mesaj=mesaj))
        return jsonify({"ok": True, "mesaj": "Bilgileriniz alındı.", "lead_id": lead_id}), 201
    except Exception as err:
        return jsonify({"ok": False, "hata": str(err)}), 500


@main_bp.route("/api/leads", methods=["GET"])
def api_lead_listele():
    try:
        leadler = _leads.hepsini_getir()
        return jsonify({"ok": True, "toplam": len(leadler), "data": leadler})
    except Exception as err:
        return jsonify({"ok": False, "hata": str(err)}), 500
