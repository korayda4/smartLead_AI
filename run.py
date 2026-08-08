import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀 Afet Noktası Akıllı Asistan Sunucusu Başlatılıyor...")
    print(f"📍 Sohbet Arayüzü: http://127.0.0.1:{port}/")
    print(f"📊 Admin Gösterge Paneli: http://127.0.0.1:{port}/dashboard\n")
    app.run(host="0.0.0.0", port=port, debug=True)
