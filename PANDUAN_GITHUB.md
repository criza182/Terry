# Panduan Upload ke GitHub

Berikut adalah langkah-langkah detail untuk mengupload proyek Terry ke GitHub.

## 1. Persiapan di GitHub Website
1.  Buka [github.com](https://github.com/) dan login.
2.  Klik tombol **(+)** di pojok kanan atas, pilih **New repository**.
3.  **Repository name**: Isi nama, misal `Terry-AI-Assistant` (atau bebas).
4.  **Public/Private**: Pilih sesuai keinginan.
5.  **Jangan centang** "Add a README", "Add .gitignore", dll (karena kita sudah punya di komputer).
6.  Klik **Create repository**.
7.  Salin link HTTPS yang muncul (contoh: `https://github.com/username/Terry-AI-Assistant.git`).

## 2. Perintah di Terminal
Kembali ke VS Code (atau terminal Anda), pastikan Anda berada di folder proyek Terry, lalu ketik perintah ini satu per satu:

```bash
# 1. Inisialisasi Git
git init

# 2. Masukkan semua file (yang tidak di-ignore)
git add .

# 3. Simpan perubahan (Commit)
git commit -m "Upload pertama Terry AI"

# 4. Hubungkan ke GitHub (Ganti URL dengan link yang Anda salin tadi)
git remote add origin https://github.com/USERNAME/NAMA-REPO-ANDA.git

# 5. Kirim file ke GitHub
git push -u origin master
```

*Catatan: Jika perintah `git` tidak dikenali, Anda perlu menginstall Git terlebih dahulu dari [git-scm.com](https://git-scm.com/downloads).*
