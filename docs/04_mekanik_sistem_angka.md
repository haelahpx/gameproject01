# SEMESTER RECEH — Mekanik Inti, Sistem Detail & Tabel Angka

## 1. Loop Permainan
* **Loop Mikro ($10\text{--}30$ detik):** Arahkan crosshair $\rightarrow$ tekan `E` $\rightarrow$ lihat hasil + feedback instan.
* **Loop Harian ($6\text{--}8$ menit):**
  1. Bangun (`06:00`) $\rightarrow$ Lihat "Tujuan Hari Ini" di HP.
  2. Pergi ke kampus, hadiri kelas (wajib di hari kerja).
  3. Pilih $1\text{--}3$ aktivitas bebas (kerja / tugas / organisasi / nongkrong / dekor).
  4. Makan dan jaga energi.
  5. Malam: pulang ke kos, tidur $\rightarrow$ Layar **Rekap Hari Ini** (apa yang terjadi + perubahan angka + teaser besok).
* **Loop Mingguan:** Tiap awal minggu muncul **Kartu Minggu Ini** berisi 3 target kecil opsional (contoh: *"Kerja 2 kali"*, *"Ngobrol dengan Nadia"*, *"Selesaikan tugas Statistika"*). Selesai = bonus uang/hati.
* **Loop Semester:** Mengumpulkan nilai, uang, hubungan, dan reputasi menuju **Rapor Hidup** di Hari ke-36.

---

## 2. Statistik & Waktu

### 2.1 Daftar Statistik (Disederhanakan)
| Lokasi | Statistik | Rentang | Keterangan |
| :--- | :--- | :--- | :--- |
| **HUD (Selalu Tampil)** | **Uang** | $\text{Rp } 0\text{--}\infty$ | Tampil sebagai angka nominal |
| **HUD (Selalu Tampil)** | **Energi** | $0\text{--}100$ | Tampil sebagai progress bar |
| **HUD (Selalu Tampil)** | **Jam & Hari** | `06:00` – `02:00` | Teks jam + hari (misal: *Hari ke-12, Rabu*) |
| **Di dalam HP (`Tab`)** | **IPK** | $0,00\text{--}4,00$ | Dihitung dari kehadiran, tugas, UTS, UAS |
| **Di dalam HP (`Tab`)** | **Reputasi** | $0\text{--}20$ | Dipakai untuk progres organisasi |
| **Di dalam HP (`Tab`)** | **Hati Teman** | $0\text{--}5$ per NPC | Satu angka per NPC (bisa naik $0,5$) |
| **Di dalam HP (`Tab`)** | **Kenyamanan Kamar** | $0\text{--}50$ | Total poin dari perabot yang dipasang di kamar |

### 2.2 Aturan Waktu & Kalender
* **Kecepatan Jam:** Saat berjalan bebas, $1\text{ jam game} \approx 25\text{--}30\text{ detik nyata}$.
* **Lompatan Waktu Aktivitas:** Aktivitas memakai durasi tetap dan langsung melompat dengan transisi layar fade + teks lucu (misal: *"Kelas: 2 jam"*).
* **Pause Otomatis:** Waktu berhenti sepenuhnya saat HP dibuka, saat dialog, atau di menu jeda.
* **Batas Malam:**
  * Jam `24:00`: Efek "ngantuk" ringan (vignette layar agak buram, jalan sedikit melambat).
  * Jam `02:00`: Pemain pingsan di tempat dan terbangun di kamar esok paginya (energi pulih $50\%$, bangun agak siang). Bukan game over.
* **Kalender 1 Semester (36 Hari):**
  * 1 Minggu = 5 hari kuliah (Senin–Jumat) + 1 hari akhir pekan (Sabtu/Minggu digabung jadi 1 hari bebas) = 6 hari.
  * **Kiriman Orang Tua:** Hari 1 dan Hari 19.
  * **Tagihan Kos:** Hari 18 dan Hari 36.
  * **UTS:** Minggu 3 | **Pekan Raya Kampus:** Minggu 5 | **UAS:** Minggu 6.

---

## 3. Tabel Angka Awal (Untuk Balancing)

