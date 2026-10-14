# Playground RDP - GitHub Actions Remote Desktop

Repository ini berisi workflow GitHub Actions untuk memberi akses Remote Desktop (RDP) atau SSH
ke runner GitHub Actions menggunakan beberapa metode tunneling berbeda.

## 📋 Daftar Workflow

| Workflow | Metode Tunnel | OS Support | Setup | Status |
|----------|---------------|------------|-------|--------|
| `rdp-cloudflare.yml` | Cloudflare Tunnel | Windows only | Domain + tunnel token | ✅ legacy |
| `rdp-ngrok.yml` | Ngrok TCP | Windows only | Akun + authtoken | ✅ legacy |
| `rdp-tailscale.yml` | Tailscale (WireGuard) | Windows only | Akun + auth key | ✅ legacy |
| `rdp-zerotier.yml` | ZeroTier (mesh VPN) | **Win + Linux + macOS** | Network ID | ✅ baru |

> ⚠️ **Penting soal input `os`:** hanya `rdp-zerotier.yml` yang benar-benar menghormati input `os`.
> Tiga workflow lama (`rdp-cloudflare`, `rdp-ngrok`, `rdp-tailscale`) sudah teruji dan **masih Windows-only**
> — step-nya memakai `shell: pwsh` + registry Windows (`HKLM:`, `New-LocalUser`, `netsh`).
> Memilih `ubuntu-latest`/`macos-latest` di sana akan **gagal**.
> Alasan file tersebut sengaja tidak diubah: sudah teruji dipakai, dan tidak ingin merusak yang sudah jalan.
> Lihat [Pilih OS Runner](#pilih-os-runner-workflow-input).

### Memilih titik awal tercepat

| Kalau Anda… | Pakai |
|---|---|
| Sudah pakai Ngrok/Tailscale/Cloudflare (Windows) | workflow legacy-nya |
| Butuh **Linux atau macOS** | `rdp-zerotier.yml` |
| Mau **RDP sekaligus opsi SSH** | `rdp-zerotier.yml` + input `protocol` |

### 🔒 Catatan keamanan

Semua workflow ini membuat **akun Administrator dengan password acak** lalu mengeksposnya lewat
internet publik. Itu inherent pada konsepnya. Yang bisa dilakukan:

- Hapus log run setelah selesai — log berisi password / private key
- Pakai `protocol: ssh` bila hanya butuh terminal (lebih ringan daripada RDP)
- Jangan pernah simpan kredensial penting di runner yang diakses lewat tunnel ini

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

## 🪐 4. ZeroTier (`rdp-zerotier.yml`)

> Workflow **termuda dan paling lengkap**: satu-satunya yang benar-benar jalan di ketiga OS
> (Windows/Linux/macOS), dan punya step cleanup yang proper.

### Fitur
- Mesh VPN alternatif dari Tailscale (layer berbeda, jadi cadangan bila Tailscale bermasalah)
- Gratis untuk personal, tanpa kartu kredit
- Bawaan composite action sehingga setup per-OS tidak diulang tiap workflow
- Lifecycle node dijaga: `zerotier-cli leave` otomatis jalan saat workflow cancelled/failed

### Persiapan (Sekali Saja)

1. Daftar di [my.zerotier.com](https://my.zerotier.com/)
2. Login → **Networks** → **Create a Network**
3. Beri nama, pilih **Access type**:
   - **Private** — perlu otorisasi manual tiap node (paling aman)
   - **Public** — langsung dapat IP tanpa otorisasi (paling gampang, kurang aman)
4. Catat **Network ID** (16 karakter hex, contoh: `a1b2c3d4e5f6a7b8`)

> Network ID bisa diisi saat Run workflow, **atau** disimpan sebagai repository secret
> bernama `ZEROTIER_NETWORK_ID` supaya tidak perlu di-paste tiap kali.

### Menjalankan Workflow
1. Buka tab **Actions** → **"Playground RDP (ZeroTier)"**
2. **Run workflow** → isi:
   - **network_id**: Network ID (boleh dikosongkan jika secret `ZEROTIER_NETWORK_ID` sudah ada)
   - **custom_password**: opsional, kosongkan untuk auto-generate
   - **os**: pilih `windows-latest` / `ubuntu-latest` / `macos-latest`
   - **protocol**: opsional — `auto` (default), `rdp`, atau `ssh`
3. Tunggu step **"Install & Join ZeroTier"** selesai
4. Copy **Computer** dari step "Display RDP Access Info"

> ⚠️ **Jika network pakai Access type = Private**, node akan tertahan di status *Pending*.
> Buka **my.zerotier.com → Networks → <network Anda> → Machines**, cari node `gh-runner-*`,
> klik **Authorize**, lalu jalankan ulang workflow.

### Koneksi dari Local (Client)

#### Install ZeroTier
- **Windows**: https://www.zerotier.com/download/
- **macOS**: https://www.zerotier.com/download/
- **Linux**: `curl -s https://install.zerotier.com | sudo sh`
- **iOS/Android**: App Store / Play Store

#### Login & Connect
1. Buka ZeroTier app → **Login** dengan akun yang memiliki network tersebut
2. Tunggu status **Connected** (hijau)
3. Catat IP dari log workflow (format `10.x.x.x` untuk network private, atau `999.x.x.x` untuk public)

### 🔀 Pilih RDP atau SSH (`protocol`)

| `protocol` | Windows | Ubuntu | macOS |
|------------|---------|--------|-------|
| `auto` (default) | RDP 3389 | xrdp 3389 | SSH 22 |
| `rdp` | RDP 3389 | xrdp 3389 | ❌ error jelas |
| `ssh` | SSH 22 | SSH 22 | SSH 22 |

`macos-latest` tidak bisa RDP sama sekali — runner itu tidak punya console session,
jadi Screen Sharing selalu black screen. Kalau pilih `rdp` di macOS, workflow gagal
dengan pesan yang menjelaskan alasannya.

#### RDP (Windows/Linux)
- **Computer**: `10.x.x.x:3389` (dari log)
- **Username**: `RDP`
- **Password**: (dari log workflow)

#### SSH (semua OS)
- **Computer**: `10.x.x.x:22` (dari log)
- **User**: `runner` (user bawaan runner, bukan user `RDP`)
- **Auth**: private key yang dicetak di log workflow

```bash
# simpan private key dari log, lalu:
ssh -i playground_key -p 22 runner@10.x.x.x
```

> ⚠️ Private key dicetak penuh di log run. Hapus log run setelah key tersimpan aman di mesin Anda.

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

### Error ZeroTier: node dapat IP tapi tidak bisa dijangkau
- **Access type Private**: node harus di-*Authorize* dulu di my.zerotier.com → Machines
- Jalur P2P gagal → ZeroTier fallback ke relay, jadi tetap jalan tapi latency lebih tinggi

### `protocol: ssh` — private key tidak muncul di log
- Runner memakai user bawaan (`runner`), bukan user `RDP`
- Key hanya dicetak di step "Display RDP Access Info"; kalau workflow gagal sebelum
  step itu, key memang belum pernah di-generate

---

## 🔒 Keamanan

| Aspek | Cloudflare | Ngrok | Tailscale | ZeroTier |
|-------|------------|-------|-----------|----------|
| Enkripsi | TLS 1.3 | TLS 1.2+ | WireGuard (ChaCha20-Poly1305) | ZeroTier E2E crypto |
| Auth | Tunnel Token | Authtoken | Auth Key + Device Auth | Device identity + Network auth |
| Network | Cloudflare Edge | Ngrok Edge | Mesh P2P | Mesh P2P (relay bila P2P gagal) |
| Audit Log | Ya (Zero Trust) | Ya | Ya (Admin Console) | Ya (Central) |
| MFA Support | Ya | Ya (paid) | Ya (SSO) | Tidak (personal plan) |

### Best Practices
- ✅ Gunakan **Ephemeral** auth key (Tailscale) - auto cleanup
- ✅ Pakai **Access type = Private** (ZeroTier) + autorisasi node secara manual
- ✅ Rotasi secret berkala
- ✅ Hapus workflow run log setelah selesai (berisi password / private key)
- ✅ Batasi `timeout-minutes` sesuai kebutuhan
- ❌ Jangan commit secret ke repo
- ❌ Jangan share password ke orang lain

---

## 📝 Catatan Teknis

### Arsitektur Koneksi

```
┌─────────────┐     ┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  Client     │────▶│   Tunnel/VPN        │────▶│  GitHub Actions      │     │   Runner OS         │
│ (Your PC)   │     │ (Cloudflare/        │     │  Workflow Runs       │     │  (pilihan:         │
│             │     │  Ngrok/Tailscale/   │     │  1. Setup RDP/SSH   │     │   windows-latest/  │
│             │     │  ZeroTier)          │     │  2. Start Tunnel     │     │   ubuntu-latest/   │
│             │     │                     │     │                     │     │   macos-latest)    │
└─────────────┘     └─────────────────────┘     └──────────────────────┘     │                   │
                                                                              └─────────────────────┘
```

**Alur lengkap:**
1. **Workflow dijalankan** → GitHub menyediakan runner (VM)
2. **Setup RDP/SSH** → Enable RDP (Windows) atau xrdp/SSH (Linux/macOS), buat user, buka firewall
3. **Start Tunnel Service** → Cloudflare Tunnel / Ngrok / Tailscale / ZeroTier
4. **Client connect** → Via tunnel ke runner:3389 (RDP) atau port SSH

### Pilih OS Runner (Workflow Input)

Semua workflow punya input `os`, **tetapi tidak semua workflow mendukung semua OS.**

| Workflow | `windows-latest` | `ubuntu-latest` | `macos-latest` |
|----------|:----------------:|:---------------:|:---------------:|
| `rdp-cloudflare.yml` | ✅ | ❌ | ❌ |
| `rdp-ngrok.yml` | ✅ | ❌ | ❌ |
| `rdp-tailscale.yml` | ✅ | ❌ | ❌ |
| `rdp-zerotier.yml` | ✅ | ✅ | ✅ |

> ❌ = akan **gagal** di step setup, bukan "jalan tanpa fitur". Ketiga workflow lama masih memakai
> `shell: pwsh` + registry Windows (`HKLM:`, `New-LocalUser`, `netsh`). Input `os` di sana
> warisan dari versi awal dan sengaja tidak diubah karena ketiga workflow sudah teruji dipakai.

Keempat workflow baru berbagi composite action `.github/actions/setup-rdp`, jadi perilaku
per-OS identik di semua workflow tersebut:

| OS | Protokol | Port | Cara kerja |
|----|----------|------|------------|
| `windows-latest` | RDP native | 3389 | Registry `Terminal Server` + `TermService`, user via `net user` |
| `ubuntu-latest` | xrdp | 3389 | `apt install xrdp xfce4`, desktop xfce (bukan black screen), user via `useradd` |
| `macos-latest` | SSH | 22 | Generate keypair `ed25519`, masukkan ke `~/.ssh/authorized_keys` |

**Kenapa macOS pakai SSH, bukan RDP?**
Runner `macos-latest` tidak punya console/display yang ter-attach, sehingga Screen Sharing (VNC/RDP)
tidak punya session untuk di-render — hasilnya black screen regardless of konfigurasi.
SSH adalah jalur remote access yang benar-benar bekerja di runner macOS, jadi itu yang dipakai.
Private key-nya dicetak di log run.

> ⚠️ **Catatan**: 
> - Untuk repo **public** gratis, workflow lama yang Windows-only **tidak bisa dipakai** — butuh GitHub Team/Enterprise, atau Actions minutes dari private repo. Pakai `rdp-zerotier.yml` dengan `ubuntu-latest` sebagai gantinya.
> - macOS runner memiliki batasan concurrent jobs lebih ketat

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
| ZeroTier | ZeroTier E2E (UDP, relay fallback) | 3389 | 3389 (managed IP) |

> Dengan `protocol: ssh`, port runner jadi **22** untuk semua OS.
> Port **22** juga dipakai otomatis di `macos-latest` (RDP tidak mungkin di sana).

---

## 🤝 Kontribusi

PR welcome untuk:
- Perbaikan bug / optimasi workflow
- Dokumentasi tambahan
- Setup remote access untuk OS runner lain (Windows arm64, Fedora, dll)
- Metode tunnel **tanpa server milik sendiri** (nilai plusnya: repo ini tidak butuh VPS)

> Metode yang butuh VPS (WireGuard hub, frps server, bore server sendiri) sengaja tidak
> disertakan: premis repo ini adalah *tidak perlu infrastruktur tambahan* besides a throwaway runner.

### Struktur Repo

```
.github/
├── workflows/
│   ├── rdp-cloudflare.yml    # Windows-only (legacy, tested)
│   ├── rdp-ngrok.yml         # Windows-only (legacy, tested)
│   ├── rdp-tailscale.yml     # Windows-only (legacy, tested)
│   └── rdp-zerotier.yml      # Windows + Linux + macOS
└── actions/
    ├── setup-rdp/            # Per-OS remote access setup (RDP / xrdp / SSH)
    ├── setup-zerotier/       # ZeroTier per-OS + join network  ← dipakai rdp-zerotier.yml
    ├── setup-cloudflare/     # cloudflared per-OS + start tunnel  ← belum dipakai
    ├── setup-ngrok/          # ngrok v3 per-OS + TCP tunnel       ← belum dipakai
    └── setup-tailscale/      # Tailscale per-OS + join tailnet   ← belum dipakai
```

> **Satu action per metode tunnel**, plus `setup-rdp` sebagai primitif bersama yang dipakai
> workflow baru (Windows RDP / Linux xrdp / macOS SSH).

> ⚠️ **Catatan penting — action yang belum terpakai:**
> `setup-cloudflare`, `setup-ngrok`, dan `setup-tailscale` **belum direferensikan workflow mana pun**,
> karena ketiga workflow lamanya sengaja tidak diubah (sudah teruji).
> Action tersebut ada sebagai referensi/registry yang siap dipakai saat ketiga workflow legacy
> suatu saat di-migrasi ke composite action — tapi **sampai itu terjadi, action itu belum pernah
> dieksekusi**. Jangan dianggap sudah teruji.
>
> Workflow legacy sengaja dibiarkan apa adanya — kalau menambah metode tunnel baru,
> ikuti pola `rdp-zerotier.yml`, jangan sentuh yang legacy kecuali ada bug nyata.

### ✅ Apa yang sudah diverifikasi di runner sungguhan

Pengujian dilakukan dengan menjalankan workflow di GitHub-hosted runner sungguhan
bukan hanya validasi statis:

| Kombinasi | Hasil |
|---|---|
| `windows-latest` + RDP + Ngrok | ✅ port 3389 listen |
| `ubuntu-latest` + xrdp + Ngrok | ✅ port 3389 listen |
| `ubuntu-latest` + SSH + Ngrok | ✅ `SSH-2.0-OpenSSH_9.6p1 Ubuntu` |
| `macos-latest` + SSH + Ngrok | ✅ port 22 listen |

`setup-rdp` terverifikasi di keempat kombinasi. Tunnel ZeroTier belum diuji end-to-end.

---

## ⚖️ Lisensi

MIT License - Bebas gunakan, modifikasi, distribusi.

---

## 📞 Bantuan

- **GitHub Issues**: Untuk bug report & feature request
- **Cloudflare Docs**: https://developers.cloudflare.com/cloudflare-one/
- **Ngrok Docs**: https://ngrok.com/docs
- **Tailscale Docs**: https://tailscale.com/kb/