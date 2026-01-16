# 📚 Dokumentasi Lengkap Terry AI Assistant

## 🎯 Ringkasan Aplikasi

**Terry** adalah asisten AI berbasis suara dan teks yang dirancang untuk Windows dan Linux. 
Aplikasi ini menggabungkan teknologi speech recognition, text-to-speech, 
dan multiple AI providers untuk memberikan pengalaman interaksi yang natural dan responsif.

---

## 🎨 Fungsi Utama Aplikasi

### 1. **Voice Assistant (Asisten Suara)**
- **Speech Recognition**: Mendengarkan perintah suara pengguna menggunakan Google Speech Recognition API
- **Text-to-Speech**: Mengkonversi respons AI menjadi suara menggunakan Microsoft Edge TTS (Bahasa Indonesia)
- **Wake Word Detection**: Mengaktifkan dengan kata pemicu seperti "Terry", "Halo", "Buka", dll.

### 2. **Auto-Update AI Brain**
Aplikasi mendukung **Auto-Discovery** untuk mendeteksi model terbaru secara otomatis:
- **Google Gemini** (Prioritas 1): Otomatis mendeteksi model `gemini-*` terbaru.
- **OpenRouter** (Prioritas 2): Otomatis mengambil daftar model gratis (Free Tier).
- **Perplexity AI**: `sonar`, `sonar-pro` (Manual config).
- **DeepSeek Chat**: Alternatif AI provider.
- **Groq**: Otomatis mendeteksi model (Llama 3, Mixtral, dll).
- **Ollama (Local)**: Otomatis mendeteksi model yang terinstall (`ollama list`).
- **Fallback**: Google Search jika semua provider gagal

### 3. **Sistem Aksi Lokal (Local Actions)**
Aksi yang dieksekusi tanpa menggunakan AI (hemat kuota & cepat):
- **Membuka Aplikasi**: `"Buka Notepad"`, `"Buka Chrome"`
- **Membuka Website**: `"Buka google.com"`
- **Memutar YouTube**: `"Putar lagu [judul]"` - Mencari dan memutar video di YouTube
- **Waktu & Tanggal**: `"Jam berapa sekarang?"`, `"Tanggal berapa?"`
- **Kontrol Volume**: `"Besarkan suara"`, `"Kecilkan suara"`, `"Mute"`
- **Media Control**: `"Pause"`, `"Resume"`, `"Skip"`, `"Next"`
- **Cek Server**: `"Cek server"` - Ping server untuk mengecek status
- **Internet Speed Test**: `"Tes internet"` - Membuka fast.com

### 4. **Fitur Visual**
- **Generate Image**: `"Buatkan gambar [deskripsi]"` - Generate gambar dan tampilkan di overlay popup (bukan buka app foto).
- **Web Screenshot**: `"Screenshot [url]"` - Menangkap layar website

### 5. **Pencarian Internet**
- **DuckDuckGo Search**: Mencari informasi dari internet untuk konteks AI
- **Keywords**: `"Cari [query]"`, `"Siapa [nama]"`, `"Berapa harga [barang]"`, dll.

### 6. **Web Dashboard**
- **FastAPI Server**: Dashboard web di port 8000
- **Real-time Chat**: Chat interface berbasis web
- **Live Logs**: Menampilkan log sistem secara real-time
- **Model Status**: Menampilkan AI model yang sedang digunakan
- **Settings**: Konfigurasi Perplexity model via web

### 7. **Memory & Context**
- **Chat History**: Menyimpan 10 percakapan terakhir (20 items) untuk konteks
- **State Management**: Shared state untuk tracking model, logs, dan konfigurasi

---

## ⚙️ Cara Kerja Aplikasi

### **Arsitektur Sistem**

