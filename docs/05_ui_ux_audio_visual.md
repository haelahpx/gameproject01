# SEMESTER RECEH — UI/UX, Kontrol, Audio & Panduan Visual

## 1. Skema Kontrol (PC)
| Aksi | Tombol |
| :--- | :--- |
| **Gerak** | `W` `A` `S` `D` |
| **Lihat Sekeliling** | `Mouse` |
| **Jalan Cepat (Sprint)** | `Shift` |
| **Interaksi** | `E` (Tekan atau Tahan) |
| **Buka / Tutup HP** | `Tab` |
| **Jeda / Menu Pengaturan** | `Esc` |
| **Putar Barang (Mode Dekor)** | `R` |
| **Percepat Dialog** | `Tahan E` |
| **Menu Debug (Khusus Build Dev)** | `F1` |

### 1.1 Sistem Kamera & Tubuh Pemain (True First-Person)
Game ini menggunakan sistem **True First-Person** yang memvisualisasikan tubuh pemain:

```text
       ┌───────────┐
       │   Kamera  │ (Tinggi mata: 1,6 m - kepala di-cull dari render kamera)
       └─────┬─────┘
             │
      ┌──────┴──────┐
      │  Tangan FP  │ → Terlihat di sudut bawah layar (Idle, ayun saat jalan, raih saat E, pegang HP)
      │             │
      │   Badan     │
      │             │
      │  Kaki/Paha  │ → Terlihat melangkah saat kamera menunduk (pitch down)
      └─────────────┘
```

* **Tangan di Layar (First-Person Hands):**
  * **Idle:** Kedua tangan rileks di sudut bawah kiri-kanan layar tanpa menutupi pandangan utama.
  * **Jalan (Walk/Sprint):** Ayunan tangan berirama halus, memberi rasa kecepatan dan berat tubuh.
  * **Interaksi (`E` / Tombol Interaksi Sentuh):** Tangan kanan maju meraih/menunjuk ke objek interaksi secara instan.
  * **Buka HP (`Tab` / Tombol HP Sentuh):** Animasi tangan mengangkat bodi HP ke depan pandangan pemain secara mulus.
* **Kaki & Tubuh Bawah (*Look-Down Feet*):**
  * Saat pemain menundukkan pandangan (pitch mouse ke bawah atau geser sentuh ke bawah), terlihat dada kaos/hoodie, celana jeans, dan kedua kaki/sepatu yang melangkah.
  * Memberikan rasa kehadiran fisik (*grounded presence*) yang nyata dan memuaskan.
* **Teknik Anti-Kliping Kepala (*Head-Culling*):**
  * Di Blender: bagian kepala dipisah sebagai sub-mesh `mesh_head` atau di-assign ke material layer terpisah.
  * Di Godot: `mesh_head` dimatikan visibilitasnya khusus untuk `Camera3D` pemain (culling mask), sehingga kamera tidak pernah menabrak bagian dalam kepala/mata sendiri.
  * **Bayangan Tetap Utuh:** Properti `cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON` diaktifkan untuk seluruh mesh termasuk kepala, sehingga bayangan karakter pemain di lantai/dinding kampus tetap utuh dan realistis.
* **Performa & Bobot (Aman untuk Android):**
  * Model memakai *Base Mesh Humanoid* low-poly yang sama dengan NPC (< 2.500 tris) dan 1 palet tekstur bersama.
  * Hanya menghasilkan **1 draw call** dan beban komputasi tulang animasi yang sangat minimal. **0% penurunan performa**, berjalan mulus 60 FPS di PC dan 30+ FPS stabil di HP Android RAM 3 GB.

---

## 2. Tata Letak HUD & HP Pemain

### 2.1 HUD Minimalis
```text
┌────────────────────────────────────────────────────────┐
│ Rp 850.000                        Tujuan: Masuk Kelas   │
│ Hari 5 · Jumat · 09:30            (pin di kanan atas)   │
│                                                        │
│                         ·  (crosshair)                 │
│                    [E] Masuk Kelas                     │
│                                                        │
│ ▓▓▓▓▓▓▓▓░░ Energi                                       │
└────────────────────────────────────────────────────────┘
```
* Crosshair berupa titik kecil di tengah layar; berubah jadi lingkaran + teks prompt saat mengarah ke objek `Interactable`.
* Penanda arah (ikon melayang di layar) menunjuk ke "Tujuan Hari Ini" (bisa dimatikan di pengaturan).
* Teks melayang (*floating text*) saat uang atau energi bertambah/berkurang.

