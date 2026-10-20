# SEMESTER RECEH — Visi & Prinsip Desain
**Simulator kehidupan mahasiswa Indonesia.** First-person, 3D low-poly, komedi, sandbox ringan. Dikerjakan 2 developer pemula secara Full-Stack (50:50 Coding & 3D Asset) dengan Godot 4 + GDScript + Blender.

| Atribut | Detail |
| :--- | :--- |
| **Judul Sementara** | Semester Receh (boleh diganti) |
| **Versi Dokumen** | v1.1 (Edisi Kolaborasi Adil / Full-Stack 2 Dev) |
| **Genre** | Life sim, komedi, sandbox ringan |
| **Kamera** | First-person |
| **Visual** | 3D low-poly colorful |
| **Platform** | Windows, Linux, Android (development 100% di Linux — lihat [[09_setup_linux_multiplatform]]) |
| **Durasi Sekali Main** | $\pm 4\text{--}5$ jam (1 semester / 36 hari game) |
| **Waktu Development** | 16 minggu + 2 minggu buffer (lihat [[07_setup_roadmap_adil_2_dev]]) |

---

## 1. Visi dan Pilar Desain
**Pitch satu kalimat:** Kamu anak rantau yang baru masuk kuliah. Uang pas-pasan, jadwal padat, kos sempit, dan hidup selalu penuh kejadian receh. Jalani satu semester dengan caramu sendiri.

### Empat Pilar Desain
| Pilar | Artinya di Game | Contoh |
| :--- | :--- | :--- |
| **Receh dan Relatable** | Humor dari hal sehari-hari mahasiswa | Rapat 3 jam yang hasilnya cuma warna banner |
| **Pilihan Kecil, Dampak Jelas** | Tiap pilihan mudah dipahami dan terasa efeknya | Nongkrong = uang turun, hati teman naik |
| **Santai, Tanpa Hukuman Berat** | Tidak ada game over; kegagalan dibuat lucu | Kehabisan uang $\rightarrow$ makan mi instan gratis dari Bu Kos |
| **Kecil tapi Padat** | Satu kampus, satu kos, banyak kejadian | 6 minggu game, tiap minggu punya cerita |

> **Yang BUKAN tujuan game ini:** Dunia terbuka luas, ekonomi rumit, simulasi akademik mendalam, grafis realistis.

---

## 2. Pengalaman Pemain yang Dituju
* **Target Pemain:** Penggemar game santai (*Stardew Valley*, *Animal Crossing*, *Student Life sims*), anak kuliah atau alumni yang paham humor kampus. Pemain tidak perlu jago main game.
* **Perasaan yang Ingin Dihasilkan:**
  1. Nostalgia dan tertawa (*"ini gue banget"*).
  2. Rasa nyaman dan terkendali (tidak pernah bingung harus ngapain).
  3. Rasa maju (kamar makin bagus, nilai naik, teman makin dekat).
  4. Rasa *"satu hari lagi"* (tiap malam ada rekap lucu dan teaser besok).
* **Pacing Satu Sesi Bermain (Target $30\text{--}45$ menit):**
  * $4\text{--}6$ hari game per sesi, tiap hari $\pm 6\text{--}8$ menit.
  * Ada titik berhenti natural: setiap malam (autosave + rekap).

---

## 3. Prinsip Kenyamanan (Anti-Ribet)
Ini aturan emas desain. Setiap fitur yang dibuat oleh Dev 1 maupun Dev 2 harus lolos daftar ini:

| # | Prinsip | Penerapan |
| :- | :--- | :--- |
| **1** | **Satu tombol interaksi** | Semua interaksi memakai `E`. Prompt selalu tampil: `[E] Masuk Kelas`. |
| **2** | **Maksimal 3 angka di layar** | HUD hanya: Uang, Energi, Jam. Sisanya ada di HP. |
| **3** | **Selalu tahu harus ngapain** | Pojok kanan atas menampilkan 1 baris "Tujuan Hari Ini" + penanda arah di layar. |
| **4** | **Semua menu di satu tempat** | HP pemain (tombol `Tab`). Tidak ada menu tersebar. |
| **5** | **Waktu berhenti di menu/dialog** | Pemain tidak pernah panik karena jam jalan saat baca. |
| **6** | **Tidak ada game over** | Gagal = konsekuensi lucu + jalan keluar. |
| **7** | **Bisa lewati/ulang** | Dialog bisa dipercepat (tahan `E`), tutorial bisa dibuka lagi di HP. |
| **8** | **Autosave pagi & saat tidur** | Pemain tidak perlu pikir soal save manual. |
| **9** | **Satu pelajaran per waktu** | Tutorial mengajarkan satu mekanik per langkah, di dalam cerita. |
| **10**| **Feedback instan** | Setiap aksi: suara kecil + teks melayang (`+Rp 80.000`, `-15 Energi`). |
| **11**| **Teks pendek** | Dialog maksimal 2 baris per kotak; ukuran font bisa diubah. |
| **12**| **Kenyamanan fisik** | Opsi FOV, sensitivitas mouse, head-bob on/off (cegah pusing). |

> **Aturan untuk Developer:** Jika sebuah mekanik butuh lebih dari 3 langkah input atau penjelasan lebih dari 2 kalimat, sederhanakan atau buang.