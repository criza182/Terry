# 🤖 Terry AI Assistant

Terry adalah asisten AI berbasis suara dan teks yang dirancang untuk Windows dan Linux. Aplikasi ini menggabungkan teknologi speech recognition, text-to-speech, dan multiple AI providers untuk memberikan pengalaman interaksi yang natural dan responsif.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)

---

## ✨ Fitur Utama

- 🎤 **Voice Assistant**: Speech recognition dan text-to-speech dalam Bahasa Indonesia
- 🧠 **Multi-Provider AI**: Gemini, Perplexity, DeepSeek, Groq, Ollama dengan fallback otomatis
- ⚡ **Local Actions**: Aksi cepat tanpa AI (buka app, YouTube, waktu, volume, media control)
- 🌐 **Internet Search**: Pencarian informasi via DuckDuckGo
- 🎨 **Image Generation**: Generate gambar dari teks
- 📸 **Web Screenshot**: Capture layar website
- 💻 **Web Dashboard**: Interface web real-time di port 8000
- 💾 **Memory & Context**: Menyimpan riwayat percakapan untuk konteks

---

## 📋 Prasyarat

### **Sistem Operasi**
- ✅ Windows 10/11
- ✅ Linux (Ubuntu/Debian dan distro lainnya)

### **Python**
- Python 3.10 atau lebih tinggi
- **Windows**: [Download dari python.org](https://www.python.org/downloads/)
  - **PENTING**: Centang opsi "Add Python to PATH" saat menginstal
- **Linux**: 
  ```bash
  sudo apt install python3 python3-venv python3-pip
  ```

### **FFmpeg**
Wajib untuk pemrosesan audio.

**Windows - Opsi A (Otomatis)**:
- Script akan menawarkan download otomatis saat pertama kali dijalankan

**Windows - Opsi B (Manual)**:
1. [Download dari gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z) (pilih "full")
2. Ekstrak dan rename folder menjadi `ffmpeg`
3. Pindahkan ke `C:\ffmpeg`
4. Tambahkan `C:\ffmpeg\bin` ke PATH:
   - Windows → ketik "env" → "Edit the system environment variables"
   - Environment Variables → System variables → Path → Edit → New
   - Ketik: `C:\ffmpeg\bin` → OK
5. Verifikasi: Buka terminal baru, ketik `ffmpeg -version`

**Windows - Opsi C (Lokal)**:
- Gunakan FFmpeg di folder `bin/` (jika ada)

**Linux**:
```bash
sudo apt install ffmpeg
```

---

## 🚀 Instalasi

### **Windows**

1. **Download/Clone** folder proyek ini
2. **Jalankan script setup**:
   ```bat
   start_terry.bat
   ```
   Script ini akan:
   - Membuat virtual environment (`venv`)
   - Install semua dependencies
   - Menjalankan aplikasi

### **Linux**

1. **Install dependencies sistem**:
   ```bash
   sudo apt install portaudio19-dev python3-pyaudio
   ```

2. **Jalankan script setup**:
   ```bash
   chmod +x start_terry.sh
   ./start_terry.sh
   ```

**Catatan**: Saat pertama kali dijalankan, proses instalasi mungkin agak lama karena sedang mendownload modul-modul yang dibutuhkan.

---

## ⚙️ Konfigurasi API Keys

Buat file `.env` di folder utama project, lalu isi dengan API keys Anda:

```env
# Gemini (Wajib untuk fitur utama)
GEMINI_API_KEY=your_gemini_key_here
GEMINI_API_KEY_2=backup_key_1
GEMINI_API_KEY_3=backup_key_2

# Perplexity (Opsional)
PERPLEXITY_API_KEY=your_perplexity_key
PERPLEXITY_API_KEY_2=backup_key_1
PERPLEXITY_API_KEY_3=backup_key_2

# Groq (Opsional)
GROQ_API_KEY=your_groq_key

# DeepSeek (Opsional)
DEEPSEEK_API_KEY=your_deepseek_key

# Ollama Local (Opsional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Hugging Face (Opsional, untuk image generation backup)
HF_TOKEN=your_huggingface_token
```

### **Cara Mendapatkan API Keys**

- **Gemini**: [Google AI Studio](https://aistudio.google.com/) (Gratis)
- **Perplexity**: [Perplexity Console](https://www.perplexity.ai/settings/api) (Berbayar)
- **Groq**: [Groq Console](https://console.groq.com/) (Gratis dengan limit)
- **DeepSeek**: [DeepSeek Platform](https://platform.deepseek.com/) (Berbayar)
- **Ollama**: Install lokal dari [ollama.ai](https://ollama.ai/)

**Catatan**: Minimal butuh satu API key (Gemini direkomendasikan). Aplikasi akan menggunakan fallback otomatis jika provider utama gagal.

---

## 🎮 Cara Menggunakan

### **Menjalankan Aplikasi**

**Windows**: Double-click `start_terry.bat`

**Linux**: 
```bash
./start_terry.sh
```

**Manual**:
```bash
# Windows
venv\Scripts\activate
python main.py

# Linux
source venv/bin/activate
python main.py
```

### **Interface**

Setelah aplikasi berjalan:
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

---

## 🛠️ Troubleshooting

### **Masalah Umum**

#### **"ffmpeg is not recognized"**
- **Windows**: Pastikan FFmpeg sudah di-install dan ditambahkan ke PATH, atau gunakan FFmpeg di folder `bin/`
- **Linux**: Install dengan `sudo apt install ffmpeg`

#### **Suara Putus-putus atau Tidak Jelas**
- Cek koneksi internet (Edge TTS butuh internet)
- Cek volume speaker
- Cek apakah ada aplikasi lain yang menggunakan audio

#### **Microphone Tidak Terdeteksi**
- **Windows**: Cek di Settings → Privacy → Microphone
- **Linux**: Install `portaudio19-dev` dan `python3-pyaudio`
- Cek apakah microphone tidak di-mute

#### **Error API (429, Quota Exhausted)**
- API key Anda mungkin sudah mencapai limit
- Gunakan backup API key (GEMINI_API_KEY_2, dll)
- Atau gunakan provider lain (Groq, DeepSeek)

#### **"Module not found"**
- Pastikan virtual environment aktif
- Install ulang dependencies: `pip install -r requirements.txt`

#### **Web Dashboard Tidak Bisa Diakses**
- Pastikan port 8000 tidak digunakan aplikasi lain
- Cek firewall settings
- Coba akses `http://127.0.0.1:8000`

#### **YouTube Tidak Bisa Diputar**
- Pastikan `yt-dlp` terinstall: `pip install yt-dlp`
- Cek koneksi internet
- Coba perintah lain seperti "Buka YouTube"

---

## 📁 Struktur Project

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

## 🔧 Pengembangan

### **Menambah Kata Pemicu**
Edit `main.py`, tambahkan ke array `TRIGGERS`:
```python
TRIGGERS = [
    "terry", "halo", "buka", # ... tambahkan di sini
    "kata_baru_anda"
]
```

### **Menambah Local Action**
Edit `core/brain.py` dan `core/actions.py` untuk menambah aksi baru.

### **Mengubah Voice TTS**
Edit `core/voice.py`, ubah variabel `VOICE`:
```python
VOICE = "id-ID-GadisNeural"  # Ganti dengan voice lain
```

---

## 📚 Dokumentasi Lengkap

Untuk dokumentasi lebih detail tentang:
- Arsitektur sistem dan flow eksekusi
- Daftar lengkap dependencies
- Panduan instalasi step-by-step
- Catatan teknis dan keamanan
- Panduan kustomisasi lanjutan

Lihat file **[DOKUMENTASI_LENGKAP.md](DOKUMENTASI_LENGKAP.md)**

---

## 🔐 Keamanan & Privasi

- **API Keys**: Jangan commit file `.env` ke Git
- **Microphone**: Data suara dikirim ke Google Speech Recognition API
- **Internet**: Aplikasi membutuhkan koneksi internet untuk beberapa fitur
- **Local Actions**: Beberapa aksi (volume, media control) dijalankan lokal tanpa internet

---

## 📝 Lisensi

Aplikasi ini menggunakan berbagai library open-source. Pastikan untuk mematuhi lisensi masing-masing dependency.

---

## 🤝 Kontribusi

Kontribusi sangat diterima! Jika menemukan bug atau ingin menambah fitur:
1. Buat issue di GitHub repository
2. Fork repository
3. Buat branch untuk fitur baru
4. Submit pull request

---

## ⭐ Fitur Unggulan

- ✅ Voice & Text interface
- ✅ Multi-provider AI dengan fallback otomatis
- ✅ Local actions untuk kecepatan
- ✅ Web dashboard untuk monitoring
- ✅ Cross-platform (Windows & Linux)
- ✅ Extensible architecture

---

**Selamat menggunakan Terry! 🚀**
