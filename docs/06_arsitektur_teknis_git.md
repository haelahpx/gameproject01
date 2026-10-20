# SEMESTER RECEH — Arsitektur Teknis & Kolaborasi Git (2 Dev)

Karena **Dev 1** dan **Dev 2** sama-sama menulis kode GDScript dan sama-sama merakit scene 3D di Godot, arsitektur proyek harus modular agar tidak terjadi tabrakan file (*merge conflict*).

## 1. Spesifikasi Teknologi (Kunci Versi!)
* **Game Engine:** Godot Engine **4.5.x Stable atau lebih baru** (dikunci di Hari 1), renderer **Compatibility**. *Catatan: Dev 1 dan Dev 2 WAJIB menggunakan versi angka yang persis sama, jangan pernah update versi Godot di tengah proyek. Alasan & setup Linux/Android: [[09_setup_linux_multiplatform]].*
* **Bahasa Pemrograman:** GDScript dengan *static typing* (`var uang: int = 100000`).
* **Software 3D:** Blender 4.2 LTS (ekspor ke `.glb`).
* **Sistem Dialog:** Addon **Dialogue Manager** (oleh Nathan Hoad) — ringan, berbasis teks, sangat aman untuk Git kolaborasi 2 orang.
* **Version Control:** Git + GitHub + **Git LFS** (wajib untuk file `.glb`, `.png`, `.ogg`, `.wav`).

---

## 2. Struktur Folder Proyek (`res://`)
```text
res://
├── autoload/            # Singleton global (EventBus, GameState, TimeManager, dll.)
├── scenes/
│   ├── world/           # kos.tscn (Dev 1), kampus_luar.tscn (Bersama), kelas.tscn (Dev 2), kantin.tscn (Dev 2), sekretariat.tscn (Dev 1)
│   ├── props/           # Sub-scene perabot & objek interaktif (dibagi 2 dev)
│   ├── player/          # player.tscn (Dev 1)
│   ├── npc/             # npc_base.tscn, npc_bu_tini.tscn, npc_bagas.tscn, dll.
│   ├── ui/              # hud.tscn, phone.tscn, app_tugas.tscn, app_belanja.tscn, dll.
│   └── minigames/       # ujian_ui.tscn (Dev 2), shift_kantin.tscn (Dev 2), mode_dekor.tscn (Dev 1)
├── scripts/
│   ├── core/            # interactable.gd, interaction_ray.gd, resource_definitions/
│   ├── systems/         # sistem_kuliah.gd, sistem_dekor.gd, sistem_organisasi.gd, dll.
│   └── ui/              # skrip tiap tab aplikasi HP
├── data/
│   ├── items/           # *.tres (ItemData - dibagi 2 dev)
│   ├── events/          # *.tres (EventData - #1-10 Dev 1, #11-20 Dev 2)
│   ├── dialogue/        # *.dialogue (file teks dialog per NPC)
│   └── schedule/        # *.tres (jadwal posisi NPC)
├── assets/
│   ├── models/          # file .glb hasil ekspor Blender
│   ├── textures/        # palette_utama.png, ikon UI
│   ├── audio/           # music/, sfx/
│   └── fonts/
└── docs/                # Semua file MD dokumentasi ini
```

---

## 3. Daftar Autoload (Singleton) & Pembagian Pembuatnya
Sistem tidak boleh saling memanggil secara langsung (*tight coupling*), melainkan berkomunikasi lewat `EventBus` dan `GameState`.

| Autoload | Tanggung Jawab Utama | Pembuat Kode |
| :--- | :--- | :---: |
| **`EventBus.gd`** | Kumpulan signal global (`day_started`, `time_changed`, `money_changed`, `energy_changed`, `task_completed`). | **Dev 1** |
| **`GameState.gd`** | Menyimpan seluruh variabel progres pemain (IPK, hati NPC, inventori, flag cerita, jurnal). | **Dev 2** |
| **`TimeManager.gd`** | Mengatur jam (`06:00`–`02:00`), hari ($1\text{--}36$), lompatan waktu aktivitas, dan status *pause*. | **Dev 2** |
| **`Wallet.gd`** | Fungsi tambah/kurang uang, validasi cukup uang, dan pencatatan 10 transaksi terakhir. | **Dev 2** |
| **`SaveManager.gd`** | Serialisasi `GameState` ke `user://save_1.json` lengkap dengan `save_version`. | **Dev 1** |
| **`DialogueRunner.gd`**| Jembatan pemanggil addon Dialogue Manager, menghentikan waktu saat dialog aktif. | **Dev 1** |
| **`AudioManager.gd`** | Memutar musik latar *crossfade*, SFX, dan bunyi *blip* dialog. | **Dev 2** |

