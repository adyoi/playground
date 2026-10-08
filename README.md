# Playground RDP - GitHub Actions Remote Desktop

Repository ini berisi workflow GitHub Actions untuk membuat akses Remote Desktop (RDP) ke runner Windows GitHub Actions menggunakan tiga metode tunneling berbeda.

## 📋 Daftar Workflow

| Workflow | Metode Tunnel | Keuntungan | Cocok Untuk |
|----------|---------------|------------|-------------|
| `rdp-cloudflare.yml` | Cloudflare Tunnel | Gratis, custom domain, keamanan tinggi | Production, akses jangka panjang |
| `rdp-ngrok.yml` | Ngrok TCP | Setup cepat, URL publik langsung | Testing cepat, demo |
| `rdp-tailscale.yml` | Tailscale (WireGuard) | Mesh VPN, performa tinggi, NAT traversal | Tim development, akses secure |

---

## 🔧 Prasyarat Umum

1. **GitHub Repository** dengan Actions enabled
2. **GitHub Secrets** sesuai metode yang dipilih (lihat tabel di bawah)
3. **Local machine** dengan Windows/Mac/Linux untuk koneksi RDP

---

## ☁️ 1. Cloudflare Tunnel (`rdp-cloudflare.yml`)

### Fitur
- Menggunakan Cloudflare Zero Trust Tunnel
- Support custom domain (misal: `rdp.domain.com`)
- Gratis untuk personal use
- Proteksi DDoS bawaan Cloudflare
- Bypass firewall/NAT tanpa port forwarding

### Persiapan (Sekali Saja)

