from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app.database import lead_ekle, tum_leadler
from app.services.ai_service import AIService, AIServiceError

main_bp = Blueprint("main", __name__)
ai_service = AIService()

# Hardcoded MVP Administrator Credentials
ADMIN_EMAIL = "koray@afetnoktasi.com"
ADMIN_PASSWORD = "123"


@main_bp.route("/", methods=["GET"])
def index():
    """
    Renders the public Afet Noktası Landing Page & AI Assistant Modal.
    """
    return render_template("index.html")


@main_bp.route("/hakkimizda", methods=["GET"])
def hakkimizda():
    """
    Renders the official Hakkımızda & Marka Hikayesi page.
    """
    return render_template("hakkimizda.html")


@main_bp.route("/kvkk", methods=["GET"])
def kvkk():
    """
    Renders the official KVKK Aydınlatma Metni page.
    """
    return render_template("kvkk.html")


@main_bp.route("/gizlilik", methods=["GET"])
def gizlilik():
    """
    Renders the official Gizlilik Politikası page.
    """
    return render_template("gizlilik.html")


@main_bp.route("/cerez-politikasi", methods=["GET"])
def cerez():
    """
    Renders the official Çerez Politikası page.
    """
    return render_template("cerez.html")


@main_bp.route("/kullanim-kosullari", methods=["GET"])
def kullanim_kosullari():
    """
    Renders the official Kullanım Koşulları page.
    """
    return render_template("kullanim_kosullari.html")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Renders login template or processes administrator login credentials.
    """
    if request.method == "GET":
        if session.get("user"):
            return redirect(url_for("main.dashboard"))
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session["user"] = email
        return redirect(url_for("main.dashboard"))

    return render_template("login.html", hata="Hatalı e-posta veya şifre."), 401


@main_bp.route("/logout", methods=["GET"])
def logout():
    """
    Logs out the current administrator session.
    """
    session.pop("user", None)
    return redirect(url_for("main.login"))


@main_bp.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Renders the Lead Management Dashboard for authenticated administrators.
    Redirects to /login if user is not authenticated in session.
    """
    if not session.get("user"):
        return redirect(url_for("main.login"))
    return render_template("dashboard.html")


@main_bp.route("/api/sohbet", methods=["POST", "OPTIONS"])
def api_sohbet():
    """
    API Endpoint for processing visitor chat messages via AI Service.
    Expects JSON: { "mesaj": string, "gecmis": list }
    """
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json(silent=True) or {}
    mesaj = data.get("mesaj", "").strip()
    gecmis = data.get("gecmis", [])

    if not mesaj:
        return jsonify({
            "ok": False,
            "hata": "Lütfen geçerli bir mesaj yazın."
        }), 400

    try:
        yanit = ai_service.sohbet_yaniti_al(kullanici_mesaji=mesaj, gecmis=gecmis)
        return jsonify({
            "ok": True,
            "yanit": yanit
        })
    except AIServiceError as err:
        return jsonify({
            "ok": False,
            "hata": str(err)
        }), 502
    except Exception as err:
        return jsonify({
            "ok": False,
            "hata": "Sohbet işlenirken beklenmeyen bir hata oluştu."
        }), 500


@main_bp.route("/api/leads", methods=["POST", "OPTIONS"])
def api_lead_olustur():
    """
    API Endpoint for saving visitor contact details (name, phone, message).
    Expects JSON: { "isim": string, "telefon": string, "mesaj": string }
    """
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json(silent=True) or {}
    isim = data.get("isim", "").strip()
    telefon = data.get("telefon", "").strip()
    mesaj = data.get("mesaj", "").strip()

    if not isim or not telefon:
        return jsonify({
            "ok": False,
            "hata": "İsim ve Telefon alanları zorunludur."
        }), 400

    try:
        lead_id = lead_ekle(isim=isim, telefon=telefon, mesaj=mesaj)
        return jsonify({
            "ok": True,
            "mesaj": "İletişim bilgileriniz başarıyla alındı. Uzmanlarımız sizinle iletişime geçecektir.",
            "lead_id": lead_id
        }), 201
    except Exception as err:
        return jsonify({
            "ok": False,
            "hata": f"Lead kaydedilirken veritabanı hatası oluştu: {str(err)}"
        }), 500


@main_bp.route("/api/leads", methods=["GET", "OPTIONS"])
def api_lead_listele():
    """
    API Endpoint returning all saved leads for the dashboard.
    """
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    try:
        leadler = tum_leadler()
        return jsonify({
            "ok": True,
            "toplam": len(leadler),
            "data": leadler
        })
    except Exception as err:
        return jsonify({
            "ok": False,
            "hata": f"Kayıtlar çekilirken bir hata oluştu: {str(err)}"
        }), 500