```
┌─────────────────────────────────────────────────────────┐
│                    main.py                               │
│  ┌──────────────┐         ┌──────────────┐             │
│  │ Web Server   │         │ Voice Loop    │             │
│  │ (Thread)     │         │ (Async)       │             │
│  └──────────────┘         └──────────────┘             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              core/voice.py                               │
│  • listen() → Speech Recognition                        │
│  • speak() → Text-to-Speech (Edge TTS)                  │
│  • Audio Queue → Sequential playback                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              core/brain.py                               │
│  1. Parse Command (Local Actions?)                      │
│     ├─ Ya → execute_action() → Return                  │
│     └─ Tidak → Lanjut ke AI                            │
│                                                          │
│  2. Internet Search? (DuckDuckGo)                       │
│                                                          │
│  3. AI Processing (Multi-provider dengan fallback)      │
│     ├─ Gemini → Perplexity → DeepSeek → Groq → Ollama  │
│     └─ Streaming Response                               │
│                                                          │
│  4. Parse Actions dari AI Response                      │
│     ├─ [ACTION:REMIND]                                  │
│     ├─ [ACTION:WRITE_FILE]                              │
│     └─ [ACTION:OPEN_APP]                                │
│                                                          │
│  5. Save to Chat History                                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              core/actions.py                             │
│  • open_app() → AppOpener / webbrowser                  │
│  • play_youtube() → yt-dlp + webbrowser                 │
│  • get_time() / get_date() → datetime                   │
│  • volume_*() → pyautogui                               │
│  • generate_image() → Pollinations.ai / Hugging Face   │
│  • capture_web() → pyautogui.screenshot()               │
│  • check_server() → subprocess ping                     │
│  • write_file() → File I/O                              │
└─────────────────────────────────────────────────────────┘
```

### **Flow Eksekusi**

1. **Startup** (`main.py`):
   - Membersihkan file TTS lama
   - Menjalankan web server di thread terpisah (port 8000)
   - Menjalankan voice loop utama

2. **Voice Loop**:
   - Terry menyapa: `"Halo, Aku Terry"`
   - Loop terus-menerus:
     - `listen()` → Mendengarkan suara (timeout 5 detik, max 10 detik)
     - Cek kata pemicu (trigger words)
     - Jika ada trigger → `process()` → `speak()`
     - Jika tidak → Abaikan

3. **Processing** (`brain.py`):
   - **Pre-processing**: Cek apakah perintah adalah local action
   - **Search**: Jika mengandung keyword pencarian → DuckDuckGo
   - **AI Processing**: 
     - Build prompt dengan system prompt + chat history + search context
     - Coba provider satu per satu (Gemini → Perplexity → DeepSeek → Groq → Ollama)
     - Streaming response per kalimat
   - **Post-processing**: Parse action tags, simpan ke history

4. **Audio Playback**:
   - Queue-based system untuk memastikan audio diputar secara berurutan
   - Cross-platform: Windows (MCI) / Linux (ffplay)

---

## 📋 Keperluan & Dependencies

### **Sistem Operasi**
- ✅ Windows 10/11
- ✅ Linux (Ubuntu/Debian dan distro lainnya)

### **Python**
- Python 3.10 atau lebih tinggi

### **Dependencies (requirements.txt)**

#### **Core**
- `python-dotenv` - Load environment variables (.env)
- `requests` - HTTP requests

#### **Web/API**
- `fastapi` - Web framework untuk dashboard
- `uvicorn` - ASGI server
- `jinja2` - Template engine

#### **Audio/Voice**
- `SpeechRecognition` - Speech-to-text (Google API)
- `pyaudio` - Audio I/O untuk microphone
- `edge-tts` - Microsoft Edge Text-to-Speech
- `pygame` - Audio playback (backup)

#### **AI/LLM**
- `google-genai` - Google Gemini API
- `openai` - OpenAI-compatible API (untuk Perplexity, DeepSeek)
- `groq` - Groq API client
- `putergenai` - Alternative AI provider

#### **System/Tools**
- `pyautogui` - Automation (volume, media control, screenshot)
- `AppOpener` - Membuka aplikasi Windows/Linux
- `psutil` - System utilities
- `schedule` - Task scheduling (untuk reminder)
- `yt-dlp` - YouTube downloader/search
- `duckduckgo-search` - Internet search

### **External Tools**
- **FFmpeg**: Wajib untuk audio processing
  - Windows: Download dari gyan.dev atau gunakan yang di folder `bin/`
  - Linux: `sudo apt install ffmpeg`

### **API Keys (Opsional)**
Aplikasi dapat berjalan dengan beberapa kombinasi API keys:
- `GEMINI_API_KEY` (wajib untuk Gemini)
- `GEMINI_API_KEY_2`, `GEMINI_API_KEY_3` (backup keys)
- `PERPLEXITY_API_KEY` (untuk Perplexity)
- `PERPLEXITY_API_KEY_2`, `PERPLEXITY_API_KEY_3` (backup)
- `DEEPSEEK_API_KEY` (untuk DeepSeek)
- `GROQ_API_KEY` (untuk Groq)
- `OLLAMA_BASE_URL` (untuk Ollama local, contoh: `http://localhost:11434`)
- `OLLAMA_MODEL` (default: `llama3.2`)
- `HF_TOKEN` (untuk Hugging Face image generation backup)

