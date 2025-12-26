# Terry AI Assistant

Terry adalah asisten suara cerdas untuk Windows yang dirancang agar komunikatif, membantu, dan penuh kepribadian.

## 📋 Prasyarat (Prerequisites)

Sebelum memulai, pastikan Anda telah menginstal hal-hal berikut di komputer Anda:

1.  **Python 3.10+**: [Download dari python.org](https://www.python.org/downloads/)
    *   **PENTING**: Centang opsi "Add Python to PATH" saat menginstal.
    *   **Linux**: `sudo apt install python3 python3-venv python3-pip`
2.  **FFmpeg**: Wajib ada untuk pemrosesan audio (agar Terry bisa bicara).
    *   **Windows**:
        1.  [Download dari gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z) (pilih yang "full").
        2.  Ekstrak file `.7z` tersebut (klik kanan > Extract here).
        3.  Ubah nama folder hasil ekstrak menjadi `ffmpeg` (biar pendek).
        4.  Pindahkan folder `ffmpeg` tersebut ke Drive C (jadi `C:\ffmpeg`).
        5.  **Memasukkan ke PATH**:
            *   Tekan tombol **Windows**, ketik **"env"**, pilih **"Edit the system environment variables"**.
            *   Klik tombol **"Environment Variables"** di kanan bawah.
            *   Di bagian **"System variables"** (kotak bawah), cari tulisan **"Path"**, lalu klik **Edit**.
            *   Klik **New** di sampan kanan.
            *   Ketik: `C:\ffmpeg\bin`
            *   Klik **OK**, **OK**, **OK** sampai semua jendela tertutup.
        6.  **Tes**: Buka terminal baru, ketik `ffmpeg -version`.
    *   **Linux**: `sudo apt install ffmpeg`

## 🚀 Instalasi & Pengaturan

1.  **Download/Clone** folder proyek ini.
2.  **Buka Terminal** di dalam folder proyek ini.
3.  **Jalankan script setup**:
    
    **Windows**:
    ```bat
    start_terry.bat
    ```

    **Linux**:
    ```bash
    chmod +x start_terry.sh
    ./start_terry.sh
    ```
    *   *Catatan: Saat pertama kali dijalankan, proses ini mungkin agak lama karena sedang mendownload modul-modul yang dibutuhkan.*

## ⚙️ Konfigurasi (.env)

Buat atau edit file bernama `.env` di folder utama, lalu isi dengan kunci API (API Key) Anda:

```env
GEMINI_API_KEY=kunci_gemini_api_anda_disini
GROQ_API_KEY=kunci_groq_api_anda_disini
```

*   **Gemini API Key**: Dapatkan gratis di [Google AI Studio](https://aistudio.google.com/).
*   **Groq API Key**: Dapatkan gratis di [Groq Console](https://console.groq.com/).

## 🎮 Cara Menggunakan

Cukup klik dua kali (double-click) file `start_terry.bat` untuk menyalakan Terry.

*   **Kata Pemicu (Wake Words)**: "Terry", "Halo", "Buka", "Tolong", dll.
*   **Contoh Perintah**:
    *   "Terry, jam berapa sekarang?"
    *   "Putar lagu Govinda Hal Hebat"
    *   "Buka Notepad"
    *   "Ceritakan dongeng sebelum tidur"

## 🛠️ Pemecahan Masalah (Troubleshooting)

*   **Suara Putus-putus**: Pastikan koneksi internet Anda stabil (Suara Terry butuh internet).
*   **"ffmpeg is not recognized"**: Artinya FFmpeg belum terinstal atau belum masuk ke PATH. Lihat bagian Prasyarat di atas.
*   **Error API**: Cek kuota API key Anda atau koneksi internet.
