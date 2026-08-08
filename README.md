# 🛡️ Afet Noktası - Akıllı Afet Hazırlık & Satış Asistanı Platformu

**Afet Noktası**, doğal afetler öncesinde ve anında hayati öneme sahip sismik risk verileri sunan, **Offline Mesh** (internetsiz haberleşme) altyapısını destekleyen ve bünyesindeki **Groq AI (Llama-3.1)** destekli Akıllı Asistan ile kullanıcılara kişiselleştirilmiş 72 saatlik deprem çantası çözümleri sunan mobil dijital platform web MVP projesidir.

---

## 🏛️ Mimari Yapı ve Modüller (SOLID & Separation of Concerns)

Proje kurumsal modüler mimariye tam uyumlu olarak geliştirilmiştir. İş mantığı, veritabanı sorguları ve yapay zeka istekleri birbirinden kesin çizgilerle izole edilmiştir:

```
smartlead_ai/
├── run.py                 # Sunucuyu başlatan ana giriş noktası
├── config.py              # Uygulama ayarları, .env okuyucu ve marka prompt yönetimi
├── requirements.txt       # Bağımlılıklar (Flask, requests, python-dotenv)
├── .env.example           # Örnek çevre değişkenleri şablonu
├── .gitignore             # Güvenlik ve venv yok sayma kuralları
└── app/
    ├── __init__.py        # create_app() fabrika fonksiyonu ve SQLite ilklendirmesi
    ├── database.py        # SQLite işlemleri (SADECE parametreli SQL sorguları)
    ├── routes.py          # HTTP rotaları (SADECE yönlendirme & oturum kontrolü)
    ├── templates/
    │   ├── index.html     # Ziyaretçi Landing Page & Yüzen AI Asistan Modalı
    │   ├── login.html     # Korumalı Yönetici Giriş Ekranı (Minimalist 2D)
    │   └── dashboard.html # F-Pattern UX Bağımsız Yönetim Paneli
    └── services/
        ├── __init__.py
        └── ai_service.py  # Groq API entegrasyonu (AIService & AIServiceError)
```

---

## ✨ Öne Çıkan Özellikler

### 1. Ziyaretçi Landing Page (`/`)
- **3D Telefon Görseli ve Ürün Sunumu:** Şık ve etkileşimli mobil uygulama tanıtımı.
- **Temel Teknolojiler:** Offline Mesh haberleşme, sismik risk takibi ve 72 saatlik acil durum kitleri.
- **Ziyaretçi İzolasyonu:** Ziyaretçi arayüzünde yönetim paneline dair hiçbir buton veya yönlendirme izi yer almaz.

### 2. Yüzen Yapay Zeka Asistanı Modalı (Floating AI Modal)
- **Groq Llama-3.1 Entegrasyonu:** Hızlı ve doğal Türkçe yanıt üretimi.
- **Çoklu Tur Sohbet Hafızası (Multi-Turn Chat Memory):** Yapay zeka kullanıcının önceki mesajlarını ve bölgesel bilgilerini unutmaz.
- **Zengin Metin Ayrıştırma (`marked.js`):** Liste maddeleri, kalın yazılar ve başlıklar düzenli HTML formatında sunulur.
- **Entegre İletişim Formu:** Ziyaretçilerin doğrudan sohbet modülü üzerinden ücretsiz risk ve kit teklifi bırakabilmesi.

### 3. Korumalı Yönetim Paneli & CRM (`/dashboard`)
- **Güvenli Oturum Kontrolü (`/login`):** Flask Session tabanlı oturum koruması. Oturum açmamış istekler doğrudan giriş sayfasına yönlendirilir.
- **F-Pattern UX Tablo Tasarımı:** İnsan gözünün ekran tarama alışkanlığına uygun olarak en önemli veri olan **Müşteri Adı** tablonun en solundaki 1. Kolonda konumlandırılmıştır.
- **Dinamik API Entegrasyonu:** `GET /api/leads` rotasından canlı veri çekme, anlık metin araması, CSV dışa aktarımı ve müşteri detay inceleme modalı.

---

## 🔒 Güvenlik Prensipleri

1. **SQL Injection Koruması:** `app/database.py` içerisindeki tüm sorgularda strictly `?` parametre yer tutucuları kullanılmıştır.
2. **Hassas Veri Koruması:** API anahtarları ve gizli veriler `.env` dosyasında tutulur ve versiyon kontrolüne (git) dahil edilmez.
3. **Yönlendirme Koruması:** Yönetim paneli rotaları (`/dashboard`) oturum doğrulamasız erişime kapalıdır.

---

## 🚀 Hızlı Başlangıç

### 1. Depoyu Klonlayın ve Sanal Ortamı Oluşturun
```bash
git clone https://github.com/korayda4/smartLead_AI.git
cd smartLead_AI
python -m venv venv
.\venv\Scripts\activate  # Windows
```

### 2. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 3. `.env` Dosyasını Yapılandırın
`.env.example` dosyasını kopyalayarak `.env` oluşturun ve Groq API anahtarınızı tanımlayın:
```env
SECRET_KEY=afet-noktasi-secret-key-2026
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
DATABASE_PATH=afet_noktasi.db
```

### 4. Uygulamayı Çalıştırın
```bash
python run.py
```
- **Ziyaretçi Arayüzü:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Yönetici Girişi:** [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)

---

## 📝 Lisans ve Marka Bilgisi
Afet Noktası Proje Başlatma Belgesi (Brand Charter) standartlarına uygun olarak tasarlanmıştır. Tüm hakları saklıdır.
