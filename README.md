# Echo Chat Bot

Antarmuka chat ringan berbasis React + Vite dengan backend Python sederhana yang terhubung ke Gemini. Repositori ini sudah dipisah dari proyek asal dan siap untuk dikembangkan atau dideploy menggunakan akun kamu sendiri.

## Struktur Proyek

- `src/` – frontend React/TypeScript.
- `public/robot-icon.svg` – ikon tab browser.
- `testbackend/` – server WebSocket Python yang meneruskan permintaan ke Gemini.
- `.env` (opsional) – variabel lingkungan lokal (tidak dipush, gunakan `.env.example` sebagai referensi).

## Persiapan Lingkungan

1. **Frontend**
   ```bash
   npm install
   ```

2. **Backend**
   ```bash
   cd testbackend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Salin `.env.example` menjadi `.env` lalu isi nilai yang diperlukan:
   ```
   GEMINI_API_KEY=AIza...        # ganti dengan API key milikmu
   GEMINI_MODEL=gemini-2.5-flash # atau model lain yang memang tersedia
   PORT=8090
   VITE_WS_ENDPOINT=             # kosongkan saat local dev
   ```

## Menjalankan Secara Lokal

Frontend dan backend dijalankan terpisah.

```bash
# terminal 1 – backend
cd testbackend
source venv/bin/activate
python test.py

# terminal 2 – frontend
npm run dev
```

Aplikasi dapat diakses di `http://localhost:5173`. Frontend otomatis menyambung ke `ws://localhost:8090` jika `VITE_WS_ENDPOINT` tidak diisi.

## Tips

- Jangan commit file `.env` yang berisi secret (sudah di-ignore).
- Jika backend tidak merespons atau memunculkan error 404 model, cek daftar model dengan:
  ```bash
  python - <<'PY'
  import os, google.generativeai as genai
  genai.configure(api_key=os.environ["GEMINI_API_KEY"])
  for model in genai.list_models():
      methods = getattr(model, "supported_generation_methods", [])
      if "generateContent" in methods:
          print(model.name)
  PY
  ```
- Untuk pengujian manual WebSocket bisa gunakan `wscat` atau extension VSCode *WebSocket Client*.

Selamat membangun Echo Chat Bot!
