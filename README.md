# 🚀 URL Shortener Service

A **fast** and **efficient** URL shortener built with [FastAPI](https://fastapi.tiangolo.com/), using Brotli compression and Base62 encoding for ultra-compact, URL-safe codes.

---

## ✨ Features

- 🔗 **Shortens long URLs** into compact, shareable codes
- ⚡ **Domain shortcuts** for popular sites (e.g., `google.com` → `g`)
- 🏷️ **Subdomain & TLD shortcuts** (e.g., `www` → `w`, `.com` → `c`)
- 🗜️ **Brotli compression** for path components
- 🔢 **Base62 encoding** for URL-safe output
- 🚀 **Lightweight & blazing fast**

---

## 📚 API Endpoints

### 🔒 Encode a URL

**POST** `/encode`

**Request:**
```json
{
  "url": "https://www.example.com/some/long/path"
}
```

**Response:**
```json
{
  "code": "s_w.example.c_2yZ..."
}
```

---

### 🔓 Decode a Shortened Code

**GET** `/decode/{code}`

**Example:** `/decode/s_w.example.c_2yZ...`

**Response:**
```json
{
  "url": "https://www.example.com/some/long/path"
}
```

---

## 🏷️ Domain Shortcuts

| Domain         | Shortcut |
| -------------- | :------: |
| google.com     |    g     |
| youtube.com    |    y     |
| facebook.com   |    f     |
| github.com     |   gh     |
| openai.com     |   oa     |

---

### 🏷️ Subdomain & TLD Shortcuts

**Subdomains:**

| Subdomain | Shortcut |
| --------- | :------: |
| www       |    w     |
| blog      |    b     |
| mail      |    m     |

**TLDs:**

| TLD    | Shortcut |
| ------ | :------: |
| com    |    c     |
| org    |    o     |
| net    |    n     |
| io     |    i     |
| co.uk  |   uk     |

---

## 🌐 Hosting

**Live Demo:**
[https://urlshortner-ru2l.onrender.com/](https://urlshortner-ru2l.onrender.com/)

---

## ⚙️ Technical Details

- 🐍 Built with **Python** & **FastAPI**
- 🗜️ **Brotli** compression for path components
- 🔢 **Base62** encoding for URL-safe output
- ⚡ **Lightweight** and **fast**

---

## 💡 Example Usage

### Encode

```bash
curl -X POST "https://urlshortner-ru2l.onrender.com/encode" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.google.com/search?q=fastapi"}'
```

### Decode

```bash
curl "https://urlshortner-ru2l.onrender.com/decode/s_g_8Ht..."
```

---

## 🏃‍♂️ Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/urlshortner.git
   cd urlshortner
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI app:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Visit:**
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive API docs.

---