---

## 🚀 Panduan Instalasi

### **Windows**

#### **Langkah 1: Install Python**
1. Download Python 3.10+ dari [python.org](https://www.python.org/downloads/)
2. **PENTING**: Centang opsi **"Add Python to PATH"** saat instalasi
3. Verifikasi: Buka Command Prompt, ketik `python --version`

#### **Langkah 2: Install FFmpeg**

**Opsi A: Otomatis (Recommended)**
1. Jalankan `start_terry.bat` (Shortcut ke `app_standalone.py`)
2. Jika FFmpeg tidak ditemukan, script akan menawarkan download otomatis
3. Pilih `Y` untuk download

**Opsi B: Manual**
1. Download FFmpeg dari [gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z) (pilih "full")
2. Ekstrak file `.7z` (klik kanan > Extract here)
3. Rename folder menjadi `ffmpeg`
4. Pindahkan ke `C:\ffmpeg`
5. Tambahkan ke PATH:
   - Tekan `Windows` → ketik `env` → pilih "Edit the system environment variables"
   - Klik "Environment Variables"
   - Di "System variables", cari "Path" → Edit
   - Klik "New" → ketik: `C:\ffmpeg\bin`
   - OK → OK → OK
6. Verifikasi: Buka terminal baru, ketik `ffmpeg -version`

**Opsi C: Gunakan FFmpeg Lokal**
- Script akan otomatis menggunakan `bin/ffmpeg.exe` jika ada di folder project

#### **Langkah 3: Setup Project**
1. Download/Clone folder project
2. Buka Command Prompt di folder project
3. Jalankan:
   ```bat
   start_terry.bat
   ```
   Script ini akan:
   - Membuat virtual environment (`venv`)
   - Install semua dependencies
   - Menjalankan aplikasi

#### **Langkah 4: Konfigurasi API Keys**
1. Buat file `.env` di folder utama project
2. Isi dengan API keys Anda:
   ```env
   GEMINI_API_KEY=your_gemini_key_here
   GEMINI_API_KEY_2=backup_key_1
   GEMINI_API_KEY_3=backup_key_2
   PERPLEXITY_API_KEY=your_perplexity_key
   GROQ_API_KEY=your_groq_key
   DEEPSEEK_API_KEY=your_deepseek_key
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   HF_TOKEN=your_huggingface_token
   ```

**Cara Mendapatkan API Keys:**
- **Gemini**: [Google AI Studio](https://aistudio.google.com/) (Gratis)
- **Perplexity**: [Perplexity Console](https://www.perplexity.ai/settings/api) (Berbayar)
- **Groq**: [Groq Console](https://console.groq.com/) (Gratis dengan limit)
- **DeepSeek**: [DeepSeek Platform](https://platform.deepseek.com/) (Berbayar)
- **Ollama**: Install lokal dari [ollama.ai](https://ollama.ai/)

#### **Langkah 5: Jalankan Aplikasi**
- Double-click `start_terry.bat`
- Atau buka terminal, ketik:
  ```bat
  venv\Scripts\activate
  python main.py
  ```

---

### **Linux (Ubuntu/Debian)**

#### **Langkah 1: Install Python & Dependencies Sistem**
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip ffmpeg
```

#### **Langkah 2: Install PyAudio Dependencies**
```bash
sudo apt install portaudio19-dev python3-pyaudio
```

#### **Langkah 3: Setup Project**
1. Download/Clone folder project
2. Buka terminal di folder project
3. Berikan permission execute:
   ```bash
   chmod +x start_terry.sh
   ```
4. Jalankan:
   ```bash
   ./start_terry.sh
   ```
   Script ini akan:
   - Membuat virtual environment
   - Install dependencies
   - Menjalankan aplikasi

#### **Langkah 4: Konfigurasi API Keys**
Sama seperti Windows, buat file `.env` di folder utama:
```env
GEMINI_API_KEY=your_key_here
# ... (sama seperti Windows)
```

#### **Langkah 5: Jalankan Aplikasi**
```bash
source venv/bin/activate
python main.py
```

---

## 🎮 Panduan Penggunaan

### **Cara Menjalankan**

1. **Via Script** (Paling Mudah):
   - Windows: Double-click `start_terry.bat`
   - Linux: `./start_terry.sh`

2. **Via Terminal**:
   ```bash
   # Windows
   venv\Scripts\activate
   python app_standalone.py
   
   # Linux
   source venv/bin/activate
   python app_standalone.py
   ```

### **Interface**

Setelah aplikasi berjalan, Anda akan melihat:
- **Terminal/Console**: Menampilkan log dan status
- **Web Dashboard**: Buka browser ke `http://localhost:8000`

### **Kata Pemicu (Wake Words)**

Terry akan merespons jika perintah mengandung kata-kata berikut:
- `"terry"`, `"halo"`, `"buka"`, `"ingat"`, `"jam"`, `"waktu"`, `"tanggal"`
- `"putar"`, `"tolong"`, `"siapa"`, `"mainkan"`, `"apa"`, `"kenapa"`
- `"bagaimana"`, `"gimana"`, `"jelaskan"`, `"cerita"`, `"dongeng"`
- `"hibur"`, `"harga"`, `"berapa"`, `"cari"`, `"tulis"`, `"buat"`
- `"cek"`, `"tes"`, `"internet"`, `"server"`, `"check"`

### **Contoh Perintah**

#### **Aksi Lokal (Cepat, Tanpa AI)**
```
"Terry, jam berapa sekarang?"
"Tanggal berapa hari ini?"
"Buka Notepad"
"Buka Chrome"
"Buka google.com"
"Putar lagu Govinda Hal Hebat"
"Besarkan suara"
"Kecilkan suara"
"Mute"
"Pause"
"Resume"
"Skip"
"Cek server"
"Tes internet"
```

#### **Pencarian & Informasi**
```
"Terry, cari informasi tentang Python"
"Siapa presiden Indonesia?"
"Berapa harga iPhone 15?"
"Cari berita teknologi terbaru"
```

#### **Generasi Konten**
```
"Buatkan gambar sunset di pantai"
"Ceritakan dongeng sebelum tidur"
"Tulis puisi tentang hujan"
"Jelaskan cara kerja AI"
```

#### **Kontrol Sistem**
```
"Buka CasaOS"
"Buka dashboard server"
"Screenshot google.com"
```

### **Web Dashboard**

Akses di `http://localhost:8000`:
- **Chat Interface**: Chat dengan Terry via teks
- **Live Logs**: Melihat log sistem real-time
- **Model Status**: Melihat AI model yang sedang digunakan
- **Settings**: Mengubah Perplexity model (Sonar / Sonar Pro)

### **Tips Penggunaan**

1. **Microphone**: Pastikan microphone aktif dan tidak di-mute
2. **Internet**: Beberapa fitur membutuhkan koneksi internet (TTS, AI, Search)
3. **Suara Jelas**: Bicara dengan jelas dan tidak terlalu cepat
4. **Trigger Words**: Pastikan perintah mengandung kata pemicu
5. **Volume**: Atur volume speaker agar dapat mendengar respons Terry

---

## 🔧 Troubleshooting

### **Masalah Umum**

#### **1. "ffmpeg is not recognized"**
- **Windows**: Pastikan FFmpeg sudah di-install dan ditambahkan ke PATH, atau gunakan FFmpeg di folder `bin/`
- **Linux**: Install dengan `sudo apt install ffmpeg`

#### **2. Suara Putus-putus atau Tidak Jelas**
- Cek koneksi internet (Edge TTS butuh internet)
- Cek volume speaker
- Cek apakah ada aplikasi lain yang menggunakan audio

#### **3. Microphone Tidak Terdeteksi**
- **Windows**: Cek di Settings → Privacy → Microphone
- **Linux**: Install `portaudio19-dev` dan `python3-pyaudio`
- Cek apakah microphone tidak di-mute

#### **4. Error API (429, Quota Exhausted)**
- API key Anda mungkin sudah mencapai limit
- Gunakan backup API key (GEMINI_API_KEY_2, dll)
- Atau gunakan provider lain (Groq, DeepSeek)

#### **5. "Module not found"**
- Pastikan virtual environment aktif
- Install ulang dependencies: `pip install -r requirements.txt`

#### **6. Web Dashboard Tidak Bisa Diakses**
- Pastikan port 8000 tidak digunakan aplikasi lain
- Cek firewall settings
- Coba akses `http://127.0.0.1:8000`

#### **7. YouTube Tidak Bisa Diputar**
- Pastikan `yt-dlp` terinstall: `pip install yt-dlp`
- Cek koneksi internet
- Coba perintah lain seperti "Buka YouTube"

#### **8. Aplikasi Tidak Bisa Dibuka**
- **Windows**: Gunakan `AppOpener` - pastikan nama aplikasi benar
- Coba buka manual dulu untuk memastikan aplikasi terinstall

---

## 📁 Struktur Folder

```
Terry Voice+Text/
├── main.py                 # Entry point aplikasi
├── requirements.txt        # Dependencies Python
├── .env                    # API keys (buat sendiri)
├── start_terry.bat         # Script startup Windows
├── start_terry.sh          # Script startup Linux
│
├── core/                   # Core modules
│   ├── brain.py           # AI processing & routing
│   ├── voice.py           # Speech recognition & TTS
│   ├── actions.py         # System actions executor
│   └── shared.py          # Shared state & logging
│
├── web/                    # Web dashboard
│   ├── server.py          # FastAPI server
│   ├── templates/
│   │   └── index.html     # Dashboard UI
│   └── static/
│       ├── script.js      # Frontend logic
│       └── style.css      # Styling
│
├── bin/                    # FFmpeg binaries (opsional)
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
│
├── rumah/                  # Working directory
│   ├── galeri/            # Generated images
│   └── screenshots/       # Web screenshots
│
└── venv/                   # Virtual environment (auto-generated)
```

---

## 🔐 Keamanan & Privasi

1. **API Keys**: Jangan commit file `.env` ke Git
2. **Microphone**: Data suara dikirim ke Google Speech Recognition API
3. **Internet**: Aplikasi membutuhkan koneksi internet untuk beberapa fitur
4. **Local Actions**: Beberapa aksi (volume, media control) dijalankan lokal tanpa internet

---

## 🚀 Pengembangan & Kustomisasi

### **Menambah Kata Pemicu**
Edit `main.py`, tambahkan ke array `TRIGGERS`:
```python
TRIGGERS = [
    "terry", "halo", "buka", # ... tambahkan di sini
    "kata_baru_anda"
]
```

### **Menambah Local Action**
Edit `core/brain.py`, tambahkan kondisi baru:
```python
if "kata_kunci" in text_lower:
    state.set_model("Local (Action)")
    yield execute_action("action_type", payload)
    return
```

Lalu implementasikan di `core/actions.py`:
```python
elif action_type == "action_type":
    # Implementasi aksi
    return "Response message"
```

### **Menambah AI Provider**
Edit `core/brain.py`, tambahkan setelah provider lain:
```python
# X. Provider Baru
new_key = os.getenv("NEW_PROVIDER_API_KEY")
if new_key:
    try:
        state.set_model("New Provider")
        # Implementasi API call
        async for s in process_stream(stream): yield s
        return
    except Exception as e:
        log(f"[Brain] New Provider Error: {e}")
```

### **Mengubah Voice TTS**
Edit `core/voice.py`, ubah variabel `VOICE`:
```python
VOICE = "id-ID-GadisNeural"  # Ganti dengan voice lain
# Daftar voice: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support
```

---

## 📝 Catatan Teknis

### **Audio Processing**
- **Windows**: Menggunakan Windows MCI (Media Control Interface) untuk playback
- **Linux**: Menggunakan `ffplay` (dari FFmpeg)
- **Queue System**: Memastikan audio diputar berurutan, tidak overlap

### **AI Streaming**
- Response AI di-stream per kalimat untuk pengalaman lebih natural
- Sentence splitting menggunakan regex untuk memisahkan kalimat
- Action parsing menggunakan regex untuk ekstrak `[ACTION:...]` tags

### **State Management**
- Shared state menggunakan singleton pattern
- Chat history dibatasi 20 items (10 percakapan)
- Logs dibatasi 100 entries

### **Error Handling**
- Fallback chain: Gemini → Perplexity → DeepSeek → Groq → Ollama → Google Search
- Setiap provider memiliki error handling sendiri
- Local actions tidak membutuhkan internet (kecuali YouTube, web capture)

---

## 📞 Support & Kontribusi

Jika menemukan bug atau ingin berkontribusi:
1. Buat issue di GitHub repository
2. Fork repository
3. Buat branch untuk fitur baru
4. Submit pull request

---

## 📄 Lisensi

Aplikasi ini menggunakan berbagai library open-source. Pastikan untuk mematuhi lisensi masing-masing dependency.

---

## 🎉 Kesimpulan

Terry AI Assistant adalah aplikasi asisten AI yang powerful dengan fitur:
- ✅ Voice & Text interface
- ✅ Multi-provider AI dengan fallback
- ✅ Local actions untuk kecepatan
- ✅ Web dashboard untuk monitoring
- ✅ Cross-platform (Windows & Linux)
- ✅ Extensible architecture

Selamat menggunakan Terry! 🚀