#### A. Dapatkan Domain Gratis (digitalplat.org) + Setup Cloudflare
> **Catatan**: Cloudflare Tunnel memerlukan domain sendiri. Jika belum punya, bisa dapatkan gratis via [digitalplat.org](https://digitalplat.org/) lalu kelola DNS di Cloudflare.

1. **Daftar domain gratis di digitalplat.org**
   - Buka https://digitalplat.org/
   - Pilih menu **Domain** → submenu **Register Domains**
   - Pada halaman **Domain Registration**, pilih **DigitalPlat One** → klik **Choose a DigitalPlat extension**
   - Scroll ke bagian bawah
   - Ketik domain yang diinginkan, pilih ekstensi domain gratis yang disediakan → klik **Check Availability**
   - Jika tersedia, centang kebijakan → klik **Buat Domain**
   - Verifikasi email
   - Catat nameserver Cloudflare yang diberikan (biasanya 2 nameserver: `xxx.ns.cloudflare.com`, `yyy.ns.cloudflare.com`)

2. **Tambahkan domain ke Cloudflare**
   - Login ke [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - Klik **Add a site** → Masukkan domain digitalplat.org Anda → **Continue**
   - Pilih plan **Free** → **Continue**
   - Cloudflare akan scan DNS record → **Continue**

3. **Ganti Nameserver di digitalplat.org**
   - Di Cloudflare, catat 2 nameserver (contoh: `alice.ns.cloudflare.com`, `bob.ns.cloudflare.com`)
   - Login ke digitalplat.org → Kelola Domain → **Ganti Nameserver**
   - Masukkan 2 nameserver Cloudflare → **Simpan**
   - Tunggu propagasi DNS (biasanya 5-30 menit, cek di Cloudflare status jadi **Active**)

4. **Verifikasi domain aktif di Cloudflare**
   - Di Cloudflare Dashboard, domain harus status **Active**
   - Tab **DNS** → **Records** → pastikan sudah ada record NS ke Cloudflare

#### B. Buat Cloudflare Tunnel
1. Login ke [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/)
2. Pilih **Networks** → **Tunnels** → **Create a tunnel**
3. Pilih **Cloudflared** → Beri nama (misal: `github-rdp`)
4. **Save tunnel**

#### C. Konfigurasi Public Hostname (TCP)
1. Di halaman edit tunnel tersebut, lihat bagian atas dan klik tab **Public Hostname**.
2. Klik tombol **Add a public hostname**.
3. Isi kolom yang tersedia dengan data berikut:
   - **Subdomain**: `rdp`
   - **Domain**: Pilih domain digitalplat.org Anda dari menu drop-down
   - **Type** (di bawah kolom Service): pilih **TCP**
   - **URL**: `rdp://localhost:3389`
4. Klik **Save hostname**

#### D. Ambil Tunnel Token
1. Di detail tunnel, klik **Configure** → **Token**
2. Copy **Tunnel Token** (format: `eyJh...`)

### Setup GitHub Secrets
| Secret Name | Value | Deskripsi |
|-------------|-------|-----------|
| `CLOUDFLARE_TUNNEL_TOKEN` | Token dari langkah D | Untuk autentikasi tunnel |

### Menjalankan Workflow
1. Buka tab **Actions** di repository GitHub
2. Pilih **"Playground RDP (Cloudflare Tunnel)"** workflow
3. Klik **Run workflow** → isi **Tunnel hostname** (opsional, contoh: `rdp.namaku.digitalplat.org`) → **Run workflow**
4. Tunggu sampai step "Display RDP Access Info" muncul
5. Copy **Password** dari log

### Koneksi dari Local (Client)

#### Windows/macOS/Linux
```bash
# Install cloudflared
# Windows: winget install Cloudflare.cloudflared
# macOS: brew install cloudflare/cloudflare/cloudflared
# Linux: lihat https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

# Jalankan tunnel lokal (ganti dengan hostname Anda)
cloudflared access tcp --hostname rdp.namaku.digitalplat.org --url rdp://localhost:3389
```

#### Remote Desktop Connection
- **Computer**: `localhost:3389`
- **Username**: `RDP`
- **Password**: (dari log workflow)

> ⚠️ **Catatan**: Biarkan terminal `cloudflared` terbuka selama sesi RDP aktif.

---

## 🚀 2. Ngrok (`rdp-ngrok.yml`)

### Fitur
- Setup paling cepat (< 2 menit)
- URL TCP publik langsung (format: `0.tcp.ngrok.io:XXXXX`)
- Gratis untuk personal use (dengan batasan session)
- Tidak perlu custom domain

### Persiapan (Sekali Saja)

#### A. Buat Akun Ngrok
1. Daftar di [ngrok.com](https://ngrok.com/)
2. Verifikasi email
3. Buka **Dashboard** → **Your Authtoken**
4. Copy **Authtoken** (format: `2x...`)

### Setup GitHub Secrets
| Secret Name | Value | Deskripsi |
|-------------|-------|-----------|
| `NGROK_AUTH_TOKEN` | Authtoken dari dashboard Ngrok | Untuk autentikasi ngrok |

### Menjalankan Workflow
1. Buka tab **Actions** → **"playground"** workflow
2. Klik **Run workflow** → **Run workflow**
3. Tunggu step **"Install & Run Ngrok"** selesai
4. Lihat log step tersebut untuk mendapatkan **Public URL** (format: `0.tcp.ngrok.io:12345`)
5. Password default: `MantapBener_2026!`

### Koneksi dari Local (Client)
- **Computer**: `0.tcp.ngrok.io:XXXXX` (dari log workflow)
- **Username**: `RDP`
- **Password**: `MantapBener_2026!`

> ⚠️ **Catatan**: URL berubah setiap kali workflow dijalankan. Copy dari log terbaru.

---

## 🔐 3. Tailscale (`rdp-tailscale.yml`)

### Fitur
- Menggunakan WireGuard (performa tinggi, latency rendah)
- Mesh VPN - akses langsung via IP Tailscale (100.x.x.x)
- Tidak perlu port forwarding atau public IP
- Akses aman hanya untuk device di tailnet yang sama
- Gratis hingga 100 devices (Personal plan)

### Persiapan (Sekali Saja)

#### A. Buat Akun Tailscale
1. Daftar di [tailscale.com](https://tailscale.com/)
2. Login ke [Admin Console](https://login.tailscale.com/admin)

#### B. Buat Auth Key
1. **Settings** → **Auth keys** → **Generate auth key**
2. Pilih:
   - **Reusable** ✓ (agar bisa dipakai berulang)
   - **Ephemeral** ✓ (device otomatis hapus saat disconnected)
   - **Pre-approved** ✓ (langsung connect tanpa approval manual)
3. **Generate** → Copy key (format: `tskey-auth-...`)

### Setup GitHub Secrets
| Secret Name | Value | Deskripsi |
|-------------|-------|-----------|
| `TAILSCALE_AUTH_KEY` | Auth key dari langkah B | Untuk join tailnet |

### Menjalankan Workflow
1. Buka tab **Actions** → **"Playground RDP Tailscale"** workflow
2. Klik **Run workflow** → **Run workflow**
3. Tunggu step **"Establish Tailscale Connection"** selesai
3. Lihat log untuk **Tailscale IP** (format: `100.x.x.x`)
4. Copy **Password** dari step "Display RDP Access Info"

### Koneksi dari Local (Client)

#### Install Tailscale
- **Windows**: https://tailscale.com/download/windows
- **macOS**: https://tailscale.com/download/mac
- **Linux**: `curl -fsSL https://tailscale.com/install.sh | sh`
- **iOS/Android**: App Store / Play Store

#### Login & Connect
1. Buka Tailscale app → **Login** dengan akun yang sama
2. Tunggu status **Connected** (hijau)
3. Catat IP GitHub Runner dari log workflow (misal: `100.64.1.23`)

#### Remote Desktop Connection
- **Computer**: `100.x.x.x:3389` (IP Tailscale dari log)
- **Username**: `RDP`
- **Password**: (dari log workflow)

---

## 🛠 Troubleshooting Umum

### Error 0x708: "Console session in progress"
**Penyebab**: Windows default hanya izinkan 1 session RDP.
**Solusi**: Workflow sudah set `fSingleSessionPerUser=0`. Jika masih error:
- Gunakan `mstsc /admin /v:address:port` (Windows)
- Atau logout user lain di runner sebelum connect

### Error: "Access denied" / Password salah
- Pastikan copy password **persis** dari log (case-sensitive)
- Password di-generate baru tiap run workflow

### Tunnel tidak connect / Timeout
1. Cek secret sudah benar di GitHub Settings → Secrets
2. Cek log workflow untuk error detail
3. Untuk Cloudflare: pastikan tunnel **Healthy** di dashboard
4. Untuk Tailscale: pastikan auth key **Reusable + Ephemeral + Pre-approved**

### RDP Port tidak terbuka
Workflow sudah buka firewall port 3389. Jika masih gagal:
- Cek log step "Verify RDP Connectivity"
- Pastikan service `TermService` running

---

## 🔒 Keamanan

| Aspek | Cloudflare | Ngrok | Tailscale |
|-------|------------|-------|-----------|
| Enkripsi | TLS 1.3 | TLS 1.2+ | WireGuard (ChaCha20-Poly1305) |
| Auth | Tunnel Token | Authtoken | Auth Key + Device Auth |
| Network | Cloudflare Edge | Ngrok Edge | Mesh P2P |
| Audit Log | Ya (Zero Trust) | Ya | Ya (Admin Console) |
| MFA Support | Ya | Ya (paid) | Ya (SSO) |

### Best Practices
- ✅ Gunakan **Ephemeral** auth key (Tailscale) - auto cleanup
- ✅ Rotasi secret berkala
- ✅ Hapus workflow run log setelah selesai (berisi password)
- ✅ Batasi `timeout-minutes` sesuai kebutuhan
- ❌ Jangan commit secret ke repo
- ❌ Jangan share password ke orang lain

---

## 📝 Catatan Teknis

### Arsitektur Koneksi

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Client     │────▶│   Tunnel/VPN     │────▶│ GitHub Runner   │
│ (Your PC)   │     │ (Cloudflare/     │     │ (Windows)       │
│             │     │  Ngrok/Tailscale)│     │ Port 3389 (RDP) │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

### Resource Limits GitHub Actions
- **Windows runners**: 4-core, 16GB RAM, 50GB disk
- **Max timeout**: 360 minutes (6 jam) untuk workflow_dispatch
- **Concurrent jobs**: Tergantung plan (Free: 20 concurrent)

### Port & Protocol
| Metode | Protocol | Port Runner | Port Client |
|--------|----------|-------------|-------------|
| Cloudflare | TCP over TLS | 3389 | 3389 (localhost) |
| Ngrok | TCP | 3389 | Dynamic (0.tcp.ngrok.io:XXXXX) |
| Tailscale | WireGuard/UDP | 3389 | 3389 (direct IP) |

---

## 🤝 Kontribusi

PR welcome untuk:
- Perbaikan bug / optimasi workflow
- Dokumentasi tambahan
- Support metode tunnel lain (ZeroTier, WireGuard manual, dll)

---

## ⚖️ Lisensi

MIT License - Bebas gunakan, modifikasi, distribusi.

---

## 📞 Bantuan

- **GitHub Issues**: Untuk bug report & feature request
- **Cloudflare Docs**: https://developers.cloudflare.com/cloudflare-one/
- **Ngrok Docs**: https://ngrok.com/docs
- **Tailscale Docs**: https://tailscale.com/kb/