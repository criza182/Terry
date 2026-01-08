# 🔧 Troubleshooting Git - Terry AI

## Masalah: Gagal Commit/Push ke GitHub

### ✅ Status Saat Ini
- **Commit lokal**: ✅ Berhasil (2 commit menunggu push)
- **Remote repository**: ✅ Terkonfigurasi (`https://github.com/criza182/Terry.git`)
- **Git config**: ✅ Sudah di-set (user.name & user.email)

### ❌ Masalah yang Terjadi
```
fatal: unable to access 'https://github.com/criza182/Terry.git/': 
Failed to connect to github.com port 443 after 89 ms: Could not connect to server
```

---

## 🔍 Solusi

### **1. Cek Koneksi Internet**
```powershell
# Test koneksi ke GitHub
Test-NetConnection github.com -Port 443
```

Jika gagal, pastikan:
- Internet Anda terhubung
- Tidak ada VPN yang memblokir GitHub
- Firewall tidak memblokir port 443

### **2. Cek Proxy Settings (Jika Menggunakan Proxy)**
```powershell
# Cek proxy git
git config --global --get http.proxy
git config --global --get https.proxy

# Jika ada proxy, set dengan benar:
# git config --global http.proxy http://proxy.example.com:8080
# git config --global https.proxy https://proxy.example.com:8080

# Atau hapus proxy jika tidak digunakan:
# git config --global --unset http.proxy
# git config --global --unset https.proxy
```

### **3. Gunakan SSH Instead of HTTPS (Alternatif)**
Jika HTTPS terus bermasalah, gunakan SSH:

```powershell
# 1. Cek apakah sudah ada SSH key
ls ~/.ssh

# 2. Jika belum ada, generate SSH key
ssh-keygen -t ed25519 -C "mail@tonykumbayer.my.id"

# 3. Tambahkan SSH key ke GitHub (copy isi id_ed25519.pub)
cat ~/.ssh/id_ed25519.pub

# 4. Ubah remote URL ke SSH
git remote set-url origin git@github.com:criza182/Terry.git

# 5. Test koneksi
ssh -T git@github.com

# 6. Push lagi
git push origin master
```

### **4. Cek Firewall Windows**
1. Buka **Windows Defender Firewall**
2. Cek apakah Git/VS Code diizinkan melalui firewall
3. Atau sementara nonaktifkan firewall untuk test

### **5. Gunakan GitHub CLI (Alternatif)**
```powershell
# Install GitHub CLI
winget install GitHub.cli

# Login
gh auth login

# Push via CLI
gh repo sync
```

### **6. Manual Upload via GitHub Web**
Jika semua gagal, Anda bisa:
1. Buka https://github.com/criza182/Terry
2. Upload file secara manual via web interface
3. Atau gunakan GitHub Desktop app

---

## 📋 Perintah Git yang Berguna

### **Cek Status**
```powershell
git status
```

### **Lihat Commit yang Belum di-Push**
```powershell
git log origin/master..HEAD --oneline
```

### **Cek Remote**
```powershell
git remote -v
```

### **Ubah Remote URL (Jika Perlu)**
```powershell
# HTTPS
git remote set-url origin https://github.com/criza182/Terry.git

# SSH
git remote set-url origin git@github.com:criza182/Terry.git
```

### **Force Push (HATI-HATI!)**
```powershell
# Hanya jika benar-benar perlu, dan Anda yakin
git push origin master --force
```

---

## 🎯 Langkah-Langkah Push yang Benar

1. **Pastikan semua perubahan sudah di-commit**:
   ```powershell
   git status
   git add .
   git commit -m "Pesan commit Anda"
   ```

2. **Cek koneksi internet**:
   ```powershell
   Test-NetConnection github.com -Port 443
   ```

3. **Push ke GitHub**:
   ```powershell
   git push origin master
   ```

4. **Jika masih gagal, coba dengan verbose untuk melihat error detail**:
   ```powershell
   git push origin master -v
   ```

---

## 💡 Tips

- **Commit lokal sudah aman**: Meskipun push gagal, commit Anda sudah tersimpan lokal
- **Coba lagi nanti**: Jika masalahnya koneksi, coba push lagi saat koneksi lebih stabil
- **Gunakan GitHub Desktop**: Lebih mudah untuk user yang tidak familiar dengan command line
- **Backup lokal**: Selalu backup folder project secara manual sebagai cadangan

---

## 📞 Bantuan Lebih Lanjut

Jika masalah masih berlanjut:
1. Cek [GitHub Status](https://www.githubstatus.com/)
2. Lihat [GitHub Documentation](https://docs.github.com/)
3. Cek [Git Documentation](https://git-scm.com/doc)
