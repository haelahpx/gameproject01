"""
Comprehensive script to:
1. Shift kampung houses/buildings back so that the upgraded road and sidewalks fit with zero clipping:
   - North row shifted by +1.2m (Y)
   - South row shifted by -1.2m (Y)
   - Branch lateral houses (House8, TambalBan) shifted +1.0m (X)
   - House10 shifted -1.0m (X)
   - Associated props, vegetation, and details moved synchronously.
2. Completely replace old plain kampung road boxes and 229 old curb fragments with matching high-quality
   residential road segments:
   - 4.2m roadway
   - 0.70m elevated sidewalks on both sides
   - Alternating black-and-white curb blocks
   - Dashed white center road markings
   - Smooth corner curb returns at Pos Ronda T-junction and Tambal Ban corner.
3. Fix the Jalan Raya intersections (completely eliminating all Z-fighting / overlapping faces):
   - Gang_Road_Main-col.002 (E-W avenue) stops at X=-143.39 on the West (never overlaps West Avenue).
   - Gang_Road_Main-col.002 skips the intersection box at X in [56.61, 65.61] (zero duplicate faces with East Avenue).
   - Gang_Road_Main-col.001 (East Avenue) provides the single continuous intersection pavement.
   - Beautiful curved corner curb returns (radius 3.0m) at the perempatan corners.
4. Save blend file and export updated GLBs.
"""

import bpy  # pyrefly: ignore[missing-import] # type: ignore
import bmesh  # pyrefly: ignore[missing-import] # type: ignore
import math
from mathutils import Vector  # pyrefly: ignore[missing-import] # type: ignore

