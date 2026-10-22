# 🎓 MahasiswaIni

> **Simulator Kehidupan Mahasiswa Indonesia**  
> *First-Person 3D Low-Poly · Comedy · Relatable Campus Life · Cozy Sandbox*

[![Godot Engine](https://img.shields.io/badge/Godot_Engine-4.7+-478CBF?logo=godotengine&logoColor=white)](https://godotengine.org)
[![Blender](https://img.shields.io/badge/Blender-4.5+-F5792A?logo=blender&logoColor=white)](https://www.blender.org)
[![Platform](https://img.shields.io/badge/Platforms-Linux%20%7C%20Windows%20%7C%20Android-green.svg)](#-target-platform)
[![Git LFS](https://img.shields.io/badge/Git_LFS-Enabled-orange.svg)](https://git-lfs.github.com)
[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)](#-lisensi)

---

## 📖 Tentang Game

**MahasiswaIni** adalah game simulasi kehidupan mahasiswa rantau di Indonesia dengan sudut pandang orang pertama (*first-person*) dan visual 3D *low-poly* yang cerah (*colorful*). 

Kamu bermain sebagai anak rantau yang baru menjejakkan kaki di dunia perkuliahan. Uang pas-pasan, jadwal kuliah padat, kamar kos sempit, serta keseharian yang selalu dipenuhi kejadian receh dan kocak. Mulai dari bertahan hidup di akhir bulan, menghadapi tagihan ibu kos, rapat organisasi berjam-jam yang tak berujung, hingga menata kamar kos idaman — tentukan caramu sendiri dalam menjalani satu semester perkuliahan!

### ✨ Pilar Desain Utama
- **Receh & Relatable**: Lelucon dan humor khas realita mahasiswa Indonesia (rapat 3 jam demi warna spanduk, makan mi instan saat dompet menipis, tugas mepet tenggat).
- **Pilihan Sederhana, Dampak Nyata**: Setiap aktivitas berdampak jelas pada Uang, Energi, Nilai Akademik, dan Relasi Pertemanan.
- **Santai & Anti-Pusing**: Tanpa hukuman *Game Over* yang memberatkan; kegagalan selalu dibalut konsekuensi kocak dan solusi jalan keluar.
- **Kecil tapi Padat**: Lingkungan kampung kos dan kampus yang hidup dengan beragam interaksi di setiap sudutnya.

---

## 🎮 Fitur Unggulan

- **🏘️ Eksplorasi Kampung Kos & Kampus**:
  Jelajahi gang-gang sempit perkampungan kos Indonesia, warung makan/kantin, gerbang dorong interaktif, jalanan dengan trotoar belang, hingga gedung fakultas perkuliahan.
- **📱 Smartphone Mahasiswa (HP Virtual)**:
  Tekan `Tab` untuk membuka smartphone in-game: periksa saldo rekening, jadwal kuliah harian, kalender semester, chat grup teman/dosen, serta katalog perabotan.
- **🛏️ Kustomisasi & Pindah Kos**:
  Mulai dari kos petakan super sederhana (*Extremely Poor Kost*) dengan kasur lantai dan kipas angin berisik, kumpulkan uang dari beasiswa atau kerja sampingan untuk *upgrade* ke kos yang lebih nyaman (*Kos Bu Kondang*).
- **⏰ Siklus Waktu & Semester Dinamis**:
  Simulasi waktu 1 semester (6 minggu perkuliahan / 36 hari in-game) dengan sistem jam dinamis, transisi waktu, dan *autosave* otomatis saat pagi dan tidur.
- **🕹️ Input Ergonomis Lintas Platform**:
  Sistem interaksi *Single-Button Contextual* (`[E]`, sentuhan, atau `[A]` gamepad) yang otomatis mendeteksi objek di depan karakter.

---

## 🕹️ Skema Kontrol

Game dirancang menggunakan arsitektur `InputRouter` yang mendukung Keyboard & Mouse, Layar Sentuh (*Android Touch Controls*), dan Gamepad:

| Aksi | PC (Keyboard & Mouse) | Android (Touch Screen) | Gamepad (Xbox / Steam Deck) |
| :--- | :--- | :--- | :--- |
| **Gerak** | `W` `A` `S` `D` | Virtual Joystick Dinamis (Layar Kiri) | Stik Kiri |
| **Kamera / Arah Pandang** | Gerakan Mouse | Drag Sentuh (Layar Kanan) | Stik Kanan |
| **Interaksi Utama** | `E` | Tombol Interaksi Kontekstual | Tombol `A` / `✕` |
| **Tahan Interaksi** | Tahan `E` | Tahan Tombol Interaksi (Progress Ring) | Tahan `A` |
| **Buka Smartphone (HP)** | `Tab` | Ikon HP 📱 (Kanan Atas) | `Y` / `△` |
| **Sprint / Lari Cepat** | `Shift` | Tombol Toggle Sprint 🏃 | `L3` (Tekan Stik) |
| **Jeda / Kembali** | `Esc` | Ikon Pause ⏸ / Tombol Back HP | `Start` / `B` |
| **Dekorasi: Rotasi Objek** | `R` | Tombol Rotasi ⟳ | `RB` |
| **Dekorasi: Konfirmasi** | Klik Kiri | Tombol Simpan ✔ | `A` |

---

## 📁 Struktur Proyek

```text
gameproject01/
├── art_source/                 # Sumber aset 3D mentah (.blend, palet warna, konsep)
├── builds/                     # Hasil kompilasi ekspor game (Windows, Linux, APK)
├── docs/                       # Dokumentasi Game Design Document (GDD) & Roadmap
│   ├── 01_visi_prinsip_desain.md
│   ├── 02_karakter_dunia.md
│   ├── 03_cerita_event_humor.md
│   ├── 04_mekanik_sistem_angka.md
│   ├── 05_ui_ux_audio_visual.md
│   ├── 06_arsitektur_teknis_git.md
│   ├── 07_setup_roadmap_adil_2_dev.md
│   ├── 08_mekanik_pindah_kos_jabatan_ending.md
│   └── 09_setup_linux_multiplatform.md
├── game/
│   └── new-game-project/       # Root Project Godot Engine
│       ├── assets/             # Model 3D (glTF/glb), tekstur palet, audio, UI
│       ├── scenes/             # Scene Godot (.tscn)
│       │   ├── levels/         # Level: kampung_kos_level, campus_area, kos_greybox
│       │   ├── player/         # Karakter pemain & kamera first-person
│       │   └── ui/             # Virtual controls, smartphone UI, HUD
│       ├── scripts/            # Skrip GDScript (.gd)
│       │   ├── core/           # InputRouter, interaksi, waktu, dialog
│       │   ├── gameplay/       # Sistem kos, perkuliahan, mini-game
│       │   └── ui/             # Kontrol sentuh, virtual joystick, menu
│       ├── tools/              # Skrip generator & otomasi scene (Python/GDScript)
│       ├── export_presets.cfg  # Preset konfigurasi ekspor platform
│       └── project.godot       # Pengaturan utama proyek Godot
└── OWNERSHIP.md                # Pembagian modul kerja tim pengembang
```

---

## 🚀 Memulai Pengembangan (Quick Start)

### 1. Prasyarat Sistem
* **[Godot Engine 4.5+ / 4.7+](https://godotengine.org/download)** (Vulkan Forward+ / Compatibility)
* **[Git LFS (Large File Storage)](https://git-lfs.github.com)** *(Wajib untuk aset 3D & audio binary)*
* **[Blender 4.5 LTS+](https://www.blender.org/download/)** *(Untuk pemodelan dan pengeditan aset 3D)*
* **Python 3.10+** *(Opsional, untuk menjalankan skrip automasi `tools/`)*

### 2. Kloning Repositori
Pastikan Git LFS sudah diinisialisasi sebelum melakukan kloning:

```bash
# Inisialisasi Git LFS
git lfs install

# Kloning repositori
git clone https://github.com/haelahpx/gameproject01.git
cd gameproject01

# Pastikan seluruh file binary LFS telah terunduh
git lfs pull
```

### 3. Membuka di Godot Engine
1. Jalankan aplikasi **Godot Engine**.
2. Klik tombol **Import** di Project Manager.
3. Arahkan ke folder: `game/new-game-project/project.godot`.
4. Buka proyek dan biarkan Godot melakukan impor aset awal.
5. Tekan **F5** untuk menjalankan game dari scene utama (`scenes/levels/kampung_kos_level.tscn` / `main.tscn`).

---

## 📱 Target Platform & Spesifikasi Performa

| Metrik | Desktop (Linux / Windows) | Mobile (Android) |
| :--- | :--- | :--- |
| **Spesifikasi Acuan** | Laptop iGPU (Intel UHD 620 / Vega 8), RAM 8 GB | RAM 3–4 GB, SoC Helio G85 / Snapdragon 680 |
| **Target Frame Rate** | 60 FPS @ 1080p | 30–60 FPS @ Render Scale 75–100% |
| **Kompleksitas Poligon** | < 300k segitiga per frame | < 100k segitiga per frame |
| **Draw Calls** | < 500 per frame | < 150 per frame (Shared Color Palette) |
| **Format Ekspor** | `.x86_64` (Linux) / `.exe` (Windows) | `.apk` / `.aab` (Android 8.0+) |

---

## 🛠️ Tim Pengembang & Kontribusi

Proyek ini dikembangkan secara kolaboratif dengan pembagian peran terstruktur (lihat rincian di [`OWNERSHIP.md`](file:///home/haelahpx/Documents/GitHub/gameproject01/OWNERSHIP.md)):
- **Core System & UI**: `res://scripts/core/`, `res://scenes/ui/`, Settings & Input Map.
- **Gameplay & Level Design**: `res://scenes/levels/`, `res://scripts/gameplay/`, 3D Level Art, Build & Export Pipelines.

### Alur Kerja Git (Git Workflow)
1. Selalu buat branch baru dari `main` untuk setiap fitur baru: `feature/<nama-fitur>`.
2. Lakukan pengujian di branch lokal sebelum membuat Pull Request.
3. Pastikan branch `main` selalu dalam kondisi *clean* dan siap rilis.

---

## 📄 Lisensi
Hak Cipta © 2026 Tim Pengembang MahasiswaIni. Seluruh aset, kode, dan konten kreatif dilindungi hak cipta untuk keperluan proyek permainan ini.
