# Playground RDP - GitHub Actions Remote Desktop

Repository ini berisi workflow GitHub Actions untuk membuat akses Remote Desktop (RDP) ke runner Windows GitHub Actions menggunakan tiga metode tunneling berbeda.

## 📋 Daftar Workflow

| Workflow | Metode Tunnel | OS Support | Butuh Server Sendiri? | Setup |
|----------|---------------|------------|:---------------------:|-------|
| `rdp-cloudflare.yml` | Cloudflare Tunnel | Windows only | ❌ | Domain + tunnel token |
| `rdp-ngrok.yml` | Ngrok TCP | Windows only | ❌ | Akun + authtoken |
| `rdp-tailscale.yml` | Tailscale (WireGuard) | Windows only | ❌ | Akun + auth key |
| `rdp-zerotier.yml` | ZeroTier (mesh VPN) | **Win + Linux + macOS** | ❌ | Network ID |
| `rdp-bore.yml` | bore (public TCP) | **Win + Linux + macOS** | ❌ | **Nol** — langsung jalan |
| `rdp-wireguard.yml` | WireGuard (mesh VPN) | **Win + Linux + macOS** | ✅ | VPS + WireGuard hub |
| `rdp-frp.yml` | frp (TCP reverse proxy) | **Win + Linux + macOS** | ✅ | VPS + frps server |

