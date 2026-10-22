"""
Script to build the interior layout of the Campus Building in Blender:
1. Grand Entrance Lobby (wide open, spacious sightline when opening windows/doors)
2. Back Stairs (at the back of the central atrium ascending to Floor 2 mezzanine)
3. Back Elevator / Lift (in the back corner serving Floor 1 and Floor 2)
4. Perpustakaan (Library section in West Forward wing)
5. Toilet / Restrooms (in West Rear wing)
6. Ruang Kelas 101 (Classroom section in East Forward wing)
7. Ruang Meja Dosen (Faculty Office section in East Rear wing)
All props are strictly INSIDE the building walls. Outdoor courtyards are kept clean.
"""

import bpy  # pyrefly: ignore[missing-import] # type: ignore
import math

def get_or_create_mat(name, rgba, roughness=0.5, metallic=0.0, transmission=0.0, emission=None):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = rgba
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = transmission
        if emission and 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission[0]
            bsdf.inputs['Emission Strength'].default_value = emission[1]
    return mat

def create_box(name, loc, size, mat=None, collection=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if collection and obj.name not in collection.objects:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        collection.objects.link(obj)
    return obj

def create_cyl(name, loc, radius, depth, mat=None, rot=(0,0,0), collection=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=16, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if mat:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    if collection and obj.name not in collection.objects:
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        collection.objects.link(obj)
    return obj

def build_interior():
    ca = bpy.data.collections.get("CampusArea")
    if not ca:
        ca = bpy.data.collections.new("CampusArea")
        bpy.context.scene.collection.children.link(ca)

    # Clean previous generated interior objects
    prefixes = [
        "InWall_", "Lobby_", "Stair_", "Lift_", "Perpus_", "Toilet_", "Kelas_", "Dosen_",
        "IntDoor_", "Sign_"
    ]
    to_remove = [o for o in ca.objects if any(o.name.startswith(p) for p in prefixes)]
    for o in to_remove:
        bpy.data.objects.remove(o, do_unlink=True)
    print(f"Cleaned {len(to_remove)} previous interior objects.")

    # Materials
    m_wall_cream = get_or_create_mat("Mat_Int_WallCream", (0.92, 0.90, 0.85, 1.0), roughness=0.6)
    m_wall_white = get_or_create_mat("Mat_Int_WallWhite", (0.95, 0.95, 0.95, 1.0), roughness=0.5)
    m_tile_floor = get_or_create_mat("Mat_Int_TileLobby", (0.85, 0.85, 0.88, 1.0), roughness=0.25)
    m_tile_wc = get_or_create_mat("Mat_Int_TileWC", (0.75, 0.85, 0.90, 1.0), roughness=0.2)
    m_wood_dark = get_or_create_mat("Mat_Int_WoodDark", (0.28, 0.16, 0.08, 1.0), roughness=0.4)
    m_wood_light = get_or_create_mat("Mat_Int_WoodLight", (0.72, 0.54, 0.35, 1.0), roughness=0.45)
    m_wood_desk = get_or_create_mat("Mat_Int_WoodDesk", (0.55, 0.38, 0.22, 1.0), roughness=0.35)
    m_metal_dark = get_or_create_mat("Mat_Int_MetalDark", (0.15, 0.15, 0.17, 1.0), roughness=0.3, metallic=0.8)
    m_metal_silver = get_or_create_mat("Mat_Int_MetalSilver", (0.75, 0.77, 0.80, 1.0), roughness=0.25, metallic=0.9)
    m_glass = get_or_create_mat("Mat_Int_Glass", (0.85, 0.92, 0.95, 1.0), roughness=0.05, transmission=0.9)
    m_screen = get_or_create_mat("Mat_Int_Screen", (0.05, 0.08, 0.15, 1.0), roughness=0.2, emission=((0.2, 0.4, 0.8, 1.0), 1.5))
    m_whiteboard = get_or_create_mat("Mat_Int_Whiteboard", (0.96, 0.96, 0.96, 1.0), roughness=0.1)
    m_book_red = get_or_create_mat("Mat_Int_BookRed", (0.75, 0.15, 0.15, 1.0), roughness=0.5)
    m_book_blue = get_or_create_mat("Mat_Int_BookBlue", (0.15, 0.30, 0.75, 1.0), roughness=0.5)
    m_book_green = get_or_create_mat("Mat_Int_BookGreen", (0.15, 0.60, 0.25, 1.0), roughness=0.5)
    m_cushion_blue = get_or_create_mat("Mat_Int_CushionBlue", (0.18, 0.28, 0.55, 1.0), roughness=0.7)
    m_cushion_black = get_or_create_mat("Mat_Int_CushionBlack", (0.10, 0.10, 0.10, 1.0), roughness=0.6)
    m_porcelain = get_or_create_mat("Mat_Int_Porcelain", (0.95, 0.97, 0.98, 1.0), roughness=0.15)
    m_plant_green = get_or_create_mat("Mat_Int_PlantGreen", (0.12, 0.45, 0.12, 1.0), roughness=0.6)
    m_pot_white = get_or_create_mat("Mat_Int_PotWhite", (0.90, 0.90, 0.90, 1.0), roughness=0.3)
    m_brass = get_or_create_mat("Mat_Int_Brass", (0.85, 0.70, 0.25, 1.0), roughness=0.3, metallic=0.85)

    # -------------------------------------------------------------------------
    # FLOOR MATERIALS SETUP (Fix missing texture and assign specialized room floors)
    # -------------------------------------------------------------------------
    import os
    img_path = "/home/haelahpx/Documents/GitHub/gameproject01/game/new-game-project/assets/textures/floor_tiles_nat.png"
    img_floor = bpy.data.images.get("floor_tiles_nat.png.001")
    if not img_floor and os.path.exists(img_path):
        img_floor = bpy.data.images.load(img_path)
        img_floor.name = "floor_tiles_nat.png.001"
    elif img_floor and os.path.exists(img_path):
        img_floor.filepath = img_path
        img_floor.reload()

    # Lobby & Atrium Floor Material
    m_lobby_floor = bpy.data.materials.get("Mat_InteriorFloor.001")
    if m_lobby_floor and m_lobby_floor.use_nodes:
        fnodes = m_lobby_floor.node_tree.nodes
        flinks = m_lobby_floor.node_tree.links
        fnodes.clear()
        f_out = fnodes.new('ShaderNodeOutputMaterial')
        f_out.location = (400, 0)
        f_bsdf = fnodes.new('ShaderNodeBsdfPrincipled')
        f_bsdf.location = (100, 0)
        f_bsdf.inputs['Roughness'].default_value = 0.22
        if 'Specular IOR Level' in f_bsdf.inputs:
            f_bsdf.inputs['Specular IOR Level'].default_value = 0.6
        f_bsdf.inputs['Base Color'].default_value = (0.90, 0.88, 0.85, 1.0)
        if img_floor:
            f_tex = fnodes.new('ShaderNodeTexImage')
            f_tex.location = (-200, 0)
            f_tex.image = img_floor
            f_tex.extension = 'REPEAT'
            f_map = fnodes.new('ShaderNodeMapping')
            f_map.location = (-400, 0)
            f_map.inputs['Scale'].default_value = (8.0, 8.0, 1.0)
            f_coord = fnodes.new('ShaderNodeTexCoord')
            f_coord.location = (-600, 0)
            flinks.new(f_coord.outputs['UV'], f_map.inputs['Vector'])
            flinks.new(f_map.outputs['Vector'], f_tex.inputs['Vector'])
            flinks.new(f_tex.outputs['Color'], f_bsdf.inputs['Base Color'])
        flinks.new(f_bsdf.outputs['BSDF'], f_out.inputs['Surface'])

    # Specialized room floor materials
    m_floor_lib = get_or_create_mat("Mat_Floor_Library", (0.65, 0.45, 0.26, 1.0), roughness=0.38)
    m_floor_wc = get_or_create_mat("Mat_Floor_Toilet", (0.80, 0.89, 0.93, 1.0), roughness=0.20)
    m_floor_class = get_or_create_mat("Mat_Floor_Classroom", (0.86, 0.86, 0.88, 1.0), roughness=0.35)
    m_floor_dosen = get_or_create_mat("Mat_Floor_Dosen", (0.36, 0.22, 0.13, 1.0), roughness=0.30)

    floor_mappings = [
        ("Floor_Interior_LeftFwd-col", m_floor_lib),
        ("Floor_Interior_Left-col", m_floor_wc),
        ("Floor_Interior_RightFwd-col", m_floor_class),
        ("Floor_Interior_Right-col", m_floor_dosen),
    ]
    for fname, fmat in floor_mappings:
        fobj = bpy.data.objects.get(fname)
        if fobj:
            if fobj.data.materials:
                fobj.data.materials[0] = fmat
            else:
                fobj.data.materials.append(fmat)

    # =========================================================================
    # 1. INTERIOR PARTITION WALLS & ARCHWAYS
    # =========================================================================
    # Wall height from floor Z=0.40 to ceiling Z=4.28 -> height=3.88, center Z=2.34
    wh = 3.88
    wz = 0.40 + wh / 2.0  # 2.34
    door_h = 2.40
    door_wz = 0.40 + door_h + (wh - door_h) / 2.0  # lintel center Z = 3.54
    lintel_h = wh - door_h  # 1.48

    # A. West Wall separating Atrium and West Hallway (along X = -54.18, Y in [-115.25, -105.25])
    # Opening for corridor: Y in [-112.5, -110.0] (width 2.5m)
    # South partition: Y in [-115.25, -112.5] (length 2.75m, center Y = -113.875)
    create_box("InWall_West_South-col", (-54.18, -113.875, wz), (0.25, 2.75, wh), m_wall_cream, ca)
    # North partition: Y in [-110.0, -105.25] (length 4.75m, center Y = -107.625)
    create_box("InWall_West_North-col", (-54.18, -107.625, wz), (0.25, 4.75, wh), m_wall_cream, ca)
    # Lintel over West doorway (Y in [-112.5, -110.0])
    create_box("InWall_West_Lintel-col", (-54.18, -111.25, door_wz), (0.25, 2.50, lintel_h), m_wall_cream, ca)

    # B. East Wall separating Atrium and East Hallway (along X = -42.18, Y in [-115.25, -105.25])
    # Opening for corridor: Y in [-112.5, -110.0] (width 2.5m)
    # South partition: Y in [-115.25, -112.5] (length 2.75m, center Y = -113.875)
    create_box("InWall_East_South-col", (-42.18, -113.875, wz), (0.25, 2.75, wh), m_wall_cream, ca)
    # North partition: Y in [-110.0, -105.25] (length 4.75m, center Y = -107.625)
    create_box("InWall_East_North-col", (-42.18, -107.625, wz), (0.25, 4.75, wh), m_wall_cream, ca)
    # Lintel over East doorway (Y in [-112.5, -110.0])
    create_box("InWall_East_Lintel-col", (-42.18, -111.25, door_wz), (0.25, 2.50, lintel_h), m_wall_cream, ca)

    # C. Partition separating Library (West Fwd) and Restrooms (West Rear) along Y = -115.25
    # X in [-69.18, -61.18] (length 8.0m). Doorway at X in [-65.0, -63.0] (width 2.0m)
    # West section: X in [-69.18, -65.0] (length 4.18m, center X = -67.09)
    create_box("InWall_Perpus_West-col", (-67.09, -115.25, wz), (4.18, 0.25, wh), m_wall_cream, ca)
    # East section: X in [-63.0, -61.18] (length 1.82m, center X = -62.09)
    create_box("InWall_Perpus_East-col", (-62.09, -115.25, wz), (1.82, 0.25, wh), m_wall_cream, ca)
    # Lintel over Library door
    create_box("InWall_Perpus_Lintel-col", (-64.0, -115.25, door_wz), (2.0, 0.25, lintel_h), m_wall_cream, ca)
    # Library Door Header Sign
    create_box("Sign_Perpus_Header", (-64.0, -115.10, 2.75), (1.8, 0.06, 0.35), m_wood_dark, ca)

    # D. Partition separating Classroom 101 (East Fwd) and Ruang Dosen (East Rear) along Y = -115.25
    # X in [-35.18, -27.18] (length 8.0m). Doorway at X in [-33.0, -31.0] (width 2.0m)
    # West section: X in [-35.18, -33.0] (length 2.18m, center X = -34.09)
    create_box("InWall_Kelas_West-col", (-34.09, -115.25, wz), (2.18, 0.25, wh), m_wall_cream, ca)
    # East section: X in [-31.0, -27.18] (length 3.82m, center X = -29.09)
    create_box("InWall_Kelas_East-col", (-29.09, -115.25, wz), (3.82, 0.25, wh), m_wall_cream, ca)
    # Lintel over Classroom door
    create_box("InWall_Kelas_Lintel-col", (-32.0, -115.25, door_wz), (2.0, 0.25, lintel_h), m_wall_cream, ca)
    # Classroom Door Header Sign
    create_box("Sign_Kelas_Header", (-32.0, -115.10, 2.75), (1.8, 0.06, 0.35), m_wood_dark, ca)

    # E. Toilet Entrance Privacy Partition in West Wing
    # Along X = -60.0, Y in [-114.5, -107.5], door opening at Y in [-114.5, -112.5]
    create_box("InWall_Toilet_Screen-col", (-60.0, -109.5, wz), (0.20, 4.0, wh), m_wall_white, ca)
    create_box("InWall_Toilet_Lintel-col", (-60.0, -113.5, door_wz), (0.20, 2.0, lintel_h), m_wall_white, ca)
    create_box("Sign_Toilet_Header", (-59.85, -113.5, 2.75), (0.06, 1.4, 0.35), m_metal_dark, ca)

    # =========================================================================
    # 2. GRAND ENTRANCE LOBBY (Wide Open Front Area)
    # =========================================================================
    # Floor Inlay / Carpet Runner in front lobby
    create_box("Lobby_Floor_Runner", (-48.18, -116.0, 0.405), (3.6, 5.5, 0.01), m_tile_floor, ca)

    # Reception / Welcome Counter (off to the East side: X = -44.5, Y = -116.2)
    # Keeps the central entrance axis completely wide open!
    create_box("Lobby_Reception_Desk-col", (-44.5, -116.2, 0.40 + 0.55), (2.2, 0.8, 1.10), m_wood_dark, ca)
    create_box("Lobby_Reception_CounterTop", (-44.5, -116.2, 0.40 + 1.12), (2.3, 0.9, 0.05), m_wood_light, ca)
    create_box("Lobby_Reception_PC", (-44.2, -116.2, 0.40 + 1.32), (0.45, 0.15, 0.35), m_screen, ca)
    create_box("Lobby_Reception_Chair-col", (-43.5, -116.2, 0.40 + 0.45), (0.5, 0.5, 0.9), m_cushion_black, ca)

    # University Directory / Information Display (off to the West side: X = -52.2, Y = -116.5)
    create_box("Lobby_Directory_Stand-col", (-52.2, -116.5, 0.40 + 0.90), (0.2, 1.4, 1.8), m_metal_dark, ca)
    create_box("Lobby_Directory_Screen", (-52.08, -116.5, 0.40 + 1.25), (0.02, 1.2, 0.8), m_screen, ca)

    # Modern Planter Pots flanking entrance columns
    for px, py in [(-46.0, -118.2), (-50.36, -118.2)]:
        create_box(f"Lobby_Planter_{px:.1f}-col", (px, py, 0.40 + 0.35), (0.6, 0.6, 0.7), m_pot_white, ca)
        create_box(f"Lobby_Plant_{px:.1f}", (px, py, 0.40 + 0.90), (0.7, 0.7, 0.5), m_plant_green, ca)

    # Waiting Bench along West Wall
    create_box("Lobby_Bench_West-col", (-53.7, -113.5, 0.40 + 0.25), (0.6, 2.2, 0.48), m_wood_light, ca)
    create_box("Lobby_Bench_West_Cushion", (-53.7, -113.5, 0.40 + 0.52), (0.55, 2.1, 0.08), m_cushion_blue, ca)

    # =========================================================================
    # 3. BACK STAIRS (Against North Back Wall - Ascending West to Floor 2)
    # =========================================================================
    # Floor 2 North Bridge: adjust to leave open stairwell behind it
    f2_north = bpy.data.objects.get("Floor2_Center_North-col")
    if f2_north:
        f2_north.location = (-48.18, -108.325, 4.28)
        f2_north.dimensions = (12.0, 1.85, 0.25)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Floor 2 Top Stair Landing Slab (connects top of stairs to North Bridge and West Wing)
    create_box("Floor2_Stair_Landing-col", (-52.69, -106.325, 4.28), (2.98, 2.15, 0.25), m_tile_floor, ca)

    # Stairs along back wall: Center Y = -106.30, width = 1.70m (Y in [-107.15, -105.45])
    # Starts at X = -45.5 (Z = 0.40), ascends West to X = -51.5 (Z = 4.40)
    num_steps = 18
    step_rise = 4.0 / num_steps  # ~0.222m
    step_run = 6.0 / num_steps   # ~0.333m
    stair_w = 1.70
    stair_cy = -106.30

    for i in range(num_steps):
        s_x = -45.5 - (i + 0.5) * step_run
        s_z = 0.40 + (i + 0.5) * step_rise
        # Step block
        create_box(f"Stair_Step_{i}-col", (s_x, stair_cy, s_z), (step_run + 0.04, stair_w, step_rise), m_tile_floor, ca)
        # Wooden tread nose
        create_box(f"Stair_Tread_{i}", (s_x, stair_cy, s_z + step_rise / 2.0), (step_run + 0.06, stair_w + 0.04, 0.03), m_wood_dark, ca)

    # Stair Stringer along South (front) side of stair run
    beam_len = math.sqrt(4.0**2 + 6.0**2)
    beam_angle = math.atan2(4.0, 6.0)
    str_y = stair_cy - stair_w / 2.0 - 0.04
    b = create_box("Stair_Stringer_Front-col", (-48.5, str_y, 2.40), (beam_len, 0.08, 0.25), m_metal_dark, ca)
    b.rotation_euler = (0, beam_angle, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # Handrail along South (front) side of stair run
    hr = create_box("Stair_Handrail_Front-col", (-48.5, str_y, 3.30), (beam_len, 0.05, 0.08), m_metal_silver, ca)
    hr.rotation_euler = (0, beam_angle, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # Safety Balustrade along Landing edge
    create_box("Stair_Landing_Railing-col", (-51.2, -106.325, 4.90), (0.08, 2.15, 1.0), m_metal_silver, ca)

    # Restore Floor 2 North Railing across the North Bridge overlooking atrium
    r_north = bpy.data.objects.get("Railing2_Atrium_North-col")
    if r_north:
        r_north.location = (-48.18, -109.25, 4.90)
        r_north.dimensions = (6.4, 0.08, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    r_north_g = bpy.data.objects.get("Railing2_Atrium_North_Glass")
    if r_north_g:
        r_north_g.location = (-48.18, -109.25, 4.85)
        r_north_g.dimensions = (6.3, 0.04, 0.8)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # =========================================================================
    # 4. BACK ELEVATOR (Lift) - Back East Corner (X = -43.8, Y = -106.3)
    # =========================================================================
    lift_cx, lift_cy = -43.80, -106.30
    lift_w, lift_d = 2.00, 2.00
    lift_h = 8.40  # from 0.40 to 8.80

    # Glass Shaft Frame
    create_box("Lift_Shaft_Glass", (lift_cx, lift_cy, 0.40 + lift_h / 2.0), (lift_w - 0.1, lift_d - 0.1, lift_h), m_glass, ca)
    # Corner posts (dark metal)
    for cpx in [lift_cx - lift_w / 2.0, lift_cx + lift_w / 2.0]:
        for cpy in [lift_cy - lift_d / 2.0, lift_cy + lift_d / 2.0]:
            create_box(f"Lift_Post_{cpx:.1f}_{cpy:.1f}-col", (cpx, cpy, 0.40 + lift_h / 2.0), (0.12, 0.12, lift_h), m_metal_dark, ca)

    # Floor 1 Doors & Frame (Facing South towards Walkway/Lobby)
    create_box("Lift_F1_DoorFrame-col", (lift_cx, lift_cy - lift_d / 2.0 - 0.05, 0.40 + 1.25), (1.4, 0.10, 2.5), m_metal_dark, ca)
    create_box("Lift_F1_Doors", (lift_cx, lift_cy - lift_d / 2.0, 0.40 + 1.20), (1.1, 0.04, 2.3), m_metal_silver, ca)
    create_box("Lift_F1_CallButton", (lift_cx + 0.85, lift_cy - lift_d / 2.0 - 0.05, 0.40 + 1.20), (0.12, 0.04, 0.25), m_brass, ca)
    create_box("Lift_F1_Indicator", (lift_cx, lift_cy - lift_d / 2.0 - 0.06, 0.40 + 2.55), (0.40, 0.03, 0.15), m_screen, ca)

    # Floor 2 Doors & Frame (Facing South towards Walkway)
    create_box("Lift_F2_DoorFrame-col", (lift_cx, lift_cy - lift_d / 2.0 - 0.05, 4.40 + 1.25), (1.4, 0.10, 2.5), m_metal_dark, ca)
    create_box("Lift_F2_Doors", (lift_cx, lift_cy - lift_d / 2.0, 4.40 + 1.20), (1.1, 0.04, 2.3), m_metal_silver, ca)
    create_box("Lift_F2_CallButton", (lift_cx + 0.85, lift_cy - lift_d / 2.0 - 0.05, 4.40 + 1.20), (0.12, 0.04, 0.25), m_brass, ca)
    create_box("Lift_F2_Indicator", (lift_cx, lift_cy - lift_d / 2.0 - 0.06, 4.40 + 2.55), (0.40, 0.03, 0.15), m_screen, ca)

    # Cabin inside shaft
    create_box("Lift_Cabin_Floor-col", (lift_cx, lift_cy, 0.40 + 0.05), (1.7, 1.7, 0.10), m_tile_floor, ca)
    create_box("Lift_Cabin_Ceiling-col", (lift_cx, lift_cy, 0.40 + 2.45), (1.7, 1.7, 0.10), m_metal_silver, ca)

    # =========================================================================
    # 5. PERPUSTAKAAN (Library Section - West Forward Wing)
    # =========================================================================
    # Bounds: X in [-68.8, -61.5], Y in [-124.5, -115.5]
    # West Wall Bookshelves (along X = -68.4)
    for i, by in enumerate([-123.5, -121.2, -118.9]):
        create_box(f"Perpus_Shelf_W_{i}-col", (-68.4, by, 0.40 + 1.5), (0.50, 1.90, 3.0), m_wood_dark, ca)
        # Shelves with colorful books
        for tier in range(4):
            tz = 0.40 + 0.4 + tier * 0.7
            create_box(f"Perpus_BookRow_W_{i}_{tier}", (-68.2, by, tz), (0.28, 1.70, 0.35), [m_book_red, m_book_blue, m_book_green][tier % 3], ca)

    # East Wall Bookshelves (along X = -61.6)
    for i, by in enumerate([-123.0, -120.5]):
        create_box(f"Perpus_Shelf_E_{i}-col", (-61.6, by, 0.40 + 1.5), (0.50, 2.00, 3.0), m_wood_dark, ca)
        for tier in range(4):
            tz = 0.40 + 0.4 + tier * 0.7
            create_box(f"Perpus_BookRow_E_{i}_{tier}", (-61.8, by, tz), (0.28, 1.80, 0.35), [m_book_blue, m_book_green, m_book_red][tier % 3], ca)

    # Long Study & Reading Table (in center of library: X = -64.8, Y = -120.5)
    create_box("Perpus_Study_Table-col", (-64.8, -120.5, 0.40 + 0.40), (1.4, 3.2, 0.78), m_wood_light, ca)
    create_box("Perpus_Study_TableTop", (-64.8, -120.5, 0.40 + 0.80), (1.5, 3.3, 0.05), m_wood_desk, ca)
    # Reading lamps on study table
    for ly in [-121.3, -119.7]:
        create_box(f"Perpus_TableLamp_{ly:.1f}", (-64.8, ly, 0.40 + 1.05), (0.25, 0.25, 0.45), m_brass, ca)

    # Study Chairs around table
    for cy in [-121.5, -120.5, -119.5]:
        # West chairs
        create_box(f"Perpus_Chair_W_{cy:.1f}-col", (-65.8, cy, 0.40 + 0.42), (0.50, 0.50, 0.85), m_cushion_blue, ca)
        # East chairs
        create_box(f"Perpus_Chair_E_{cy:.1f}-col", (-63.8, cy, 0.40 + 0.42), (0.50, 0.50, 0.85), m_cushion_blue, ca)

    # Circulation Desk (near library door: X = -64.0, Y = -116.8)
    create_box("Perpus_Desk_Front-col", (-64.0, -116.8, 0.40 + 0.52), (1.8, 0.75, 1.05), m_wood_dark, ca)
    create_box("Perpus_Desk_PC", (-63.7, -116.8, 0.40 + 1.25), (0.45, 0.15, 0.35), m_screen, ca)
    create_box("Perpus_Librarian_Chair-col", (-64.0, -117.5, 0.40 + 0.45), (0.5, 0.5, 0.9), m_cushion_black, ca)

    # =========================================================================
    # 6. TOILET / RESTROOM SECTION (West Rear Wing)
    # =========================================================================
    # Bounds: X in [-68.8, -60.0], Y in [-114.5, -106.0]
    # Vanity Washbasin Counter (along North wall: Y = -106.3, X in [-65.0, -61.0])
    create_box("Toilet_Vanity_Counter-col", (-63.0, -106.3, 0.40 + 0.42), (3.6, 0.75, 0.85), m_porcelain, ca)
    # 2 recessed washbasins
    for bx in [-64.0, -62.0]:
        create_box(f"Toilet_Sink_{bx:.1f}", (bx, -106.3, 0.40 + 0.86), (0.6, 0.5, 0.05), m_tile_wc, ca)
        create_box(f"Toilet_Faucet_{bx:.1f}", (bx, -106.05, 0.40 + 1.05), (0.08, 0.15, 0.25), m_metal_silver, ca)
    # Large Vanity Mirror on wall
    create_box("Toilet_Mirror", (-63.0, -105.95, 0.40 + 1.80), (3.4, 0.04, 1.2), m_glass, ca)

    # Private Toilet Cubicles (along West wall: X in [-68.5, -65.5])
    # Stall 1: Y in [-106.2, -108.2]
    create_box("Toilet_Stall1_Partition-col", (-67.0, -108.2, 0.40 + 1.1), (2.8, 0.08, 2.2), m_wall_white, ca)
    create_box("Toilet_Stall1_Door-col", (-65.6, -107.2, 0.40 + 1.0), (0.08, 0.9, 2.0), m_wood_light, ca)
    create_box("Toilet_Bowl_1-col", (-68.0, -107.2, 0.40 + 0.25), (0.50, 0.65, 0.50), m_porcelain, ca)
    create_box("Toilet_Tank_1", (-68.25, -107.2, 0.40 + 0.65), (0.25, 0.55, 0.45), m_porcelain, ca)

    # Stall 2: Y in [-108.3, -110.3]
    create_box("Toilet_Stall2_Partition-col", (-67.0, -110.3, 0.40 + 1.1), (2.8, 0.08, 2.2), m_wall_white, ca)
    create_box("Toilet_Stall2_Door-col", (-65.6, -109.3, 0.40 + 1.0), (0.08, 0.9, 2.0), m_wood_light, ca)
    create_box("Toilet_Bowl_2-col", (-68.0, -109.3, 0.40 + 0.25), (0.50, 0.65, 0.50), m_porcelain, ca)
    create_box("Toilet_Tank_2", (-68.25, -109.3, 0.40 + 0.65), (0.25, 0.55, 0.45), m_porcelain, ca)

    # Urinals (along South wall: Y = -114.0)
    for ux in [-64.5, -63.0]:
        create_box(f"Toilet_Urinal_{ux:.1f}-col", (ux, -114.0, 0.40 + 0.75), (0.40, 0.35, 0.75), m_porcelain, ca)
        create_box(f"Toilet_Urinal_Divider_{ux:.1f}", (ux + 0.5, -114.0, 0.40 + 0.90), (0.05, 0.50, 1.10), m_wall_white, ca)

    # =========================================================================
    # 7. RUANG KELAS 101 (Classroom Section - East Forward Wing)
    # =========================================================================
    # Bounds: X in [-34.8, -27.5], Y in [-124.5, -115.5]
    # Teaching Front along North wall (Y = -115.5)
    # Large Magnetic Whiteboard
    create_box("Kelas_Whiteboard", (-31.0, -115.40, 0.40 + 1.85), (3.60, 0.05, 1.40), m_whiteboard, ca)
    create_box("Kelas_Whiteboard_Frame", (-31.0, -115.38, 0.40 + 1.85), (3.70, 0.03, 1.50), m_metal_silver, ca)
    create_box("Kelas_Marker_Tray", (-31.0, -115.35, 0.40 + 1.12), (3.40, 0.12, 0.04), m_metal_silver, ca)

    # Lecturer Podium & Desk
    create_box("Kelas_Podium_Desk-col", (-31.0, -117.0, 0.40 + 0.40), (1.60, 0.75, 0.80), m_wood_dark, ca)
    create_box("Kelas_Podium_Laptop", (-30.8, -117.0, 0.40 + 0.95), (0.35, 0.25, 0.20), m_metal_dark, ca)
    create_box("Kelas_Teacher_Chair-col", (-31.0, -116.3, 0.40 + 0.45), (0.50, 0.50, 0.90), m_cushion_black, ca)

    # Student Desks & Chairs (3 Rows of double desks)
    for row, dy in enumerate([-119.0, -121.0, -123.0]):
        for col, dx in enumerate([-32.8, -29.2]):
            # Student Desk (Seats 2)
            create_box(f"Kelas_Desk_R{row}_C{col}-col", (dx, dy, 0.40 + 0.38), (1.40, 0.65, 0.75), m_wood_light, ca)
            # Desk frame / legs
            create_box(f"Kelas_DeskLegs_R{row}_C{col}", (dx, dy, 0.40 + 0.35), (1.35, 0.60, 0.70), m_metal_dark, ca)
            # 2 Student Chairs behind each desk
            for sc in [-0.35, 0.35]:
                create_box(f"Kelas_Chair_R{row}_C{col}_{sc:.2f}-col", (dx + sc, dy - 0.60, 0.40 + 0.40), (0.42, 0.42, 0.80), m_wood_dark, ca)
                # Notebook on desk
                create_box(f"Kelas_Book_R{row}_C{col}_{sc:.2f}", (dx + sc, dy, 0.40 + 0.77), (0.22, 0.28, 0.02), [m_book_red, m_book_blue][(row + col) % 2], ca)

    # Classroom Wall Clock
    create_cyl("Kelas_WallClock", (-27.6, -117.0, 0.40 + 2.80), 0.22, 0.05, m_metal_silver, rot=(0, math.pi / 2.0, 0), collection=ca)

    # =========================================================================
    # 8. RUANG MEJA DOSEN (Faculty Office - East Rear Wing)
    # =========================================================================
    # Bounds: X in [-41.5, -27.5], Y in [-114.5, -106.0]
    # 4 Executive Lecturer Workstations (Meja Dosen)
    workstations = [
        ("Dosen1", -38.0, -107.5, "Dr. Ir. Budi S., M.Kom"),
        ("Dosen2", -31.5, -107.5, "Prof. Dr. Hendra, Ph.D"),
        ("Dosen3", -38.0, -112.5, "Siti Rahma, S.T., M.T."),
        ("Dosen4", -31.5, -112.5, "Agus Prasetyo, M.Cs")
    ]

    for name, dx, dy, lecturer_title in workstations:
        # Large Executive Desk with side pedestal
        create_box(f"Dosen_Desk_{name}-col", (dx, dy, 0.40 + 0.40), (1.80, 0.90, 0.78), m_wood_dark, ca)
        create_box(f"Dosen_DeskTop_{name}", (dx, dy, 0.40 + 0.80), (1.85, 0.95, 0.05), m_wood_desk, ca)
        create_box(f"Dosen_Pedestal_{name}-col", (dx + 0.65, dy, 0.40 + 0.35), (0.45, 0.85, 0.68), m_wood_dark, ca)
        create_box(f"Dosen_Modesty_{name}", (dx, dy + 0.40, 0.40 + 0.35), (1.75, 0.05, 0.65), m_wood_dark, ca)

        # High-back Executive Swivel Chair (behind desk)
        chair_y = dy - 0.65
        create_box(f"Dosen_Chair_{name}-col", (dx, chair_y, 0.40 + 0.55), (0.60, 0.60, 1.10), m_cushion_black, ca)

        # Student Consultation Chair (in front of desk)
        consult_y = dy + 0.75
        create_box(f"Dosen_GuestChair_{name}-col", (dx, consult_y, 0.40 + 0.42), (0.50, 0.50, 0.85), m_cushion_blue, ca)

        # Laptop on desk
        create_box(f"Dosen_Laptop_{name}", (dx - 0.15, dy, 0.40 + 0.92), (0.35, 0.25, 0.18), m_metal_dark, ca)

        # Desk Nameplate (Akrilik / Kuningan)
        create_box(f"Dosen_Nameplate_{name}", (dx + 0.55, dy + 0.30, 0.40 + 0.86), (0.28, 0.08, 0.08), m_brass, ca)

        # Stack of Skripsi / Theses with colorful covers! (Iconic Indonesian campus touch)
        create_box(f"Dosen_Skripsi_{name}", (dx - 0.60, dy, 0.40 + 0.90), (0.24, 0.32, 0.15), m_book_blue, ca)

    # Filing Cabinets along East Wall (X = -27.6)
    for i, fy in enumerate([-107.5, -109.5, -111.5]):
        create_box(f"Dosen_Cabinet_{i}-col", (-27.6, fy, 0.40 + 1.0), (0.55, 1.10, 2.0), m_metal_silver, ca)

    # Classic Indonesian Campus Water Dispenser (Dispenser Galon)
    create_box("Dosen_Dispenser_Stand-col", (-40.8, -106.8, 0.40 + 0.45), (0.45, 0.45, 0.90), m_wall_white, ca)
    create_cyl("Dosen_Dispenser_Galon", (-40.8, -106.8, 0.40 + 1.15), 0.18, 0.45, m_glass, rot=(0, 0, 0), collection=ca)

    # Meeting / Faculty Whiteboard on partition wall
    create_box("Dosen_Whiteboard", (-41.35, -108.5, 0.40 + 1.80), (0.05, 2.20, 1.20), m_whiteboard, ca)

    print("Successfully built all campus interior zones!")

if __name__ == "__main__":
    build_interior()
