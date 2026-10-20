# OmniParse AI - RapidAPI Listeleme & Kurulum Rehberi

Bu rehber, bu API'yi **0 TL harcayarak** canlıya alıp RapidAPI'de satışa açman için adım adım hazırlandı.

---

## 1. Adım: API'yi Ücretsiz Canlıya Alma (Render.com)
RapidAPI'nin servise erişebilmesi için ücretsiz bir HTTPS linkine ihtiyacımız var.

1. [GitHub.com](https://github.com)'a gir ve `omniparse-ai-api` adında yeni bir gizli veya açık repo aç.
2. Bu klasördeki (`rapidapi-micro-apis/01-ai-reader-api`) dosyaları repoya yükle.
3. [Render.com](https://render.com)'a ücretsiz üye ol.
4. **"New +" -> "Web Service"** seç.
5. GitHub reponu bağla.
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free ($0)
6. **"Create Web Service"** butonuna bas. 2-3 dakika içinde sana `https://omniparse-ai-xxxx.onrender.com` şeklinde ücretsiz bir link verecek.

---

## 2. Adım: RapidAPI'ye Ekleme
1. [RapidAPI.com](https://rapidapi.com)'a git ve "My APIs" -> **"Add New API"** butonuna tıkla.
2. Formu şu şekilde doldur:
   - **API Name:** `OmniParse - Web to Clean Markdown & LLM Reader`
   - **Short Description:** `Ultra-fast article & webpage extractor optimized for AI LLMs, RAG, and agents. Returns clean Markdown with metadata in milliseconds.`
   - **Category:** `Artificial Intelligence` veya `Data`
3. Sol menüden **"Hub Listing"** -> **"Target URL"** kısmına Render'ın verdiği linki yapıştır (örn: `https://omniparse-ai-xxxx.onrender.com`).

---

## 3. Adım: Endpoint Tanımlama (Endpoints Sekmesi)
* **Create REST Endpoint** butonuna bas.
  - **Name:** `Extract Clean Markdown`
  - **Method:** `GET`
  - **Path:** `/api/v1/extract`
  - **Parameters:**
    - `url` (Query, Required, String) -> Örnek değer: `https://en.wikipedia.org/wiki/Artificial_intelligence`
    - `format` (Query, Optional, String) -> Varsayılan: `markdown`
    - `include_images` (Query, Optional, Boolean) -> Varsayılan: `true`

---

## 4. Adım: Fiyatlandırma Paketleri (Plans & Pricing)
RapidAPI'de en çok kazandıran standart freemium şablon:

| Paket | Fiyat | Dahil İstek | Aşım Ücreti (Overage) |
|---|---|---|---|
| **BASIC (Free)** | \$0 / ay | 100 istek / ay | \$0.01 / istek |
| **PRO** | \$14.99 / ay | 5,000 istek / ay | \$0.005 / istek |
| **ULTRA** | \$39.99 / ay | 25,000 istek / ay | \$0.002 / istek |
| **MEGA** | \$89.99 / ay | 100,000 istek / ay | \$0.001 / istek |

---

## Neden Bu API Çok Satacak?
1. **Hız:** Bellekleme (caching) sayesinde mükerrer çağrılarda **<5 ms** yanıt döner.
2. **LLM Dostu:** Gereksiz HTML etiketlerini ve JavaScript çöplerini atarak OpenAI/Claude token maliyetini %70 azaltır.
3. **Sıfır Bakım:** Hedef sitelerden ban yemez, tarayıcı başlıklarıyla (User-Agent emulation) engelleri aşar.