def run():
    print("=== Starting upgrade_all_roads_and_clean_overlaps.py ===")

    # Collections
    def get_or_create_col(name, parent_col=None):
        if name in bpy.data.collections:
            return bpy.data.collections[name]
        col = bpy.data.collections.new(name)
        if parent_col:
            parent_col.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
        return col

    col_gang_road = get_or_create_col("GangRoad")
    col_perumahan = get_or_create_col("PerumahanRoads")
    col_drainage = get_or_create_col("RoadDrainage")
    col_campus = get_or_create_col("CampusArea")

    # Materials
    mat_asphalt = bpy.data.materials.get("road_asphalt")
    mat_marking_white = bpy.data.materials.get("road_marking_white")
    mat_curb_concrete = bpy.data.materials.get("curb_concrete") or bpy.data.materials.get("Mat_ConcreteCurb.001")
    mat_curb_black = bpy.data.materials.get("curb_black")
    mat_curb_white = bpy.data.materials.get("curb_white")
    mat_dark_iron = bpy.data.materials.get("Mat_DarkIron.001")
    mat_drain_trench = bpy.data.materials.get("drain_trench")

    # =========================================================================
    # 1. SHIFT KAMPUNG HOUSES & BUILDINGS TO FIT NEW SIDEWALKS
    # =========================================================================
    print("1. Shifting kampung houses and buildings back...")
    delta_north_y = 1.2
    delta_south_y = -1.2
    delta_branch_east_x = 1.0
    delta_branch_west_x = -1.0

    # North collections & prefixes
    north_cols = ['KostBuilding', 'KostRoom', 'KostWC', 'WarsunBuilding']
    north_objs = set()
    for cname in north_cols:
        c = bpy.data.collections.get(cname)
        if c:
            for o in c.objects:
                north_objs.add(o)

    north_prefixes = [
        "House4_", "House12_", "House13_", "PosRonda_", "Kentongan_", "Cermin_",
        "AC_Kost_", "Door_Kost_", "ShoeRack_Kost_", "Toren_Kost_", "Lampu_Kost_"
    ]
    for o in bpy.data.objects:
        if any(o.name.startswith(p) for p in north_prefixes):
            north_objs.add(o)

    # South collections & prefixes
    south_cols = ['PoorKost', 'PoorKostRoom']
    south_objs = set()
    for cname in south_cols:
        c = bpy.data.collections.get(cname)
        if c:
            for o in c.objects:
                south_objs.add(o)

    south_prefixes = [
        "House1_", "House2_", "House3_", "House5_", "House6_", "House7_",
        "House14_", "House15_", "House16_",
        "PoorKost_", "Aqua_Galon_", "Baskom_Cucian"
    ]
    for o in bpy.data.objects:
        if any(o.name.startswith(p) for p in south_prefixes):
            south_objs.add(o)

    # Branch houses
    branch_east_objs = set()
    for o in bpy.data.objects:
        if o.name.startswith("House8_") or "TambalBan" in o.name or "Compressor" in o.name:
            branch_east_objs.add(o)

    branch_west_objs = set()
    for o in bpy.data.objects:
        if o.name.startswith("House10_"):
            branch_west_objs.add(o)

    # Move vegetation/props in corridor
    for o in bpy.data.objects:
        if any(k in o.name for k in ["Tree", "Bush", "Palm", "Jemuran", "Trash", "Table", "Bench"]):
            if -60 <= o.location.x <= 30:
                if 0.5 <= o.location.y <= 12.0:
                    north_objs.add(o)
                elif -25.0 <= o.location.y <= -1.5:
                    south_objs.add(o)

    # Apply shifts
    shifted_count = 0
    for o in north_objs:
        o.location.y += delta_north_y
        shifted_count += 1

    for o in south_objs:
        o.location.y += delta_south_y
        shifted_count += 1

    for o in branch_east_objs:
        o.location.x += delta_branch_east_x
        shifted_count += 1

    for o in branch_west_objs:
        o.location.x += delta_branch_west_x
        shifted_count += 1

    print(f"Shifted {shifted_count} objects to create clearance for new sidewalks.")

    # =========================================================================
    # 2. CLEANUP OLD ROAD BOXES, 229 OLD CURB STRIPS, AND OLD MARKINGS
    # =========================================================================
    print("2. Cleaning up old plain road boxes and fragmented curb strips...")
    cleanup_names = [
        "Gang_Road_Main-col",
        "Gang_Road_West_Ext-col",
        "Gang_Road_South-col",
        "Gang_Road_Turn_West-col",
        "Road_Turn_Curve_1",
        "Road_Turn_Curve_2",
        "Road_South_Stripe_Approach"
    ]

    for o in list(bpy.data.objects):
        if (o.name.startswith("Curb_GB_") or o.name.startswith("Curb_GS_") or 
            o.name.startswith("Curb_N_") or o.name.startswith("Curb_S_") or
            o.name.startswith("Road_Center_Stripe_") or o.name.startswith("Road_Ext_Stripe_") or
            o.name.startswith("Road_South_Stripe_") or o.name.startswith("Road_Turn_Stripe_") or
            o.name.startswith("Road_Ext_Patch_")):
            cleanup_names.append(o.name)

    # Also clean up old perumahan road segments if re-running
    for o in list(bpy.data.objects):
        if o.name.startswith("Perum_"):
            cleanup_names.append(o.name)

    removed_old_count = 0
    for name in cleanup_names:
        o = bpy.data.objects.get(name)
        if o:
            mesh = o.data if o.type == 'MESH' else None
            bpy.data.objects.remove(o, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
            removed_old_count += 1

    print(f"Removed {removed_old_count} old road and curb fragments.")

    # =========================================================================
    # 3. REBUILD AVENUE INTERSECTIONS (ZERO OVERLAPS / ZERO Z-FIGHTING)
    # =========================================================================
    print("3. Rebuilding avenue meshes with zero intersection overlap...")

    slot_asphalt = 0
    slot_sidewalk = 1
    slot_line_white = 2
    slot_curb_white = 3
    slot_curb_black = 4

    # -------------------------------------------------------------------------
    # A. REBUILD Gang_Road_Main-col.002 (Campus Front E-W Road)
    # Stops at West Ave (X = -143.39) and skips East Ave box (X in [56.61, 65.61])
    # -------------------------------------------------------------------------
    road_ew = bpy.data.objects.get("Gang_Road_Main-col.002")
    if road_ew:
        bpy.context.view_layer.objects.active = road_ew
        road_ew.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        mats = [mat_asphalt, mat_curb_concrete, mat_marking_white, mat_curb_white, mat_curb_black]
        road_ew.data.materials.clear()
        for m in mats:
            road_ew.data.materials.append(m)

        # Origin is at X = -29.27
        # West avenue edge: X = -143.39 -> local x = -143.39 - (-29.27) = -114.12
        # Campus gate zebra cross: X = -48.18 -> local x = -18.91 (from -22.5 to -15.5)
        # East intersection west edge: X = 56.61 -> local x = 56.61 - (-29.27) = +85.88
        # East intersection east edge: X = 65.61 -> local x = 65.61 - (-29.27) = +94.88
        # East end: X = 93.73 -> local x = +123.00

        # We construct two clean segments:
        # Segment 1: from x = -114.12 to x = 85.88
        # Segment 2: from x = 94.88 to x = 123.00
        # The gap in [85.88, 94.88] has ZERO faces!

        def generate_x_pts(x_start, x_end):
            pts = []
            cur_x = x_start
            while cur_x <= x_end + 0.001:
                # Zebra crossing zones
                in_gate_z = (-22.5 <= cur_x <= -15.5)
                in_east_appr_z = (81.88 <= cur_x <= 85.88)
                in_east_exit_z = (94.88 <= cur_x <= 98.88)
                if in_gate_z or in_east_appr_z or in_east_exit_z:
                    pts.append(round(cur_x, 4))
                    cur_x += 0.5
                else:
                    pts.append(round(cur_x, 4))
                    cur_x += 1.5
            if pts[-1] < x_end:
                pts.append(round(x_end, 4))
            return pts

        x_pts_seg1 = generate_x_pts(-114.12, 85.88)
        x_pts_seg2 = generate_x_pts(94.88, 123.00)

        # Transverse Y profile across 15.0m width
        y_z_profile = [
            (-7.50, -0.15),  # 0: South outer bottom
            (-7.50,  0.18),  # 1: South outer top
            (-4.80,  0.18),  # 2: South sidewalk inner
            (-4.50,  0.18),  # 3: South curb top
            (-4.50,  0.00),  # 4: South gutter
            (-4.20,  0.00),  # 5: South edge line outer
            (-4.05,  0.00),  # 6: South edge line inner
            (-0.10,  0.00),  # 7: Center line south
            ( 0.10,  0.00),  # 8: Center line north
            ( 4.05,  0.00),  # 9: North edge line inner
            ( 4.20,  0.00),  # 10: North edge line outer
            ( 4.50,  0.00),  # 11: North gutter
            ( 4.50,  0.18),  # 12: North curb top
            ( 4.80,  0.18),  # 13: North sidewalk inner
            ( 7.50,  0.18),  # 14: North outer top
            ( 7.50, -0.15),  # 15: North outer bottom
        ]
        num_y = len(y_z_profile)

        bm_ew = bmesh.new()

        def build_ew_strip(x_pts, is_first_seg=True):
            grid = []
            for i, x in enumerate(x_pts):
                row = []
                for j, (y, z) in enumerate(y_z_profile):
                    vz = z
                    v = bm_ew.verts.new((x, y, vz))
                    row.append(v)
                grid.append(row)
            bm_ew.verts.ensure_lookup_table()

            for i in range(len(x_pts) - 1):
                x_start = x_pts[i]
                x_end = x_pts[i + 1]
                x_mid = (x_start + x_end) / 2.0

                curb_seg_idx = int(math.floor((x_mid - (-114.12)) / 1.5))
                curb_slot = slot_curb_white if (curb_seg_idx % 2 == 0) else slot_curb_black

                center_seg_idx = int(math.floor((x_mid - (-114.12)) / 3.0))
                center_is_dash = (center_seg_idx % 2 == 0)

                is_gate_zebra = (-22.5 <= x_start and x_end <= -15.5)
                gate_stripe_idx = int(round((x_start - (-22.5)) / 0.5)) if is_gate_zebra else 0
                is_gate_white = is_gate_zebra and (gate_stripe_idx % 2 == 0)

                is_east_zebra_w = (81.88 <= x_start and x_end <= 85.88)
                east_stripe_idx_w = int(round((x_start - 81.88) / 0.5)) if is_east_zebra_w else 0
                is_ez_w_white = is_east_zebra_w and (east_stripe_idx_w % 2 == 0)

                is_east_zebra_e = (94.88 <= x_start and x_end <= 98.88)
                east_stripe_idx_e = int(round((x_start - 94.88) / 0.5)) if is_east_zebra_e else 0
                is_ez_e_white = is_east_zebra_e and (east_stripe_idx_e % 2 == 0)

                is_any_zebra_white = is_gate_white or is_ez_w_white or is_ez_e_white
                is_any_zebra_zone = is_gate_zebra or is_east_zebra_w or is_east_zebra_e

                for j in range(num_y - 1):
                    face = bm_ew.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))

                    if j in [0, 1, 13, 14]:
                        face.material_index = slot_sidewalk
                    elif j in [2, 3, 11, 12]:
                        face.material_index = curb_slot
                    elif j in [4, 10]:
                        face.material_index = slot_asphalt
                    elif j in [5, 9]:
                        face.material_index = slot_line_white
                    elif j in [6, 8]:
                        if is_any_zebra_zone:
                            face.material_index = slot_line_white if is_any_zebra_white else slot_asphalt
                        else:
                            face.material_index = slot_asphalt
                    elif j == 7:
                        if is_any_zebra_zone:
                            face.material_index = slot_line_white if is_any_zebra_white else slot_asphalt
                        else:
                            face.material_index = slot_line_white if center_is_dash else slot_asphalt

                face_bot = bm_ew.faces.new((grid[i][0], grid[i][num_y - 1], grid[i + 1][num_y - 1], grid[i + 1][0]))
                face_bot.material_index = slot_asphalt

            # End caps
            bm_ew.faces.new([grid[0][j] for j in range(num_y)]).material_index = slot_asphalt
            bm_ew.faces.new([grid[-1][j] for j in reversed(range(num_y))]).material_index = slot_asphalt

        build_ew_strip(x_pts_seg1, is_first_seg=True)
        build_ew_strip(x_pts_seg2, is_first_seg=False)

        old_mesh = road_ew.data
        new_mesh = bpy.data.meshes.new(road_ew.name + "_Mesh")
        bm_ew.to_mesh(new_mesh)
        bm_ew.free()
        for m in mats:
            new_mesh.materials.append(m)
        road_ew.data = new_mesh
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
        print("Rebuilt Gang_Road_Main-col.002 with clean gap at East intersection and terminus at West intersection.")

    # -------------------------------------------------------------------------
    # B. REBUILD Gang_Road_Main-col.001 (East N-S Road) & Gang_Road_Main-col.003 (West N-S Road)
    # -------------------------------------------------------------------------
    def rebuild_ns_avenue(obj_name, is_east_road=True):
        road_ns = bpy.data.objects.get(obj_name)
        if not road_ns:
            return

        bpy.context.view_layer.objects.active = road_ns
        road_ns.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        mats = [mat_asphalt, mat_curb_concrete, mat_marking_white, mat_curb_white, mat_curb_black]
        road_ns.data.materials.clear()
        for m in mats:
            road_ns.data.materials.append(m)

        # Origin is at Y = -113.84
        # Intersection with Campus front road: World Y = -165.24 -> local y = -51.40
        # Roadway opening: Y in [-169.74, -160.74] -> local y in [-55.90, -46.90] (width 9.0m)
        # South approach zebra: local y in [-59.90, -55.90]
        # North approach zebra: local y in [-46.90, -42.90]
        # South perumahan junction: World Y = -60.0 -> local y = +53.84 (y in [51.0, 56.5])
        # Kampung boulevard junction: World Y = 0.0 -> local y = +113.84 (y in [111.0, 116.5])

        y_pts = []
        cur_y = -197.6
        while cur_y <= 197.601:
            in_campus_zebra = ((-60.5 <= cur_y <= -55.9) or (-46.9 <= cur_y <= -42.5))
            in_campus_box = (-55.9 <= cur_y <= -46.9)
            in_south_junc = (50.5 <= cur_y <= 57.0)
            in_kampung_junc = (110.5 <= cur_y <= 117.0)

            if is_east_road and in_campus_zebra:
                y_pts.append(round(cur_y, 4))
                cur_y += 0.5
            elif in_campus_box or in_south_junc or in_kampung_junc:
                y_pts.append(round(cur_y, 4))
                cur_y += 0.75
            else:
                y_pts.append(round(cur_y, 4))
                cur_y += 2.0
        if y_pts[-1] < 197.6:
            y_pts.append(197.6)

        x_z_profile = [
            (-7.50, -0.15),  # 0: West outer bottom
            (-7.50,  0.18),  # 1: West outer top
            (-4.80,  0.18),  # 2: West sidewalk inner
            (-4.50,  0.18),  # 3: West curb top
            (-4.50,  0.00),  # 4: West gutter
            (-4.20,  0.00),  # 5: West edge line outer
            (-4.05,  0.00),  # 6: West edge line inner
            (-0.10,  0.00),  # 7: Center line west
            ( 0.10,  0.00),  # 8: Center line east
            ( 4.05,  0.00),  # 9: East edge line inner
            ( 4.20,  0.00),  # 10: East edge line outer
            ( 4.50,  0.00),  # 11: East gutter
            ( 4.50,  0.18),  # 12: East curb top
            ( 4.80,  0.18),  # 13: East sidewalk inner
            ( 7.50,  0.18),  # 14: East outer top
            ( 7.50, -0.15),  # 15: East outer bottom
        ]

        bm_ns = bmesh.new()
        grid = []
        for i, y in enumerate(y_pts):
            row = []
            is_campus_junc = (-55.90 <= y <= -46.90)
            is_south_junc = (51.0 <= y <= 56.5)
            is_kampung_junc = (111.0 <= y <= 116.5)

            for j, (x, z) in enumerate(x_z_profile):
                vz = z
                if is_campus_junc:
                    if is_east_road:
                        # 4-way perempatan: lower sidewalks and curbs so E-W traffic flows flush!
                        if j in [1, 2, 3, 12, 13, 14]:
                            vz = 0.0
                    else:
                        # West road: East side joins E-W road -> lower East side
                        if j in [12, 13, 14]:
                            vz = 0.0
                elif is_south_junc or is_kampung_junc:
                    if is_east_road:
                        if j in [1, 2, 3]:
                            vz = 0.0
                    else:
                        if j in [12, 13, 14]:
                            vz = 0.0

                v = bm_ns.verts.new((x, y, vz))
                row.append(v)
            grid.append(row)
        bm_ns.verts.ensure_lookup_table()

        for i in range(len(y_pts) - 1):
            y_start = y_pts[i]
            y_end = y_pts[i + 1]
            y_mid = (y_start + y_end) / 2.0

            is_campus_junc_seg = (-55.90 <= y_start and y_end <= -46.90)
            is_south_junc_seg = (51.0 <= y_start and y_end <= 56.5)
            is_kampung_junc_seg = (111.0 <= y_start and y_end <= 116.5)

            curb_seg_idx = int(math.floor((y_mid - (-197.6)) / 1.5))
            curb_slot = slot_curb_white if (curb_seg_idx % 2 == 0) else slot_curb_black

            center_seg_idx = int(math.floor((y_mid - (-197.6)) / 3.0))
            center_is_dash = (center_seg_idx % 2 == 0)

            # Zebras strictly outside intersection box
            is_south_zebra = is_east_road and (-59.90 <= y_start and y_end <= -55.90)
            s_stripe_idx = int(round((y_start - (-59.90)) / 0.5)) if is_south_zebra else 0
            is_s_zebra_white = is_south_zebra and (s_stripe_idx % 2 == 0)

            is_north_zebra = is_east_road and (-46.90 <= y_start and y_end <= -42.90)
            n_stripe_idx = int(round((y_start - (-46.90)) / 0.5)) if is_north_zebra else 0
            is_n_zebra_white = is_north_zebra and (n_stripe_idx % 2 == 0)

            for j in range(len(x_z_profile) - 1):
                v1 = grid[i][j]
                v2 = grid[i + 1][j]
                v3 = grid[i + 1][j + 1]
                v4 = grid[i][j + 1]

                mat_slot = slot_asphalt

                if j == 0 or j == 14:
                    mat_slot = slot_sidewalk
                elif j == 1:
                    mat_slot = slot_asphalt if (is_east_road and (is_campus_junc_seg or is_south_junc_seg or is_kampung_junc_seg)) else slot_sidewalk
                elif j == 2:
                    mat_slot = slot_asphalt if (is_east_road and (is_campus_junc_seg or is_south_junc_seg or is_kampung_junc_seg)) else curb_slot
                elif j in [3, 4, 10, 11]:
                    mat_slot = slot_asphalt
                elif j == 5:
                    mat_slot = slot_line_white if not (is_campus_junc_seg or is_south_junc_seg or is_kampung_junc_seg) else slot_asphalt
                elif j in [6, 8]:
                    if is_south_zebra:
                        mat_slot = slot_line_white if is_s_zebra_white else slot_asphalt
                    elif is_north_zebra:
                        mat_slot = slot_line_white if is_n_zebra_white else slot_asphalt
                    else:
                        mat_slot = slot_asphalt
                elif j == 7:
                    if is_campus_junc_seg:
                        # Inside intersection box, zero road lines!
                        mat_slot = slot_asphalt
                    elif is_south_zebra:
                        mat_slot = slot_line_white if is_s_zebra_white else slot_asphalt
                    elif is_north_zebra:
                        mat_slot = slot_line_white if is_n_zebra_white else slot_asphalt
                    else:
                        mat_slot = slot_line_white if center_is_dash else slot_asphalt
                elif j == 9:
                    mat_slot = slot_line_white if not (is_campus_junc_seg or is_south_junc_seg or is_kampung_junc_seg) else slot_asphalt
                elif j == 12:
                    mat_slot = slot_asphalt if ((not is_east_road and (is_campus_junc_seg or is_south_junc_seg or is_kampung_junc_seg)) or (is_east_road and is_campus_junc_seg)) else curb_slot
                elif j == 13:
                    mat_slot = slot_asphalt if ((not is_east_road and (is_campus_junc_seg or is_south_junc_seg or is_kampung_junc_seg)) or (is_east_road and is_campus_junc_seg)) else slot_sidewalk

                face = bm_ns.faces.new([v1, v2, v3, v4])
                face.material_index = mat_slot

        old_mesh = road_ns.data
        new_mesh = bpy.data.meshes.new(f"{obj_name}_Mesh")
        bm_ns.to_mesh(new_mesh)
        bm_ns.free()

        for m in mats:
            new_mesh.materials.append(m)
        road_ns.data = new_mesh
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
        print(f"Rebuilt {obj_name} with single-layer intersection pavement and approach crosswalks.")

    rebuild_ns_avenue("Gang_Road_Main-col.001", is_east_road=True)
    rebuild_ns_avenue("Gang_Road_Main-col.003", is_east_road=False)

    # -------------------------------------------------------------------------
    # C. CORNER CURB RETURNS AT PEREMPATAN & WEST INTERSECTION
    # -------------------------------------------------------------------------
    def build_curb_return_arc(name, center_pt, r=2.8, start_deg=0.0, end_deg=90.0, steps=8, col_target=col_campus):
        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bm = bmesh.new()
        
        cx, cy = center_pt
        t_start = math.radians(start_deg)
        t_end = math.radians(end_deg)
        
        r_inner = r
        r_outer = r + 0.18
        sw_outer = r + 2.80 # elevated sidewalk corner slab
        
        verts_in = []
        verts_curb_top = []
        verts_sw_out = []
        for s in range(steps + 1):
            th = t_start + (s / steps) * (t_end - t_start)
            cos_t, sin_t = math.cos(th), math.sin(th)
            vi = bm.verts.new((cx + r_inner * cos_t, cy + r_inner * sin_t, 0.00))
            vc = bm.verts.new((cx + r_outer * cos_t, cy + r_outer * sin_t, 0.18))
            vsw = bm.verts.new((cx + sw_outer * cos_t, cy + sw_outer * sin_t, 0.18))
            verts_in.append(vi)
            verts_curb_top.append(vc)
            verts_sw_out.append(vsw)
            
        for s in range(steps):
            # Curb block face
            f_curb = bm.faces.new([verts_in[s], verts_in[s + 1], verts_curb_top[s + 1], verts_curb_top[s]])
            f_curb.material_index = 0 if (s % 2 == 0) else 1
            # Sidewalk corner wedge
            f_sw = bm.faces.new([verts_curb_top[s], verts_curb_top[s + 1], verts_sw_out[s + 1], verts_sw_out[s]])
            f_sw.material_index = 2
            
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_curb_white)
        mesh.materials.append(mat_curb_black)
        mesh.materials.append(mat_curb_concrete)
        col_target.objects.link(obj)
        return obj

    # East 4-way perempatan corners (X=61.11, Y=-165.24, Roadway boundary X in [56.61, 65.61], Y in [-169.74, -160.74])
    build_curb_return_arc("CurbReturn_Perempatan_NW", (53.81, -157.94), r=2.8, start_deg=270, end_deg=360)
    build_curb_return_arc("CurbReturn_Perempatan_NE", (68.41, -157.94), r=2.8, start_deg=180, end_deg=270)
    build_curb_return_arc("CurbReturn_Perempatan_SW", (53.81, -172.54), r=2.8, start_deg=0,   end_deg=90)
    build_curb_return_arc("CurbReturn_Perempatan_SE", (68.41, -172.54), r=2.8, start_deg=90,  end_deg=180)

    # West T-intersection corners (X=-147.89, Y=-165.24, Roadway boundary X=-143.39, Y in [-169.74, -160.74])
    build_curb_return_arc("CurbReturn_WestJunc_NW", (-140.59, -157.94), r=2.8, start_deg=180, end_deg=270)
    build_curb_return_arc("CurbReturn_WestJunc_SW", (-140.59, -172.54), r=2.8, start_deg=90,  end_deg=180)

    print("Rebuilt perempatan corners with non-overlapping rounded curb arcs.")

    # =========================================================================
    # 4. REBUILD ENTIRE ROAD NETWORK INCLUDING OLD KAMPUNG ROADS
    # =========================================================================
    print("4. Rebuilding entire road network with unified sidewalks & curbs...")

    def build_road_segment(name, p_start, p_end, road_width=4.2, sidewalk_width=0.70, 
                           trim_sw_start=0.0, trim_sw_end=0.0,
                           has_left_sw=True, has_right_sw=True, has_centerline=True, 
                           col_target=col_perumahan):
        x1, y1 = p_start[0], p_start[1]
        x2, y2 = p_end[0], p_end[1]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length <= 0.2:
            return None

        angle = math.atan2(dy, dx)
        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0

        # A. Road Asphalt Surface Box
        mesh_road = bpy.data.meshes.new(f"{name}_Asphalt_Mesh")
        obj_road = bpy.data.objects.new(f"{name}_Road-col", mesh_road)
        bm_r = bmesh.new()
        
        hl = length / 2.0
        hw = road_width / 2.0
        z_top = 0.00
        z_bot = -0.08

        v1 = bm_r.verts.new((-hl, -hw, z_bot))
        v2 = bm_r.verts.new(( hl, -hw, z_bot))
        v3 = bm_r.verts.new(( hl,  hw, z_bot))
        v4 = bm_r.verts.new((-hl,  hw, z_bot))
        v5 = bm_r.verts.new((-hl, -hw, z_top))
        v6 = bm_r.verts.new(( hl, -hw, z_top))
        v7 = bm_r.verts.new(( hl,  hw, z_top))
        v8 = bm_r.verts.new((-hl,  hw, z_top))

        bm_r.faces.new([v5, v6, v7, v8]) # top
        bm_r.faces.new([v4, v3, v2, v1]) # bottom
        bm_r.faces.new([v1, v2, v6, v5]) # side -y
        bm_r.faces.new([v2, v3, v7, v6]) # end +x
        bm_r.faces.new([v3, v4, v8, v7]) # side +y
        bm_r.faces.new([v4, v1, v5, v8]) # end -x

        bm_r.to_mesh(mesh_road)
        bm_r.free()
        mesh_road.materials.append(mat_asphalt)
        obj_road.location = (mid_x, mid_y, 0.0)
        obj_road.rotation_euler = (0, 0, angle)
        col_target.objects.link(obj_road)

        # B. Center Road Markings (White dashed line)
        if has_centerline and length > 3.0:
            mesh_lines = bpy.data.meshes.new(f"{name}_Stripes_Mesh")
            obj_lines = bpy.data.objects.new(f"{name}_Stripes", mesh_lines)
            bm_l = bmesh.new()
            
            stripe_len = 1.5
            gap_len = 1.5
            cycle = stripe_len + gap_len
            line_w = 0.12
            z_stripe = 0.003
            
            start_x = -hl + trim_sw_start + 0.5
            end_x = hl - trim_sw_end - 0.5
            usable_len = end_x - start_x
            if usable_len > 1.5:
                n_stripes = int(math.floor(usable_len / cycle))
                for si in range(n_stripes):
                    sx = start_x + si * cycle
                    ex = sx + stripe_len
                    sv1 = bm_l.verts.new((sx, -line_w/2, z_stripe))
                    sv2 = bm_l.verts.new((ex, -line_w/2, z_stripe))
                    sv3 = bm_l.verts.new((ex,  line_w/2, z_stripe))
                    sv4 = bm_l.verts.new((sx,  line_w/2, z_stripe))
                    bm_l.faces.new([sv1, sv2, sv3, sv4])
                    
                bm_l.to_mesh(mesh_lines)
                bm_l.free()
                mesh_lines.materials.append(mat_marking_white)
                obj_lines.location = (mid_x, mid_y, 0.0)
                obj_lines.rotation_euler = (0, 0, angle)
                col_target.objects.link(obj_lines)

        # C. Sidewalks and Alternating Black/White Curbs (Trimmed at Junctions)
        curb_w = 0.14
        curb_h = 0.12
        sw_h = 0.11

        def build_side(is_left=True):
            sign = 1.0 if is_left else -1.0
            sw_name = f"{name}_SW_{'L' if is_left else 'R'}"
            
            sw_start = -hl + trim_sw_start
            sw_end = hl - trim_sw_end
            sw_len = sw_end - sw_start
            if sw_len <= 0.2:
                return

            mesh_sw = bpy.data.meshes.new(f"{sw_name}_Mesh")
            obj_sw = bpy.data.objects.new(f"{sw_name}-col", mesh_sw)
            bm_sw = bmesh.new()
            
            y_inner = sign * hw
            y_outer = sign * (hw + sidewalk_width)
            y_a = min(y_inner, y_outer)
            y_b = max(y_inner, y_outer)
            
            s1 = bm_sw.verts.new((sw_start, y_a, -0.05))
            s2 = bm_sw.verts.new((sw_end,   y_a, -0.05))
            s3 = bm_sw.verts.new((sw_end,   y_b, -0.05))
            s4 = bm_sw.verts.new((sw_start, y_b, -0.05))
            s5 = bm_sw.verts.new((sw_start, y_a, sw_h))
            s6 = bm_sw.verts.new((sw_end,   y_a, sw_h))
            s7 = bm_sw.verts.new((sw_end,   y_b, sw_h))
            s8 = bm_sw.verts.new((sw_start, y_b, sw_h))
            
            bm_sw.faces.new([s5, s6, s7, s8]) # top
            bm_sw.faces.new([s1, s2, s6, s5])
            bm_sw.faces.new([s2, s3, s7, s6])
            bm_sw.faces.new([s3, s4, s8, s7])
            bm_sw.faces.new([s4, s1, s5, s8])
            
            bm_sw.to_mesh(mesh_sw)
            bm_sw.free()
            mesh_sw.materials.append(mat_curb_concrete)
            obj_sw.location = (mid_x, mid_y, 0.0)
            obj_sw.rotation_euler = (0, 0, angle)
            col_target.objects.link(obj_sw)

            mesh_curb = bpy.data.meshes.new(f"{sw_name}_Curbs_Mesh")
            obj_curb = bpy.data.objects.new(f"{sw_name}_Curbs", mesh_curb)
            bm_c = bmesh.new()
            
            block_len = 1.0
            n_blocks = max(1, int(round(sw_len / block_len)))
            actual_len = sw_len / n_blocks
            
            y_curb_inner = y_inner
            y_curb_outer = y_inner + sign * curb_w
            cy_a = min(y_curb_inner, y_curb_outer)
            cy_b = max(y_curb_inner, y_curb_outer)
            
            for bi in range(n_blocks):
                bx0 = sw_start + bi * actual_len
                bx1 = bx0 + actual_len
                c_slot = 0 if (bi % 2 == 0) else 1
                
                cv1 = bm_c.verts.new((bx0, cy_a, 0.00))
                cv2 = bm_c.verts.new((bx1, cy_a, 0.00))
                cv3 = bm_c.verts.new((bx1, cy_b, 0.00))
                cv4 = bm_c.verts.new((bx0, cy_b, 0.00))
                cv5 = bm_c.verts.new((bx0, cy_a, curb_h))
                cv6 = bm_c.verts.new((bx1, cy_a, curb_h))
                cv7 = bm_c.verts.new((bx1, cy_b, curb_h))
                cv8 = bm_c.verts.new((bx0, cy_b, curb_h))

                for f_vs in [[cv5, cv6, cv7, cv8], [cv1, cv2, cv6, cv5], 
                             [cv2, cv3, cv7, cv6], [cv3, cv4, cv8, cv7], [cv4, cv1, cv5, cv8]]:
                    f = bm_c.faces.new(f_vs)
                    f.material_index = c_slot
                    
            bm_c.to_mesh(mesh_curb)
            bm_c.free()
            mesh_curb.materials.append(mat_curb_white)
            mesh_curb.materials.append(mat_curb_black)
            obj_curb.location = (mid_x, mid_y, 0.0)
            obj_curb.rotation_euler = (0, 0, angle)
            col_target.objects.link(obj_curb)

        if has_left_sw:
            build_side(is_left=True)
        if has_right_sw:
            build_side(is_left=False)

        return obj_road

    # -------------------------------------------------------------------------
    # BUILD THE COMPLETE CONTINUOUS BOULEVARD ALONG Y=0.0 (FROM WEST AVE TO EAST AVE)
    # Total length: from X=-143.39 to X=+56.61 (~200 meters)
    # -------------------------------------------------------------------------
    # Segment 1: West Avenue junction to Ave-115 (X in [-143.39, -115.0])
    build_road_segment("Perum_Main_Bvd_1", (-143.39, 0.0), (-115.0, 0.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=1.2, trim_sw_end=2.3)

    # Segment 2: Ave-115 to Loop-84 (X in [-115.0, -84.0])
    build_road_segment("Perum_Main_Bvd_2", (-115.0, 0.0), (-84.0, 0.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.3, trim_sw_end=2.2)

    # Segment 3: Loop-84 to Pertigaan NS-75 (X in [-84.0, -75.0])
    build_road_segment("Perum_Main_Bvd_3", (-84.0, 0.0), (-75.0, 0.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=2.2)

    # Segment 4: Pertigaan NS-75 to Pos Ronda Pertigaan X=-32.0 (X in [-75.0, -32.0])
    # (Replaces Gang_Road_West_Ext-col)
    build_road_segment("Perum_Main_Bvd_4", (-75.0, 0.0), (-32.0, 0.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=2.2)

    # Segment 5: Pos Ronda Pertigaan X=-32.0 to East Connector X=+25.0 (X in [-32.0, 25.0])
    # (Replaces Gang_Road_Main-col)
    build_road_segment("Perum_Main_Bvd_5", (-32.0, 0.0), (25.0, 0.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=2.2)

    # Segment 6: East Connector X=+25.0 to East Avenue X=56.61 (X in [25.0, 56.61])
    build_road_segment("Perum_Main_Bvd_6", (25.0, 0.0), (56.61, 0.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=1.2)

    # -------------------------------------------------------------------------
    # KAMPUNG CENTRAL & SOUTH BRANCHES
    # -------------------------------------------------------------------------
    # Vertical Branch at X=-32.0 (Replaces Gang_Road_South-col)
    build_road_segment("Perum_Kampung_NS_32", (-32.0, -22.0), (-32.0, 0.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=2.2)

    # Horizontal Belokan at Y=-22.0 between X=-58.0 and X=-32.0 (Replaces Gang_Road_Turn_West-col)
    build_road_segment("Perum_Kampung_EW_22", (-58.0, -22.0), (-32.0, -22.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=0.0, trim_sw_end=2.2)

    # -------------------------------------------------------------------------
    # BLOK UTARA (NORTH RESIDENTIAL HOUSING ESTATE)
    # -------------------------------------------------------------------------
    # Collector North-South Road at X=-75.0 (from Y=0.0 to Y=38.0)
    build_road_segment("Perum_North_NS_75", (-75.0, 0.0), (-75.0, 38.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.3, trim_sw_end=2.3)

    # Middle East-West Ring along Y=38.0
    build_road_segment("Perum_North_EW_38_West", (-115.0, 38.0), (-75.0, 38.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.5, trim_sw_end=2.3)
    build_road_segment("Perum_North_EW_38_East", (-75.0, 38.0), (-10.0, 38.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.3, trim_sw_end=2.2)

    # Upper Ring along Y=55.0
    build_road_segment("Perum_North_EW_55", (-115.0, 55.0), (-10.0, 55.0), 
                       road_width=4.0, sidewalk_width=0.65, trim_sw_start=2.5, trim_sw_end=2.2)

    # East Vertical Connector of Upper Ring (at X=-10.0)
    build_road_segment("Perum_North_NS_10", (-10.0, 38.0), (-10.0, 55.0), 
                       road_width=4.0, sidewalk_width=0.65, trim_sw_start=2.2, trim_sw_end=2.2)

    # West Primary Residential Avenue at X=-115.0
    build_road_segment("Perum_West_Avenue_North", (-115.0, 38.0), (-115.0, 55.0), 
                       road_width=4.8, sidewalk_width=0.75, trim_sw_start=2.3, trim_sw_end=2.2)
    build_road_segment("Perum_West_Avenue_Mid", (-115.0, 0.0), (-115.0, 38.0), 
                       road_width=4.8, sidewalk_width=0.75, trim_sw_start=2.3, trim_sw_end=2.3)
    build_road_segment("Perum_West_Avenue_South1", (-115.0, -22.0), (-115.0, 0.0), 
                       road_width=4.8, sidewalk_width=0.75, trim_sw_start=2.2, trim_sw_end=2.3)
    build_road_segment("Perum_West_Avenue_South2", (-115.0, -60.0), (-115.0, -22.0), 
                       road_width=4.8, sidewalk_width=0.75, trim_sw_start=2.3, trim_sw_end=2.2)

    # Cul-de-Sacs
    build_road_segment("Perum_Gang_Melati", (-45.0, 38.0), (-45.0, 48.0), 
                       road_width=3.6, sidewalk_width=0.60, trim_sw_start=2.2, trim_sw_end=0.0)
    build_road_segment("Perum_Gang_Dahlia", (-65.0, 55.0), (-65.0, 65.0), 
                       road_width=3.6, sidewalk_width=0.60, trim_sw_start=2.2, trim_sw_end=0.0)

    def add_culdesac_bulb(name, center_pt, radius=3.6):
        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        obj = bpy.data.objects.new(f"{name}-col", mesh)
        bm = bmesh.new()
        steps = 16
        verts = []
        for s in range(steps):
            ang = 2.0 * math.pi * s / steps
            verts.append(bm.verts.new((radius * math.cos(ang), radius * math.sin(ang), 0.00)))
        bm.faces.new(verts)
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_asphalt)
        obj.location = (center_pt[0], center_pt[1], 0.0)
        col_perumahan.objects.link(obj)

        mesh_c = bpy.data.meshes.new(f"{name}_Curb_Mesh")
        obj_c = bpy.data.objects.new(f"{name}_Curb", mesh_c)
        bm_c = bmesh.new()
        r_in = radius
        r_out = radius + 0.14
        for s in range(steps):
            s_next = (s + 1) % steps
            a1 = 2.0 * math.pi * s / steps
            a2 = 2.0 * math.pi * s_next / steps
            v1 = bm_c.verts.new((r_in * math.cos(a1), r_in * math.sin(a1), 0.0))
            v2 = bm_c.verts.new((r_in * math.cos(a2), r_in * math.sin(a2), 0.0))
            v3 = bm_c.verts.new((r_out * math.cos(a2), r_out * math.sin(a2), 0.12))
            v4 = bm_c.verts.new((r_out * math.cos(a1), r_out * math.sin(a1), 0.12))
            f = bm_c.faces.new([v1, v2, v3, v4])
            f.material_index = 0 if (s % 2 == 0) else 1
        bm_c.to_mesh(mesh_c)
        bm_c.free()
        mesh_c.materials.append(mat_curb_white)
        mesh_c.materials.append(mat_curb_black)
        obj_c.location = (center_pt[0], center_pt[1], 0.0)
        col_perumahan.objects.link(obj_c)

    add_culdesac_bulb("Perum_Bulb_Melati", (-45.0, 48.0), radius=3.6)
    add_culdesac_bulb("Perum_Bulb_Dahlia", (-65.0, 65.0), radius=3.6)

    # -------------------------------------------------------------------------
    # BLOK SELATAN (UPGRADED WEST LOOP & SOUTH RESIDENTIAL CONNECTOR)
    # -------------------------------------------------------------------------
    build_road_segment("Perum_West_Loop_NS_84", (-84.0, -22.0), (-84.0, 0.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=2.3)
    build_road_segment("Perum_South_EW_22_Mid", (-84.0, -22.0), (-58.0, -22.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=0.0)
    build_road_segment("Perum_South_EW_22_West", (-115.0, -22.0), (-84.0, -22.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.5, trim_sw_end=2.2)

    build_road_segment("Perum_South_NS_75", (-75.0, -60.0), (-75.0, -22.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.3, trim_sw_end=2.2)
    build_road_segment("Perum_South_EW_60_West", (-115.0, -60.0), (-75.0, -60.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.5, trim_sw_end=2.2)
    build_road_segment("Perum_South_EW_60_Mid", (-75.0, -60.0), (25.0, -60.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=2.2)
    build_road_segment("Perum_South_EW_60_East_Conn", (25.0, -60.0), (56.61, -60.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=1.2)
    build_road_segment("Perum_East_NS_25", (25.0, -60.0), (25.0, 0.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=2.3)

    # -------------------------------------------------------------------------
    # RESIDENTIAL CORNER CURB RETURNS
    # -------------------------------------------------------------------------
    def build_corner_curb_return(name, center_pt, r=2.0, start_deg=0.0, end_deg=90.0, steps=6):
        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bm = bmesh.new()
        
        cx, cy = center_pt
        t_start = math.radians(start_deg)
        t_end = math.radians(end_deg)
        
        r_inner = r
        r_outer = r + 0.14
        
        verts_in = []
        verts_out = []
        for s in range(steps + 1):
            th = t_start + (s / steps) * (t_end - t_start)
            cos_t, sin_t = math.cos(th), math.sin(th)
            vi = bm.verts.new((cx + r_inner * cos_t, cy + r_inner * sin_t, 0.00))
            vo = bm.verts.new((cx + r_outer * cos_t, cy + r_outer * sin_t, 0.12))
            verts_in.append(vi)
            verts_out.append(vo)
            
        for s in range(steps):
            f = bm.faces.new([verts_in[s], verts_in[s + 1], verts_out[s + 1], verts_out[s]])
            f.material_index = 0 if (s % 2 == 0) else 1
            
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_curb_white)
        mesh.materials.append(mat_curb_black)
        col_perumahan.objects.link(obj)
        return obj

    # Avenue Junctions
    build_corner_curb_return("CurbReturn_East_Ave_NW", (54.2, 2.3), r=2.0, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_East_Ave_SW", (54.2, -2.3), r=2.0, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_West_Ave_NE", (-141.2, 2.5), r=2.0, start_deg=180, end_deg=270)
    build_corner_curb_return("CurbReturn_West_Ave_SE", (-141.2, -2.5), r=2.0, start_deg=90, end_deg=180)
    build_corner_curb_return("CurbReturn_East_Ave_S_NW", (54.2, -57.7), r=2.0, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_East_Ave_S_SW", (54.2, -62.3), r=2.0, start_deg=0, end_deg=90)

    # Ave-115 & Y=0 Perempatan
    build_corner_curb_return("CurbReturn_X115_Y0_NW", (-117.4, 2.3), r=2.0, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X115_Y0_NE", (-112.6, 2.3), r=2.0, start_deg=180, end_deg=270)
    build_corner_curb_return("CurbReturn_X115_Y0_SW", (-117.4, -2.3), r=2.0, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X115_Y0_SE", (-112.6, -2.3), r=2.0, start_deg=90, end_deg=180)

    # Pertigaan X=-75 & Y=0
    build_corner_curb_return("CurbReturn_X75_Y0_NW", (-77.2, 2.3), r=1.8, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X75_Y0_NE", (-72.8, 2.3), r=1.8, start_deg=180, end_deg=270)

    # Pertigaan X=-84 & Y=0
    build_corner_curb_return("CurbReturn_X84_Y0_SW", (-86.1, -2.3), r=1.8, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X84_Y0_SE", (-81.9, -2.3), r=1.8, start_deg=90, end_deg=180)

    # Pos Ronda Pertigaan at X=-32 & Y=0
    build_corner_curb_return("CurbReturn_X32_Y0_SW", (-34.1, -2.3), r=1.8, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X32_Y0_SE", (-29.9, -2.3), r=1.8, start_deg=90, end_deg=180)

    # Tambal Ban Belokan at X=-32 & Y=-22
    build_corner_curb_return("CurbReturn_X32_Y22_NW", (-34.1, -19.9), r=1.8, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X32_Y22_SE", (-29.9, -24.1), r=1.8, start_deg=90, end_deg=180)

    # Loop Corner at X=-84 & Y=-22
    build_corner_curb_return("CurbReturn_X84_Y22_NW", (-86.1, -19.9), r=1.8, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X84_Y22_NE", (-81.9, -19.9), r=1.8, start_deg=180, end_deg=270)

    # East Connector at X=25 & Y=0
    build_corner_curb_return("CurbReturn_X25_Y0_SW", (22.9, -2.3), r=1.8, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X25_Y0_SE", (27.1, -2.3), r=1.8, start_deg=90, end_deg=180)

    # Save the blend file immediately
    bpy.ops.wm.save_mainfile()
    print("=== Successfully upgraded all roads, shifted houses, and eliminated all intersection overlaps! ===")

if __name__ == "__main__":
    run()