### 2.2 Menu HP Pemain (Buka dengan `Tab`)
Semua menu terpusat di layar HP dengan **6 aplikasi (tab)**. Aturan UI: teks besar, tombol besar, maksimal kedalaman 2 layar, `Esc` selalu kembali.

| Aplikasi (Tab) | Isi Layar | Pembuat UI & Kode |
| :--- | :--- | :---: |
| **1. Tugas** | Jadwal hari ini, daftar tugas + deadline, Kartu Minggu Ini | **Dev 2** |
| **2. Chat** | Daftar teman, indikator Hati, tombol "Ajak Nongkrong", pesan masuk | **Dev 1** |
| **3. BelanjaKu**| Katalog 15 perabot kos, harga, poin kenyamanan, tombol Beli | **Dev 1** |
| **4. Dompet** | Saldo saat ini, 10 riwayat transaksi terakhir, info tagihan kos | **Dev 2** |
| **5. Rapor** | IPK sementara, rincian nilai (Kehadiran/Tugas/UTS/UAS), Reputasi, Jurnal | **Dev 2** |
| **6. Lainnya** | Bantuan (buka ulang tutorial), Pengaturan Aksesibilitas, Save Manual, Keluar | **Dev 1** |

### 2.3 Kotak Dialog & Aksesibilitas
* **Kotak Dialog:** Di bagian bawah layar, menampilkan nama NPC + maksimal 2 baris teks + bunyi *"blip"* per huruf (pitch suara berbeda tiap NPC, tanpa *voice acting*).
* **Pengaturan Aksesibilitas Wajib:**
  * Slider FOV ($60\text{--}100$, default $75$).
  * Sensitivitas Mouse.
  * Toggle Head-bob (Default: Rendah / Bisa Mati untuk mencegah *motion sickness*).
  * Ukuran Teks (Kecil / Sedang / Besar).
  * Toggle Batas Waktu Ujian (Nyala / Mati).
  * Slider Volume terpisah (Master, Musik, SFX, Blip Dialog).

---

## 3. Panduan Audio & Gaya Visual (Style Guide)

### 3.1 Kebutuhan Audio
* **Musik Latar (4 Loop Lo-Fi):** Tema Kos, Tema Kampus Siang, Tema Kerja/Semangat, Tema Malam Santai.
* **Efek Suara ($\pm 25$ SFX):** Langkah kaki, klik UI HP, notifikasi chat, koin/bayar, makan, bel kelas, ketukan pintu, lembaran kertas, suara ngantuk. (Dibuat dengan JSFXR / ChipTone atau aset lisensi CC0).

### 3.2 Aturan Visual 3D (Low-Poly Colorful)
Agar model buatan **Dev 1** dan **Dev 2** terlihat seragam seperti dibuat oleh satu orang, keduanya wajib mematuhi aturan ini di Blender:

| Aspek Visual | Standar Wajib untuk Dev 1 & Dev 2 |
| :--- | :--- |
| **Skala Dunia** | $1\text{ unit Blender/Godot} = 1\text{ meter}$. Tinggi kamera mata pemain $= 1,6\text{ m}$. Tinggi pintu $= 2,0\text{ m}$. |
| **Titik Origin** | Origin objek wajib berada di **tengah bawah (lantai)** objek. Wajib tekan `Ctrl+A -> All Transforms` sebelum ekspor. |
| **Bentuk Geometri** | Kotak/silinder sederhana, sudut tegas, gunakan sedikit *Bevel* ($1\text{ segmen}$) pada pinggiran meja/lemari agar menangkap cahaya. |
| **Warna & Material** | Gunakan **1 File Texture Palette Bersama (`palette_utama.png`)** berisi $16\text{--}24$ kotak warna hangat-pastel. Di Blender, cukup *UV Unwrap -> Project from View* dan geser UV ke kotak warna yang diinginkan. Jangan gunakan tekstur foto realistis! |
| **Batas Poligon** | Prop kecil (gelas, buku) $< 500\text{ tris}$ \| Perabot (kasur, meja) $< 1.000\text{ tris}$ \| Karakter NPC $< 3.000\text{ tris}$. |
| **Format Ekspor** | Ekspor sebagai **glTF 2.0 (`.glb`)**. Gunakan penamaan jelas: `prop_meja_belajar.glb`, `env_dinding_kos.glb`, `chr_bagas.glb`. |