### 3.1 Tabel Energi (Maksimal 100)
| Aksi | Perubahan Energi | Catatan |
| :--- | :---: | :--- |
| **Kelas (Sikap Fokus / Santai / Tidur)** | $-20 \text{ / } -10 \text{ / } +5$ | Tidur di kelas punya $40\%$ risiko ketahuan |
| **Sesi Tugas (1 jam game)** | $-10$ | Dikerjakan per sesi |
| **Shift Kerja Kantin (3 jam game)** | $-25$ | Mini-game melayani pembeli |
| **Nongkrong (2 jam game)** | $-10$ | Bersama NPC di Kantin/Taman |
| **Rapat Himpunan (Bertahan)** | $-15$ | Pilihan Kabur tidak makan energi |
| **Makan di Warung ($\text{Rp}15.000$)** | $+25$ | — |
| **Masak Mi Instan di Kos ($\text{Rp}4.000$)** | $+15$ | — |
| **Tidur sebelum `23:00`** | Pulih $100\%$ | — |
| **Tidur setelah `23:00`** | Pulih $70\%$ | ditambah bonus kenyamanan kamar |
| **Pingsan jam `02:00`** | Pulih $50\%$ | — |
| **Bonus Kenyamanan Kamar** | $+0\% \text{ s/d } +15\%$ | Menambah persentase pemulihan tidur |

*Jika Energi $< 20$: efek ngantuk. Jika Energi $= 0$: tidak bisa melakukan aktivitas berat sampai makan/tidur.*

### 3.2 Tabel Ekonomi & Uang
| Pos Ekonomi | Nominal |
| :--- | :--- |
| **Uang Awal (Hari 1)** | $\text{Rp}1.000.000$ |
| **Kiriman Orang Tua (Hari 1 & 19)** | $\text{Rp}1.000.000$ per bulan |
| **Tagihan Kos (Hari 18 & 36)** | $\text{Rp}400.000$ per bulan |
| **Makan Harian Rata-rata** | $\pm \text{Rp}20.000$ |
| **Shift Kerja (Gaji Dasar + Tips)** | $\text{Rp}60.000 + \text{tips s/d Rp}40.000$ |
| **Nongkrong** | $\text{Rp}25.000$ |
| **Harga Perabot BelanjaKu** | $\text{Rp}30.000\text{--}\text{Rp}500.000$ |

> **Simulasi Kewajaran 1 Bulan (18 Hari):** Kiriman $\text{Rp}1.000.000 + \text{Kerja 8 shift} (\approx \text{Rp}640.000) = \text{Rp}1.640.000$. Dikurangi Kos ($\text{Rp}400.000$) dan Makan ($\pm \text{Rp}360.000$) $\rightarrow$ Sisa $\pm \text{Rp}880.000$ untuk dekorasi, nongkrong, dan dana darurat.

---

## 4. Sistem Gameplay Detail

### 4.1 Kuliah (Tanpa Mini-Game Wajib)
1. Pergi ke pintu kelas sesuai jadwal $\rightarrow$ tekan `[E] Masuk Kelas`.
2. Pilih 1 dari 3 sikap:
   * **Fokus:** Energi $-20$, Kehadiran + nilai harian tertinggi.
   * **Santai:** Energi $-10$, Kehadiran + nilai sedang (pilihan aman).
   * **Tidur:** Energi $+5$, Kehadiran tetap dapat, nilai rendah, $40\%$ risiko ketahuan dosen (Reputasi $-1$, event lucu).
3. Layar fade $10\text{--}20$ detik dengan teks lucu, waktu maju 2 jam.
4. **Opsi Bolos:** Nilai kehadiran turun, tapi hemat energi dan waktu.
5. **Terlambat:** Masuk setelah jam mulai tetap dihitung hadir, tapi bonus nilai sikap hilang. Pintu tidak pernah dikunci.
6. **Rumus Nilai Akhir & IPK:**
   $$\text{Nilai Akhir} = (0,20 \times \text{Kehadiran}) + (0,30 \times \text{Tugas}) + (0,20 \times \text{UTS}) + (0,30 \times \text{UAS})$$
   $$\text{IPK} = \frac{\text{Nilai Akhir}}{25} \quad (\text{skala } 0,00\text{--}4,00)$$

### 4.2 Tugas Kuliah
* Muncul di tab **Tugas HP** lengkap dengan deadline.
* Dikerjakan di meja belajar kos atau bangku taman dengan menahan `[Tahan E]`.
* Tiap sesi memakan 1 jam game dan $-10$ energi. Tugas biasa butuh $2\text{--}4$ sesi.
* **Terlambat Kumpul:** Nilai tugas menjadi $50\%$ (bukan $0$).
* **Tugas Kelompok (Minggu 2):** 3 pilihan jelas: *"Kerjakan semua sendiri"* (nilai bagus, kuras energi), *"Bagi rata"* (hasil acak, ada anggota menghilang), atau *"Tegur anggota"* (butuh syarat hati teman).