> ⚠️ **Penting soal input `os`:** hanya 4 workflow baru (`zerotier`, `bore`, `wireguard`, `frp`) yang
> benar-benar menghormati input `os`. Tiga workflow lama (`rdp-cloudflare`, `rdp-ngrok`, `rdp-tailscale`)
> sudah teruji dan **masih Windows-only** — step-nya memakai `shell: pwsh` + registry Windows
> (`HKLM:`, `New-LocalUser`, `netsh`). Memilih `ubuntu-latest`/`macos-latest` di sana akan **gagal**.
> Alasan file tersebut sengaja tidak diubah: sudah teruji dipakai, dan saya tidak ingin merusak yang sudah jalan.
> Lihat [Pilih OS Runner](#pilih-os-runner-workflow-input).

### Picking the fastest starting point

| Kalau Anda… | Pakai |
|---|---|
| Mau coba **sekarang, tanpa akun** | `rdp-bore.yml` |
| Mau **gratis + privat**, tanpa VPS | `rdp-tailscale.yml` (Windows) / `rdp-zerotier.yml` (semua OS) |
| Sudah punya domain | `rdp-cloudflare.yml` |
| Sudah punya VPS | `rdp-wireguard.yml` (tercepat) atau `rdp-frp.yml` (fleksibel) |

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

> Tidak ada GitHub Secret yang dibutuhkan — Network ID dikirim sebagai input saat Run workflow.

### Menjalankan Workflow
1. Buka tab **Actions** → **"Playground RDP (ZeroTier)"**
2. **Run workflow** → isi:
   - **network_id**: Network ID dari langkah di atas (wajib)
   - **custom_password**: opsional, kosongkan untuk auto-generate
   - **os**: pilih `windows-latest` / `ubuntu-latest` / `macos-latest`
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

#### Remote Desktop Connection (Windows/Linux)
- **Computer**: `10.x.x.x:3389` (dari log)
- **Username**: `RDP`
- **Password**: (dari log workflow)

---

## 🕳️ 5. bore (`rdp-bore.yml`)

> **Paling cepat untuk coba-coba: tanpa akun, tanpa setup, tanpa domain.**

### Fitur
- TCP tunnel publik, **nol konfigurasi** — langsung jalan begitu workflow di-run
- Tidak perlu akun, domain, kartu kredit, atau VPS
- Client **tidak perlu install apa-apa** — cukup `mstsc`
- Binary statis kecil (~1 MB), built for Windows/Linux/macOS (amd64 & arm64)

### Persiapan
Tidak ada. Langsung ke **Actions → Run workflow**.

### Koneksi dari Local (Client)
- **Computer**: `bore.pub:XXXXX` (dari log workflow)
- **Username**: `RDP`
- **Password**: (dari log workflow)

> ⚠️ **Endpoint `bore.pub` sepenuhnya publik tanpa autentikasi tambahan.**
> Satu-satunya pengaman RDP Anda adalah password yang di-generate (24 karakter acak).
> Ini **tidak** cocok untuk akses jangka panjang atau mesin yang berisi data sensitif.

### Self-hosted bore server
Kalau punya VPS sendiri, jalankan `bore server --secret <secret>` di sana, lalu isi input
**bore server** dengan alamatnya. Password disimpan sebagai GitHub Secret `BORE_SECRET`.

---

## 🔐 6. WireGuard (`rdp-wireguard.yml`)

> Mesh VPN level-3, performa tertinggi. **Butuh VPS + WireGuard hub milik Anda sendiri.**

### Fitur
- Layer 3 (bukan proxy) → performa & latency terbaik di antara semua metode di repo ini
- Tidak ada port yang dibuka di runner: semua traffic ter-tunnel
- Kriptografi modern (Curve25519 / ChaCha20-Poly1305)
- Mendukung Pre-Shared Key untuk hardening pasca-kuantum

### Persiapan (Sekali Saja)
1. Siapkan VPS Linux dengan **UDP 51820 terbuka**.
2. Install WireGuard, lalu **buat interface `wg0` sebagai hub**:
   ```bash
   # /etc/wireguard/wg0.conf di VPS
   [Interface]
   Address    = 10.8.0.1/24
   ListenPort = 51820
   PrivateKey = <private-key-hub-anda>
   # PublicKey  = <dari blok peer di bawah>

   [Peer]                       # peer = runner ini
   #PublicKey = <runner public key dari log workflow>
   AllowedIPs = 10.8.0.2/32
   ```
3. `sudo sysctl -p && sudo wg-quick up wg0`
4. Catat **PublicKey hub** (`: wg pubkey < private-key-hub>`).

### Menjalankan Workflow
Isi saat Run workflow:
- **hub_public_key** (wajib) — PublicKey hub
- **hub_endpoint** (wajib) — `ip-vps-anda:51820`
- **tunnel_address** — default `10.8.0.2/32`
- **hub_address** — default `10.8.0.1/32`

### Koneksi dari Local (Client)
> **Dua langkah, urutan penting.**

1. **Tambahkan runner sebagai peer di hub** — salin PublicKey runner dari log workflow ke
   `wg0.conf` di VPS, lalu `sudo wg syncconf wg0 <(wg-quick strip wg0)`.
2. Di device klien, import konfigurasi mesh hub Anda → mstsc ke `10.8.0.2:3389`.

---

## 🔗 7. frp (`rdp-frp.yml`)

> TCP reverse proxy yang Anda host sendiri. Paling fleksibel untuk multi-port.

### Fitur
- Proxy TCP/UDP level-7, bukan VPN — hanya traffic yang di-proxy yang terekspos
- `frps` (server) ringan, jalan di VPS sekecil 512 MB
- Auth token + TLS antara client dan server
- Cocok kalau butuh banyak proxy dari banyak runner

### Persiapan (Sekali Saja)
1. VPS Linux, buka **TCP 7000** (bind port frps).
2. Download `frps` dan jalankan dengan config:
   ```toml
   # frps.toml di VPS
   bindPort = 7000
   auth.token = "token-sama-dengan-di-workflow"
   # Batasi port yang boleh dipakai runner:
   allowPorts = [{ start = 33890, end = 33999 }]
   ```
3. Jalankan: `./frps -c frps.toml`

### Menjalankan Workflow
- **server_addr** (wajib) — IP/domain VPS
- **server_port** — default `7000`
- **auth_token** (wajib) — harus sama dengan `auth.token` di frps
- **remote_port** — default `33890`, harus berada dalam rentang `allowPorts`

### Koneksi dari Local (Client)
- **Computer**: `ip-vps-anda:33890`
- **Username**: `RDP`
- **Password**: (dari log workflow)

> ⚠️ Kalau step gagal dengan `auth mismatch`, `port not allowed`, atau `connection refused`,
> log frpc sudah mencetak penyebabnya — jalankan ulang workflow untuk melihatnya.

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
│             │     │  ZeroTier/bore/     │     │  2. Start Tunnel     │     │   ubuntu-latest/   │
│             │     │  WireGuard/frp)     │     │                     │     │   macos-latest)    │
└─────────────┘     └─────────────────────┘     └──────────────────────┘     │   macos-latest)    │
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
| `rdp-bore.yml` | ✅ | ✅ | ✅ |
| `rdp-wireguard.yml` | ✅ | ✅ | ✅ |
| `rdp-frp.yml` | ✅ | ✅ | ✅ |

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
| bore | TCP | 3389 | 3389 (bore.pub:random) |
| WireGuard | WireGuard/UDP | 3389 | 3389 (tunnel IP) |
| frp | TCP | 3389 | 3389 (hub IP:remote port) |