---

## 4. Pola Kode Inti (Wajib Dipakai Bersama)

### 4.1 Sistem Interaksi Terpadu (`interactable.gd`)
Semua objek di game (pintu, kasur, NPC, meja belajar, gerobak kantin) menggunakan satu komponen `Area3D` ini:
```gdscript
# res://scripts/core/interactable.gd
class_name Interactable extends Area3D

@export var prompt_text: String = "Interaksi"
signal interacted(player: Node3D)

func interact(player: Node3D) -> void:
	interacted.emit(player)
```

### 4.2 Custom Resource untuk Data (`item_data.gd` & `event_data.gd`)
Agar Dev 1 dan Dev 2 bisa menambah perabot dan event secara paralel tanpa bentrok kode:
```gdscript
# res://scripts/core/item_data.gd
class_name ItemData extends Resource

@export var id: String
@export var nama_barang: String
@export var harga: int = 50000
@export var poin_kenyamanan: int = 2
@export var mesh_scene: PackedScene
@export var ikon: Texture2D
```

### 4.3 Struktur Scene Pemain (`player.tscn`)
Agar visual tangan di layar dan kaki saat menunduk berjalan rapi tanpa membebani game:
```text
player.tscn (CharacterBody3D) - [Dev 1]
├── CollisionShape3D (CapsuleShape3D, radius 0,35m, tinggi 1,7m)
├── Head (Node3D, position y = 1.6)
│   ├── Camera3D (cull_mask: render body/hands, ignore head mesh)
│   └── InteractionRay (RayCast3D, panjang 2.2m)
├── VisualBody (Node3D)
│   └── player_body.glb (Skeleton3D + MeshInstance3D)
│       ├── mesh_head (visible = false untuk kamera player, cast_shadow = ON)
│       ├── mesh_hands (FP hands selalu terlihat di frame bawah)
│       └── mesh_body_legs (terlihat saat kamera Head pitch down)
└── AnimationTree / AnimationPlayer (FP_Idle, FP_Walk, Interact_Reach)
```

---

## 5. Aturan Emas Git untuk 2 Developer Godot
Masalah terbesar pemula saat kolaborasi di Godot adalah **konflik file `.tscn` (scene)**. Ikuti aturan ini agar tidak pernah rusak:

1. **Satu Scene = Satu Pemilik Saat Itu:**
   * Jangan pernah mengedit file `.tscn` yang sama di waktu yang bersamaan.
   * Karena kita membagi **Aplikasi HP per Sub-Scene** (misal `app_belanja.tscn` dipegang Dev 1, `app_tugas.tscn` dipegang Dev 2) dan **Ruangan per Sub-Scene** (`kos.tscn` dipegang Dev 1, `kelas.tscn` dipegang Dev 2), kalian bisa *ngoding* dan mendekorasi level secara bersamaan dengan aman!
2. **Gunakan Branch per Fitur:**
   * Jangan bekerja langsung di branch `main`.
   * Contoh branch Dev 1: `dev1/sistem-dekor`, `dev1/aset-kos`.
   * Contoh branch Dev 2: `dev2/sistem-kantin`, `dev2/aset-kelas`.
3. **Pull Request & Review Singkat:**
   * Setiap selesai 1 fitur kecil, *push* branch dan buat Pull Request (PR) ke `main`. Pasangan dev wajib mengecek dan melakukan *merge*.
4. **Koordinasi `project.godot`:**
   * Saat ingin menambah Autoload atau Input Map baru (yang mengubah file `project.godot`), beri tahu pasangan di Discord terlebih dahulu, lalu langsung *commit & push* agar pasangan bisa langsung *pull*.