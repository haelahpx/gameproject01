# SEMESTER RECEH — Karakter, NPC & Lokasi Dunia

## 1. Daftar Karakter & NPC
Hubungan romansa dibatasi dua opsi (Nadia atau Dika, siapa pun bisa dipilih, tanpa batasan gender pemain) agar konten terkendali.

| Tokoh | Peran | Kepribadian | Fungsi Gameplay | Pembagian Aset & Kode (Dev 1 & Dev 2) |
| :--- | :--- | :--- | :--- | :--- |
| **Kamu** | Mahasiswa baru | Ditentukan pemain | Tokoh utama. **True First-Person Body:** kedua tangan terlihat di layar saat santai/aksi, kaki melangkah terlihat saat menunduk, kepala di-cull dari kamera agar tidak kliping | **Dev 1:** Model variasi `player_body.glb`, setup culling kepala, rig animasi tangan/kaki, controller kamera & jalan |
| **Bu Tini** | Ibu kos | Galak tapi sayang, hobi nagih | Tagihan kos, tutorial, bantuan darurat (mi gratis), kos kamar atas | **Dev 1:** Model variasi & dialog tutorial |
| **Bagas** | Tetangga kamar kos | Santai, hobi ngutang & ngajak nongkrong | Teman, sumber event receh, komedi | **Dev 1:** Model variasi & event receh kos |
| **Nadia** | Teman sekelas | Rajin, tenang, diam-diam lucu | Teman, tugas kelompok, opsi romansa | **Dev 1:** Model variasi & rute hati/romansa |
| **Pak Pembina** | Pembina Himpunan | Birokrat santai tapi perfeksionis | Menerima/merevisi proposal Pekan Raya | **Dev 1:** Model variasi & dialog proposal |
| **Pak Darmawan** | Dosen | Killer tapi adil, suka kuis dadakan | Kelas, tugas, ujian | **Dev 2:** Model variasi & sistem kelas/ujian |
| **Mang Ujang** | Pemilik warung kantin | Hangat, banyak cerita | Tempat kerja part-time | **Dev 2:** Model variasi & sistem kantin |
| **Kak Rey** | Senior, ketua himpunan | Karismatik, selalu *"kita rapat dulu ya"* | Pintu masuk organisasi, promosi jabatan, panitia | **Dev 2:** Model variasi & sistem organisasi |
| **Dika** | Anak seni/UKM | Ceria, impulsif, banyak ide aneh | Teman, event acara kampus, opsi romansa | **Dev 2:** Model variasi & rute hati/romansa |
| **Kucing Kampus**| Kucing liar | Misterius, muncul saat kamu stres | Koleksi dan momen menyenangkan | **Bersama:** Model low-poly simpel (Dev 1) & animasi (Dev 2) |

---

## 2. Panduan Teknis Pembuatan NPC (Untuk Dev 1 & Dev 2)
* **Basis Karakter Bersama:** Dev 1 dan Dev 2 membuat **1 Base Mesh Manusia Low-Poly** secara bersama-sama di awal (atau menggunakan 1 base mesh gratis yang disepakati), lalu masing-masing memodifikasi rambut, baju, dan warna untuk NPC jatahnya.
* **Batas Poligon:** Maksimal $< 3.000$ segitiga (triangles) per NPC.
* **Animasi Wajib (Hanya 3):** `Idle`, `Walk`, `Talk` (bisa menggunakan Mixamo pada *base rig* yang sama).
* **Sistem Pergerakan (Tanpa Pathfinding Rumit):** NPC memiliki jadwal (`ScheduleData`: jam $\rightarrow$ titik lokasi). Saat jam berganti dan pemain tidak melihat, NPC langsung dipindahkan (*teleport*) ke titik jadwalnya.

---

## 3. Latar dan Peta Dunia

### 3.1 Waktu
Masa kini. Satu semester = 6 minggu game = 36 hari game.

### 3.2 Tata Letak Peta (Versi 1: 3 Area Utama)
```text
 [AREA KOS] ──jalan kecil (30 detik jalan)── [GERBANG KAMPUS]
                                                   │
         ┌─────────────────────────────────────────┴────────────────────┐
         │  Gedung Kelas     Sekretariat Himpunan    Kantin Mang Ujang  │
         │                Lapangan / Taman (nongkrong)                  │
         └──────────────────────────────────────────────────────────────┘
```

| Lokasi | Isi Ruangan | Fungsi Gameplay | Penanggung Jawab 3D & Level |
| :--- | :--- | :--- | :--- |
| **Kos** | Kamar pemain, lorong, ruang bersama kecil, kamar Bagas, rumah Bu Tini di depan | Tidur, dekorasi, belajar, paket belanja | **Dev 1** (Greybox, 3D Modular Kos, Interior) |
| **Gedung Kelas** | 1 ruang kelas, koridor, ruang dosen | Kuliah, ujian, konsultasi | **Dev 2** (Greybox, 3D Modular Kelas, Meja/Papan) |
| **Sekretariat Himpunan** | 1 ruangan penuh barang kepanitiaan | Rapat, proposal, tugas panitia | **Dev 1** (Interior Sekretariat, Properti Rapat) |
| **Kantin Mang Ujang** | Warung tenda/bangunan kecil dengan meja kerja | Makan, kerja part-time, nongkrong | **Dev 2** (Gerobak/Warung, Properti Makanan) |
| **Lapangan / Taman** | Area terbuka kecil, bangku, pohon, jalan penghubung | Nongkrong, kencan, event acara kampus | **Dev 1 & Dev 2** (Kolaborasi prop pohon, bangku, banner) |

* **Aturan Skala Peta:** Dari kos ke kelas maksimal $\pm 45$ detik berjalan, dan dari titik mana pun di kampus ke tujuan lain maksimal $\pm 20$ detik. Peta kecil mencegah rasa bosan berjalan.

### 3.3 Waktu Hari dan Suasana
Empat preset pencahayaan (`WorldEnvironment` & `DirectionalLight3D`):
1. **Pagi (06:00 - 10:59):** Cerah, sejuk.
2. **Siang (11:00 - 14:59):** Terik, bayangan tegas.
3. **Sore (15:00 - 17:59):** Oranye hangat (*golden hour*).
4. **Malam (18:00 - 02:00):** Biru gelap, lampu kos dan lampu taman menyala hangat.