> Untuk `macos-latest`, port runner = **22** (SSH), bukan 3389.

---

## 🤝 Kontribusi

PR welcome untuk:
- Perbaikan bug / optimasi workflow
- Dokumentasi tambahan
- Support metode tunnel lain (WireGuard manual, frp, Playit, dll)
- Setup remote access untuk OS runner lain (Windows arm64, Fedora, dll)

### Struktur Repo

```
.github/
├── workflows/
│   ├── rdp-cloudflare.yml    # Windows-only (legacy, tested)
│   ├── rdp-ngrok.yml         # Windows-only (legacy, tested)
│   ├── rdp-tailscale.yml     # Windows-only (legacy, tested)
│   ├── rdp-zerotier.yml      # Windows + Linux + macOS
│   ├── rdp-bore.yml          # Windows + Linux + macOS
│   ├── rdp-wireguard.yml     # Windows + Linux + macOS
│   └── rdp-frp.yml           # Windows + Linux + macOS
└── actions/
    ├── setup-rdp/            # Per-OS remote access setup (RDP / xrdp / SSH) — dipakai semua workflow baru
    ├── setup-cloudflare/     # cloudflared per-OS + start tunnel
    ├── setup-ngrok/          # ngrok v3 per-OS + TCP tunnel
    ├── setup-tailscale/      # Tailscale per-OS + join tailnet
    ├── setup-zerotier/       # ZeroTier per-OS + join network
    ├── setup-bore/           # Download prebuilt bore + open public TCP tunnel
    ├── setup-wireguard/      # Generate keypair + bring up wg0 peer
    └── setup-frp/            # Download frpc + register TCP proxy
```

> **Satu action per metode tunnel**, plus `setup-rdp` sebagai primitif bersama yang dipakai
> keempat workflow baru (Windows RDP / Linux xrdp / macOS SSH).

> ⚠️ **Catatan penting — action yang belum terpakai:**
> `setup-cloudflare`, `setup-ngrok`, dan `setup-tailscale` **belum direferensikan workflow mana pun**,
> karena ketiga workflow lamanya sengaja tidak diubah (sudah teruji).
> Action tersebut ada sebagai referensi/registry yang siap dipakai saat ketiga workflow legacy
> suatu saat di-migrasi ke composite action — tapi **sampai itu terjadi, action itu belum pernah
> dieksekusi**. Jangan dianggap sudah teruji.
>
> Workflow legacy sengaja dibiarkan apa adanya — kalau menambah metode tunnel baru,
> ikuti pola `rdp-bore.yml` (paling sederhana), jangan sentuh yang legacy kecuali ada bug nyata.

---

## ⚖️ Lisensi

MIT License - Bebas gunakan, modifikasi, distribusi.

---

## 📞 Bantuan

- **GitHub Issues**: Untuk bug report & feature request
- **Cloudflare Docs**: https://developers.cloudflare.com/cloudflare-one/
- **Ngrok Docs**: https://ngrok.com/docs
- **Tailscale Docs**: https://tailscale.com/kb/