### 4.3 Ujian (UTS Minggu 3, UAS Minggu 6)
* **Format:** 5 soal pilihan ganda, waktu 15 detik per soal (batas waktu bisa dimatikan di menu aksesibilitas).
* **Tema Soal:** Humor dari mata kuliah fiktif (*"Pengantar Receh"*, *"Statistika Perasaan"*).
* **Sistem Hint Otomatis:** Setiap kehadiran penuh dan tugas yang selesai otomatis membuka **Hint 50:50** (menghilangkan 2 jawaban salah) saat ujian berlangsung.

### 4.4 Kerja Part-Time (Kantin Mang Ujang)
* Tekan `[E] Mulai Shift` di meja kantin $\rightarrow$ durasi 3 jam game ($\pm 90$ detik waktu nyata).
* 8 pembeli datang bergantian dengan gelembung pesanan ($1\text{--}2$ item: gorengan, es teh, mi instan).
* Pemain klik item makanan di meja, lalu klik pembeli.
* Kecepatan & ketepatan menentukan **Tips ($\text{Rp}0\text{--}\text{Rp}40.000$)** di atas gaji pokok $\text{Rp}60.000$. Pesanan salah hanya mengurangi tips dan memicu dialog ngomel lucu.

### 4.5 Kos, BelanjaKu & Dekorasi
* **Belanja via HP (Tab BelanjaKu):** Pilih barang & bayar $\rightarrow$ paket tiba **besok pagi** di depan pintu kamar kos.
* **Mode Dekor Sederhana:**
  * Ambil paket dengan `E` $\rightarrow$ buka Inventori Dekor $\rightarrow$ pilih barang.
  * Bayangan barang berwarna **Hijau** (valid) atau **Merah** (tabrakan).
  * `Klik Kiri` = Taruh | `R` = Putar $90^\circ$ | `Klik Kanan` = Batal. Snap otomatis ke grid $0,25\text{ m}$.
  * Barang yang sudah dipasang selalu bisa diambil kembali ke inventori dengan `E`.
* **Tingkat Kenyamanan Kamar:**
  * **Kos Seadanya ($0\text{--}9$ poin):** Pemulihan tidur dasar ($+0\%$).
  * **Lumayan ($10\text{--}24$ poin):** $+5\%$ pemulihan energi.
  * **Estetik ($25\text{--}39$ poin):** $+10\%$ pemulihan energi.
  * **Kos Sultan ($40+$ poin):** $+15\%$ pemulihan energi + Achievement.
* **Pindah Kos:** Batas kenyamanan bergantung pada kos aktif (Petak 28, Kamar Atas 42, Griya Receh 50). Detail di [[08_mekanik_pindah_kos_jabatan_ending]] Bagian A.

### 4.6 Organisasi (Himpunan Mahasiswa)
1. **Bergabung (Minggu 2):** Dialog dengan Kak Rey ("Ikut" / "Nanti dulu").
2. **Rapat Rutin (Rabu Sore, Opsional):** Pilih **Bertahan** (Energi $-15$, Reputasi $+2$, dialog komedi) atau **Kabur** (Reputasi $-1$, adegan menyelinap lucu).
3. **Proposal Pekan Raya (Minggu 3–4):** Siklus revisi komedi bersama Pak Pembina. Ambil catatan $\rightarrow$ revisi 1 sesi di laptop kos $\rightarrow$ serahkan lagi. Disetujui setelah $3\text{--}5$ revisi acak.
4. **Panitia Hari H (Minggu 5):** Pilih $1\text{--}3$ aksi singkat dengan tombol `E`: Pasang Banner, Jaga Registrasi, atau Jadi MC.
5. **Pemilihan Ketua (Minggu 6):** $\text{Reputasi} \ge 15$ = boleh mencalonkan; menang jika Skor Pemilihan $\ge 18$. Jenjang jabatan lengkap (Magang → Ketua) ada di [[08_mekanik_pindah_kos_jabatan_ending]] Bagian B.

### 4.7 Sosial & Percintaan (Should-Lite)
* **Cara Menambah Hati ($0\text{--}5$):** Ngobrol harian ($+0,5$, gratis), Ajak Nongkrong lewat tab Chat HP ($+1$, bayar $\text{Rp}25.000$, 2 jam), Beri Makanan ($+1$), atau pilihan event ($\pm 0,5\text{--}1$).
* **Nongkrong Tanpa Ribet:** Lewat tab Chat HP $\rightarrow$ pilih NPC $\rightarrow$ pilih lokasi (Kantin/Taman) $\rightarrow$ langsung bertemu di lokasi.
* **Pacaran-Lite:** Jika Nadia atau Dika mencapai 5 Hati di Minggu $\ge 5$, terbuka event **"Ajak Jadian"** dan aksi **"Kencan di Taman Malam"**.

---

## 5. Jaring Pengaman (Anti-Frustrasi) & Lampiran Data

### 5.1 Tabel Jaring Pengaman
| Situasi Kritis | Jaring Pengaman Otomatis |
| :--- | :--- |
| **Uang $< \text{Rp}10.000$** | Bu Tini memberi mi instan gratis ($1\times$ per minggu) |
| **Uang habis di akhir bulan** | Telepon Ibu: transfer darurat $\text{Rp}200.000$ ($1\times$ per bulan, plus ceramah lucu) |
| **Tugas terlambat** | Tetap dapat nilai $50\%$, bukan $0$ |
| **Pingsan jam `02:00`** | Bangun di kamar kos tanpa denda uang |
| **IPK akhir $< 2,00$** | Dapat gelar lucu *"Mahasiswa Abadi"*, bukan layar Game Over |

### 5.2 Daftar 15 Barang BelanjaKu
*(Pembagian pembuatan model 3D dibagi rata antara Dev 1 dan Dev 2)*

| # | Nama Barang | Harga | Poin Kenyamanan | Pembuat Model 3D |
| :-: | :--- | :--- | :---: | :---: |
| 1 | Kasur lipat | $\text{Rp}150.000$ | $3$ | Dev 1 |
| 2 | Kasur busa | $\text{Rp}350.000$ | $5$ | Dev 1 |
| 3 | Meja belajar | $\text{Rp}200.000$ | $3$ | Dev 1 |
| 4 | Kursi | $\text{Rp}100.000$ | $2$ | Dev 1 |
| 5 | Lampu belajar | $\text{Rp}50.000$ | $2$ | Dev 1 |
| 6 | Rak buku | $\text{Rp}150.000$ | $3$ | Dev 1 |
| 7 | Karpet | $\text{Rp}80.000$ | $2$ | Dev 1 |
| 8 | Tanaman hias kecil | $\text{Rp}40.000$ | $2$ | Dev 2 |
| 9 | Poster dinding (3 variasi) | $\text{Rp}30.000$ | $1$ | Dev 2 |
| 10 | Lampu tumblr (hiasan) | $\text{Rp}60.000$ | $2$ | Dev 2 |
| 11 | Kipas angin | $\text{Rp}180.000$ | $3$ | Dev 2 |
| 12 | Komputer / monitor | $\text{Rp}500.000$ | $4$ | Dev 2 |
| 13 | Bean bag | $\text{Rp}220.000$ | $3$ | Dev 2 |
| 14 | Lemari kecil | $\text{Rp}250.000$ | $3$ | Dev 2 |
| 15 | Jam dinding | $\text{Rp}45.000$ | $1$ | Dev 2 |

### 5.3 Daftar 14 Pencapaian (Achievements)
1. **Hari Pertama** — Selesaikan Hari 1.
2. **Pejuang Subuh** — Pingsan jam `02:00` untuk pertama kalinya.
3. **Rajin Pangkal Pandai** — Hadir di 10 kelas berturut-turut.
4. **Mi Instan Abadi** — Makan mi instan 15 kali.
5. **Si Paling Revisi** — Revisi proposal 5 kali.
6. **Rapat Sampai Tamat** — Bertahan di 3 rapat berturut-turut.
7. **Kabur Profesional** — Kabur dari 3 rapat.
8. **Sultan Kos** — Capai tingkat kamar Kos Sultan ($40+$ poin).
9. **Tetangga Idaman** — Capai Hati 5 dengan Bagas.
10. **Cinta Kampus** — Jadian dengan Nadia atau Dika.
11. **Pecinta Kucing** — Elus kucing kampus 5 kali.
12. **Ketua Dadakan** — Terpilih jadi ketua himpunan.
13. **Hemat Pangkal Kaya** — Uang akhir semester $\ge \text{Rp}1.500.000$.
14. **Janji Terpenuhi** — Berhasil mencapai "Janji Semester" pilihan awal.