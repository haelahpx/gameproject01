"""
Script to build comprehensive kampung & perumahan road network and jalan raya drainage system in Blender:
1. Removes temporary disconnected boxes on the west side.
2. Updates East Avenue (Gang_Road_Main-col.001) and West Avenue (Gang_Road_Main-col.003) to have flush openings at Y=0.0 and Y=-60.0.
3. Builds high-detail roadside drainage system:
   - Cast-iron gully grates with recessed water basins along gutters
   - Curb inlet scuppers (lubang pembuangan air trotoar)
   - Heavy cast-iron sewer manhole covers with embossed pattern
   - Sidewalk drainage inspection hatches
4. Builds the hierarchical residential road network with trimmed sidewalk/curb intersections:
   - Zero curb obstructions inside junction boxes (clean asphalt transitions)
   - Smooth corner curb returns with alternating black-and-white curb stones
   - Connects both East and West dead-ends directly to the Jalan Raya
   - Creates Kompleks Perumahan Blok Utara (housing rings, T-junctions, and cul-de-sacs with turning bulbs)
   - Creates Kompleks Perumahan Blok Selatan (connected loops and south arterial connector)
5. All roads include asphalt, painted white center markings, and sidewalks with alternating black-and-white curb blocks.
"""

import bpy  # pyrefly: ignore[missing-import] # type: ignore
import bmesh  # pyrefly: ignore[missing-import] # type: ignore
import math
from mathutils import Vector  # pyrefly: ignore[missing-import] # type: ignore

def run():
    print("=== Starting build_kampung_roads_and_drainage.py ===")

    # -------------------------------------------------------------------------
    # Helper to get or create collection
    # -------------------------------------------------------------------------
    def get_or_create_col(name, parent_col=None):
        if name in bpy.data.collections:
            return bpy.data.collections[name]
        col = bpy.data.collections.new(name)
        if parent_col:
            parent_col.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
        return col

    col_drainage = get_or_create_col("RoadDrainage")
    col_perumahan = get_or_create_col("PerumahanRoads")

    # Materials
    mat_asphalt = bpy.data.materials.get("road_asphalt")
    mat_asphalt_dark = bpy.data.materials.get("road_asphalt_dark") or mat_asphalt
    mat_marking_white = bpy.data.materials.get("road_marking_white")
    mat_curb_concrete = bpy.data.materials.get("curb_concrete") or bpy.data.materials.get("Mat_ConcreteCurb.001")
    mat_curb_black = bpy.data.materials.get("curb_black")
    mat_curb_white = bpy.data.materials.get("curb_white")
    mat_dark_iron = bpy.data.materials.get("Mat_DarkIron.001")
    mat_drain_trench = bpy.data.materials.get("drain_trench")

    # -------------------------------------------------------------------------
    # 1. CLEANUP UNFINISHED / FLOATING WEST ROAD OBJECTS & TEST OBJECTS
    # -------------------------------------------------------------------------
    cleanup_names = [
        "Test_Drain_Grate",
        "Gang_Road_South-col.001",
        "Gang_Road_Turn_West-col.001",
        "Gang_Road_Turn_West-col.002",
    ]
    # Also clean up any previously generated perumahan & drainage objects
    for obj in list(bpy.data.objects):
        if any(obj.name.startswith(p) for p in ["Perum_", "DrainGrate_", "Manhole_", "CurbReturn_", "DrainInlet_", "SidewalkHatch_"]):
            cleanup_names.append(obj.name)

    for name in cleanup_names:
        obj = bpy.data.objects.get(name)
        if obj:
            mesh = obj.data if obj.type == 'MESH' else None
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)

    # -------------------------------------------------------------------------
    # 2. UPGRADE EAST AVENUE (.001) & WEST AVENUE (.003) WITH OPENINGS AT Y=0.0 & Y=-60.0
    # -------------------------------------------------------------------------
    def rebuild_ns_avenue(obj_name, is_east_road=True):
        road_ns = bpy.data.objects.get(obj_name)
        if not road_ns:
            print(f"Warning: {obj_name} not found!")
            return

        bpy.context.view_layer.objects.active = road_ns
        road_ns.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        mats = [mat_asphalt, mat_curb_concrete, mat_marking_white, mat_curb_white, mat_curb_black]
        road_ns.data.materials.clear()
        for m in mats:
            road_ns.data.materials.append(m)

        slot_asphalt = 0
        slot_sidewalk = 1
        slot_line_white = 2
        slot_curb_white = 3
        slot_curb_black = 4

        # Origin is at Y = -113.84
        # World Y = -165.24 -> local y = -51.40 (Campus front avenue)
        # World Y = -60.0   -> local y = +53.84 (South perumahan road)
        # World Y = 0.0     -> local y = +113.84 (Main kampung boulevard)
        
        y_pts = []
        cur_y = -197.6
        while cur_y <= 197.601:
            in_campus_junc = (-64.0 <= cur_y <= -38.0)
            in_south_junc = (50.5 <= cur_y <= 57.5)
            in_kampung_junc = (110.5 <= cur_y <= 117.5)
            
            if is_east_road and ((-62.0 <= cur_y <= -58.0) or (-44.0 <= cur_y <= -40.0)):
                y_pts.append(round(cur_y, 4))
                cur_y += 0.5
            elif in_campus_junc or in_south_junc or in_kampung_junc:
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

        bm = bmesh.new()
        grid = []
        for i, y in enumerate(y_pts):
            row = []
            is_campus_junc = (-55.90 <= y <= -46.90)
            is_south_junc = (51.0 <= y <= 56.5)      # World Y ~ -62.8 to -57.3
            is_kampung_junc = (111.0 <= y <= 116.5)  # World Y ~ -2.8 to +2.7

            for j, (x, z) in enumerate(x_z_profile):
                vz = z
                if is_campus_junc:
                    if is_east_road:
                        if j in [1, 2, 3, 12, 13, 14]:
                            vz = 0.0
                    else:
                        if j in [12, 13, 14]:
                            vz = 0.0
                elif is_south_junc or is_kampung_junc:
                    if is_east_road:
                        if j in [1, 2, 3]:
                            vz = 0.0
                    else:
                        if j in [12, 13, 14]:
                            vz = 0.0

                v = bm.verts.new((x, y, vz))
                row.append(v)
            grid.append(row)
        bm.verts.ensure_lookup_table()

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

            is_south_zebra = is_east_road and (-62.0 <= y_start and y_end <= -58.0)
            s_stripe_idx = int(round((y_start - (-62.0)) / 0.5)) if is_south_zebra else 0
            is_s_zebra_white = is_south_zebra and (s_stripe_idx % 2 == 0)

            is_north_zebra = is_east_road and (-44.0 <= y_start and y_end <= -40.0)
            n_stripe_idx = int(round((y_start - (-44.0)) / 0.5)) if is_north_zebra else 0
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
                    mat_slot = slot_asphalt if ((not is_east_road) and (is_campus_junc_seg or is_south_junc_seg or is_kampung_junc_seg)) else curb_slot
                elif j == 13:
                    mat_slot = slot_asphalt if ((not is_east_road) and (is_campus_junc_seg or is_south_junc_seg or is_kampung_junc_seg)) else slot_sidewalk

                face = bm.faces.new([v1, v2, v3, v4])
                face.material_index = mat_slot

        old_mesh = road_ns.data
        new_mesh = bpy.data.meshes.new(f"{obj_name}_Mesh")
        bm.to_mesh(new_mesh)
        bm.free()

        for m in mats:
            new_mesh.materials.append(m)
        road_ns.data = new_mesh
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
        print(f"Rebuilt avenue {obj_name} with junction openings at Y=0 and Y=-60.")

    rebuild_ns_avenue("Gang_Road_Main-col.001", is_east_road=True)
    rebuild_ns_avenue("Gang_Road_Main-col.003", is_east_road=False)

    # -------------------------------------------------------------------------
    # 3. BUILD JALAN RAYA DRAINAGE SYSTEM ("pembuangan air / selokan / manholes")
    # -------------------------------------------------------------------------
    print("Building high-detail roadside drainage system...")

    # Cast-Iron Storm Drain Grate + Water Recess Catch Basin
    def build_grate_mesh(name_prefix):
        mesh = bpy.data.meshes.new(f"{name_prefix}_Mesh")
        bm = bmesh.new()

        fl, fw = 0.85, 0.45
        rim = 0.05
        z_top = 0.008

        # Recessed dark catch basin floor
        v_b1 = bm.verts.new((-fl/2 + rim, -fw/2 + rim, -0.07))
        v_b2 = bm.verts.new(( fl/2 - rim, -fw/2 + rim, -0.07))
        v_b3 = bm.verts.new(( fl/2 - rim,  fw/2 - rim, -0.07))
        v_b4 = bm.verts.new((-fl/2 + rim,  fw/2 - rim, -0.07))
        f_basin = bm.faces.new([v_b1, v_b2, v_b3, v_b4])
        f_basin.material_index = 1 # mat_drain_trench

        # Outer rim top
        x0, x1 = -fl/2, fl/2
        y0, y1 = -fw/2, fw/2
        ix0, ix1 = -fl/2 + rim, fl/2 - rim
        iy0, iy1 = -fw/2 + rim, fw/2 - rim

        def add_quad(pts, mat_idx):
            vs = [bm.verts.new((px, py, pz)) for px, py, pz in pts]
            f = bm.faces.new(vs)
            f.material_index = mat_idx
            return f

        # Rim top quads (cast iron)
        add_quad([(x0, y0, z_top), (x1, y0, z_top), (x1, iy0, z_top), (x0, iy0, z_top)], 0)
        add_quad([(x0, iy1, z_top), (x1, iy1, z_top), (x1, y1, z_top), (x0, y1, z_top)], 0)
        add_quad([(x0, iy0, z_top), (ix0, iy0, z_top), (ix0, iy1, z_top), (x0, iy1, z_top)], 0)
        add_quad([(ix1, iy0, z_top), (x1, iy0, z_top), (x1, iy1, z_top), (ix1, iy1, z_top)], 0)

        # 6 longitudinal cast iron grate bars
        num_bars = 6
        bar_w = 0.026
        inner_w = iy1 - iy0
        spacing = inner_w / (num_bars + 1)
        for bi in range(1, num_bars + 1):
            by_mid = iy0 + bi * spacing
            by_a = by_mid - bar_w/2
            by_b = by_mid + bar_w/2
            add_quad([(ix0, by_a, z_top), (ix1, by_a, z_top), (ix1, by_b, z_top), (ix0, by_b, z_top)], 0)

        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_dark_iron)
        mesh.materials.append(mat_drain_trench)
        return mesh

    grate_shared_mesh = build_grate_mesh("Shared_Drain_Grate")

    def place_grate(name, loc, rot_z=0.0):
        obj = bpy.data.objects.new(name, grate_shared_mesh)
        obj.location = loc
        obj.rotation_euler = (0, 0, rot_z)
        col_drainage.objects.link(obj)
        return obj

    # Curb Inlet Opening (Lubang Masuk Air Trotoar)
    def build_curb_inlet_mesh(name_prefix):
        mesh = bpy.data.meshes.new(f"{name_prefix}_Mesh")
        bm = bmesh.new()
        # Mouth opening in the curb face: length 0.60m, height 0.08m, depth 0.15m
        cw, ch, cd = 0.60, 0.08, 0.15
        z_bot = 0.01
        z_top = z_bot + ch

        v1 = bm.verts.new((-cw/2, -cd, z_bot))
        v2 = bm.verts.new(( cw/2, -cd, z_bot))
        v3 = bm.verts.new(( cw/2,  0.0, z_bot))
        v4 = bm.verts.new((-cw/2,  0.0, z_bot))
        v5 = bm.verts.new((-cw/2, -cd, z_top))
        v6 = bm.verts.new(( cw/2, -cd, z_top))
        v7 = bm.verts.new(( cw/2,  0.0, z_top))
        v8 = bm.verts.new((-cw/2,  0.0, z_top))

        bm.faces.new([v1, v2, v6, v5]) # back wall (dark)
        bm.faces.new([v5, v6, v7, v8]) # ceiling
        bm.faces.new([v4, v3, v2, v1]) # floor
        bm.faces.new([v4, v1, v5, v8]) # left side
        bm.faces.new([v2, v3, v7, v6]) # right side

        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_drain_trench)
        return mesh

    inlet_shared_mesh = build_curb_inlet_mesh("Shared_Curb_Inlet")

    def place_curb_inlet(name, loc, rot_z=0.0):
        obj = bpy.data.objects.new(name, inlet_shared_mesh)
        obj.location = loc
        obj.rotation_euler = (0, 0, rot_z)
        col_drainage.objects.link(obj)
        return obj

    # A. East Avenue Grates (X = 61.11, West gutter X=56.88, East gutter X=65.34)
    grate_count = 0
    for y in range(-290, 75, 18):
        if (-175 <= y <= -155) or (-66 <= y <= -54) or (-6 <= y <= 6):
            continue
        place_grate(f"DrainGrate_East_W_{y}", (56.88, float(y), 0.00), rot_z=math.radians(90))
        place_curb_inlet(f"DrainInlet_East_W_{y}", (56.61, float(y), 0.00), rot_z=math.radians(90))
        place_grate(f"DrainGrate_East_E_{y}", (65.34, float(y), 0.00), rot_z=math.radians(90))
        place_curb_inlet(f"DrainInlet_East_E_{y}", (65.61, float(y), 0.00), rot_z=math.radians(-90))
        grate_count += 2

    # B. West Avenue Grates (X = -147.89, East gutter X=-143.82, West gutter X=-151.96)
    for y in range(-290, 75, 18):
        if (-175 <= y <= -155) or (-66 <= y <= -54) or (-6 <= y <= 6):
            continue
        place_grate(f"DrainGrate_West_E_{y}", (-143.82, float(y), 0.00), rot_z=math.radians(90))
        place_curb_inlet(f"DrainInlet_West_E_{y}", (-143.39, float(y), 0.00), rot_z=math.radians(-90))
        place_grate(f"DrainGrate_West_W_{y}", (-151.96, float(y), 0.00), rot_z=math.radians(90))
        place_curb_inlet(f"DrainInlet_West_W_{y}", (-152.39, float(y), 0.00), rot_z=math.radians(90))
        grate_count += 2

    # C. Campus Front Avenue Grates (Y = -165.24, North gutter Y=-161.18, South gutter Y=-169.30)
    for x in range(-136, 50, 18):
        if (-52 <= x <= -44):
            continue
        place_grate(f"DrainGrate_Camp_N_{x}", (float(x), -161.18, 0.00), rot_z=0.0)
        place_curb_inlet(f"DrainInlet_Camp_N_{x}", (float(x), -160.74, 0.00), rot_z=0.0)
        place_grate(f"DrainGrate_Camp_S_{x}", (float(x), -169.30, 0.00), rot_z=0.0)
        place_curb_inlet(f"DrainInlet_Camp_S_{x}", (float(x), -169.74, 0.00), rot_z=math.radians(180))
        grate_count += 2

    print(f"Placed {grate_count} drainage grates and curb inlets along Jalan Raya.")

    # D. Circular Sewer Manholes (Tutup Got Besi Cor)
    def build_manhole_mesh(name_prefix):
        mesh = bpy.data.meshes.new(f"{name_prefix}_Mesh")
        bm = bmesh.new()
        r_inner = 0.36
        r_rim = 0.44
        z_base = 0.008
        segments = 20
        
        verts_outer = []
        verts_mid = []
        verts_inner = []
        v_center = bm.verts.new((0.0, 0.0, z_base + 0.005))

        for s in range(segments):
            ang = 2.0 * math.pi * s / segments
            cos_a, sin_a = math.cos(ang), math.sin(ang)
            verts_outer.append(bm.verts.new((r_rim * cos_a, r_rim * sin_a, z_base)))
            verts_mid.append(bm.verts.new((r_inner * cos_a, r_inner * sin_a, z_base + 0.003)))
            verts_inner.append(bm.verts.new((0.18 * cos_a, 0.18 * sin_a, z_base + 0.005)))

        for s in range(segments):
            s_next = (s + 1) % segments
            bm.faces.new([verts_outer[s], verts_outer[s_next], verts_mid[s_next], verts_mid[s]])
            bm.faces.new([verts_mid[s], verts_mid[s_next], verts_inner[s_next], verts_inner[s]])
            bm.faces.new([verts_inner[s], verts_inner[s_next], v_center])

        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_dark_iron)
        return mesh

    manhole_shared_mesh = build_manhole_mesh("Shared_Manhole")

    def place_manhole(name, loc):
        obj = bpy.data.objects.new(name, manhole_shared_mesh)
        obj.location = loc
        col_drainage.objects.link(obj)
        return obj

    manhole_locs = [
        (61.11, -120.0, 0.0), (61.11, -30.0, 0.0), (61.11, 40.0, 0.0), (61.11, -210.0, 0.0),
        (-147.89, -120.0, 0.0), (-147.89, -30.0, 0.0), (-147.89, 40.0, 0.0), (-147.89, -210.0, 0.0),
        (-90.0, -165.24, 0.0), (-10.0, -165.24, 0.0), (30.0, -165.24, 0.0),
        (40.0, 0.0, 0.0), (-75.0, 0.0, 0.0), (-115.0, 0.0, 0.0),
        (-75.0, 38.0, 0.0), (-115.0, 38.0, 0.0), (-115.0, -60.0, 0.0), (-25.0, -60.0, 0.0)
    ]
    for mi, mloc in enumerate(manhole_locs):
        place_manhole(f"Manhole_Cover_{mi}", mloc)

    # E. Sidewalk Drainage Inspection Hatches (Plat Besi Got Trotoar)
    def build_sidewalk_hatch_mesh(name_prefix):
        mesh = bpy.data.meshes.new(f"{name_prefix}_Mesh")
        bm = bmesh.new()
        hw = 0.30
        z = 0.185
        v1 = bm.verts.new((-hw, -hw, z))
        v2 = bm.verts.new(( hw, -hw, z))
        v3 = bm.verts.new(( hw,  hw, z))
        v4 = bm.verts.new((-hw,  hw, z))
        bm.faces.new([v1, v2, v3, v4])
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_dark_iron)
        return mesh

    hatch_mesh = build_sidewalk_hatch_mesh("Shared_Hatch")
    for y in range(-250, 60, 45):
        if (-175 <= y <= -155):
            continue
        # East Avenue sidewalks
        h_e1 = bpy.data.objects.new(f"SidewalkHatch_E_W_{y}", hatch_mesh)
        h_e1.location = (55.1, float(y), 0.0)
        col_drainage.objects.link(h_e1)
        h_e2 = bpy.data.objects.new(f"SidewalkHatch_E_E_{y}", hatch_mesh)
        h_e2.location = (67.1, float(y), 0.0)
        col_drainage.objects.link(h_e2)
        # West Avenue sidewalks
        h_w1 = bpy.data.objects.new(f"SidewalkHatch_W_E_{y}", hatch_mesh)
        h_w1.location = (-141.9, float(y), 0.0)
        col_drainage.objects.link(h_w1)
        h_w2 = bpy.data.objects.new(f"SidewalkHatch_W_W_{y}", hatch_mesh)
        h_w2.location = (-153.9, float(y), 0.0)
        col_drainage.objects.link(h_w2)

    print("Completed drainage detailing.")

    # -------------------------------------------------------------------------
    # 4. HIGH-PRECISION MODULAR BUILDER FOR RESIDENTIAL / PERUMAHAN ROADS
    # -------------------------------------------------------------------------
    def build_road_segment(name, p_start, p_end, road_width=4.2, sidewalk_width=0.70, 
                           trim_sw_start=0.0, trim_sw_end=0.0,
                           has_left_sw=True, has_right_sw=True, has_centerline=True, 
                           col_target=col_perumahan):
        """
        Creates an aligned, fully featured road segment:
        - Asphalt surface (-col for collision) spanning full length for continuous pavement.
        - Dashed white center road markings.
        - Elevated sidewalks on left/right with alternating black & white curb blocks,
          trimmed at junctions by trim_sw_start / trim_sw_end to keep intersection boxes 100% open!
        """
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
            
            # Start and end markings inside the trimmed bounds so they don't intrude into junction
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

            # 1. Sidewalk slab
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

            # 2. Alternating Black & White Curb Blocks facing the asphalt
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
    # 5. BUILD THE CONNECTED RESIDENTIAL ROAD NETWORK (TATA KOTA PERUMAHAN)
    # -------------------------------------------------------------------------
    print("Building connected residential roads with clean junction openings...")

    # A. CONNECTING THE DISCONNECTED DEAD-ENDS:
    # 1. Main East Connection: from X=27.0 to East Avenue X=56.61 along Y=0.0
    # Meets existing kampung road at X=27.0 (no trim needed at start), meets East Avenue at X=56.61 (trim 1.0m before avenue gutter)
    build_road_segment("Perum_East_Main_Conn", (27.0, 0.0), (56.61, 0.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=0.0, trim_sw_end=1.2,
                       has_left_sw=True, has_right_sw=True)

    # 2. Main West Boulevard: from X=-60.0 through X=-84.0 and X=-115.0 to West Avenue X=-143.39 along Y=0.0
    # Conn 1: X in [-84.0, -60.0] -> start at -84 (junction with NS-84, trim 2.2m), end at -60 (meets old road, trim 0)
    build_road_segment("Perum_West_Main_Conn_1", (-84.0, 0.0), (-60.0, 0.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.3, trim_sw_end=0.0,
                       has_left_sw=True, has_right_sw=True)

    # Conn 2: X in [-115.0, -84.0] -> start at -115 (junction with Ave-115, trim 2.5m), end at -84 (junction with NS-84, trim 2.3m)
    build_road_segment("Perum_West_Main_Conn_2", (-115.0, 0.0), (-84.0, 0.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.5, trim_sw_end=2.3,
                       has_left_sw=True, has_right_sw=True)

    # Conn 3: X in [-143.39, -115.0] -> start at -143.39 (West Ave, trim 1.2m), end at -115.0 (Ave-115, trim 2.5m)
    build_road_segment("Perum_West_Main_Conn_3", (-143.39, 0.0), (-115.0, 0.0), 
                       road_width=4.5, sidewalk_width=0.75, trim_sw_start=1.2, trim_sw_end=2.5,
                       has_left_sw=True, has_right_sw=True)

    # B. BLOK UTARA (NORTH RESIDENTIAL HOUSING ESTATE):
    # Secondary Collector North-South Road at X=-75.0 (from Y=0.0 to Y=38.0)
    # Trim start at Y=0 (meets Main Road width 4.2m -> trim 2.2m)
    # Trim end at Y=38.0 (meets EW-38 width 4.2m -> trim 2.2m)
    build_road_segment("Perum_North_NS_75", (-75.0, 0.0), (-75.0, 38.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.3, trim_sw_end=2.3,
                       has_left_sw=True, has_right_sw=True)

    # Middle East-West Ring along Y=38.0 (from X=-115.0 to X=-10.0, forming central T-junction at X=-75.0)
    # West half: X in [-115.0, -75.0]
    build_road_segment("Perum_North_EW_38_West", (-115.0, 38.0), (-75.0, 38.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.5, trim_sw_end=2.3,
                       has_left_sw=True, has_right_sw=True)
    # East half: X in [-75.0, -10.0]
    build_road_segment("Perum_North_EW_38_East", (-75.0, 38.0), (-10.0, 38.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.3, trim_sw_end=2.2,
                       has_left_sw=True, has_right_sw=True)

    # Upper Ring along Y=55.0 (from X=-115.0 to X=-10.0)
    build_road_segment("Perum_North_EW_55", (-115.0, 55.0), (-10.0, 55.0), 
                       road_width=4.0, sidewalk_width=0.65, trim_sw_start=2.5, trim_sw_end=2.2,
                       has_left_sw=True, has_right_sw=True)

    # East Vertical Connector of Upper Ring (from Y=38.0 to Y=55.0 at X=-10.0)
    build_road_segment("Perum_North_NS_10", (-10.0, 38.0), (-10.0, 55.0), 
                       road_width=4.0, sidewalk_width=0.65, trim_sw_start=2.2, trim_sw_end=2.2,
                       has_left_sw=True, has_right_sw=True)

    # West Primary Residential Avenue at X=-115.0 (Spans from Y=+55.0 down to Y=-60.0)
    build_road_segment("Perum_West_Avenue_North", (-115.0, 38.0), (-115.0, 55.0), 
                       road_width=4.8, sidewalk_width=0.75, trim_sw_start=2.3, trim_sw_end=2.2,
                       has_left_sw=True, has_right_sw=True)
    build_road_segment("Perum_West_Avenue_Mid", (-115.0, 0.0), (-115.0, 38.0), 
                       road_width=4.8, sidewalk_width=0.75, trim_sw_start=2.3, trim_sw_end=2.3,
                       has_left_sw=True, has_right_sw=True)
    build_road_segment("Perum_West_Avenue_South1", (-115.0, -22.0), (-115.0, 0.0), 
                       road_width=4.8, sidewalk_width=0.75, trim_sw_start=2.2, trim_sw_end=2.3,
                       has_left_sw=True, has_right_sw=True)
    build_road_segment("Perum_West_Avenue_South2", (-115.0, -60.0), (-115.0, -22.0), 
                       road_width=4.8, sidewalk_width=0.75, trim_sw_start=2.3, trim_sw_end=2.2,
                       has_left_sw=True, has_right_sw=True)

    # Residential Cul-de-Sacs / Gang Buntu
    # Gang Melati (at X=-45.0, branching north from Y=38.0 to Y=48.0)
    build_road_segment("Perum_Gang_Melati", (-45.0, 38.0), (-45.0, 48.0), 
                       road_width=3.6, sidewalk_width=0.60, trim_sw_start=2.2, trim_sw_end=0.0,
                       has_left_sw=True, has_right_sw=True)
    # Gang Dahlia (at X=-65.0, branching north from Y=55.0 to Y=65.0)
    build_road_segment("Perum_Gang_Dahlia", (-65.0, 55.0), (-65.0, 65.0), 
                       road_width=3.6, sidewalk_width=0.60, trim_sw_start=2.2, trim_sw_end=0.0,
                       has_left_sw=True, has_right_sw=True)

    # Turning bulb / bundaran putar balik for cul-de-sacs
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

    # C. BLOK SELATAN (UPGRADED WEST LOOP & SOUTH RESIDENTIAL CONNECTOR):
    # Upgraded West Loop segment at X=-84.0 (connecting Y=0.0 to Y=-22.0)
    build_road_segment("Perum_West_Loop_NS_84", (-84.0, 0.0), (-84.0, -22.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.3, trim_sw_end=2.2,
                       has_left_sw=True, has_right_sw=True)

    # Upgraded South horizontal segment at Y=-22.0
    build_road_segment("Perum_South_EW_22_Mid", (-84.0, -22.0), (-58.0, -22.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=0.0,
                       has_left_sw=True, has_right_sw=True)
    build_road_segment("Perum_South_EW_22_West", (-115.0, -22.0), (-84.0, -22.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.5, trim_sw_end=2.2,
                       has_left_sw=True, has_right_sw=True)

    # South Connector Road at X=-75.0 (from Y=-22.0 down to Y=-60.0)
    build_road_segment("Perum_South_NS_75", (-75.0, -22.0), (-75.0, -60.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=2.3,
                       has_left_sw=True, has_right_sw=True)

    # Jalan Lingkungan Asri Selatan at Y=-60.0 (from X=-115.0 to X=+25.0)
    build_road_segment("Perum_South_EW_60_West", (-115.0, -60.0), (-75.0, -60.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.5, trim_sw_end=2.2,
                       has_left_sw=True, has_right_sw=True)
    build_road_segment("Perum_South_EW_60_Mid", (-75.0, -60.0), (25.0, -60.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=2.2,
                       has_left_sw=True, has_right_sw=True)

    # South East Avenue Connector: from X=+25.0 to East Avenue X=56.61 along Y=-60.0
    build_road_segment("Perum_South_EW_60_East_Conn", (25.0, -60.0), (56.61, -60.0), 
                       road_width=4.2, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=1.2,
                       has_left_sw=True, has_right_sw=True)

    # South-East Vertical Connector: from Y=-60.0 up to Y=0.0 at X=+25.0 (creating East perumahan loop)
    build_road_segment("Perum_East_NS_25", (25.0, -60.0), (25.0, 0.0), 
                       road_width=4.0, sidewalk_width=0.70, trim_sw_start=2.2, trim_sw_end=2.3,
                       has_left_sw=True, has_right_sw=True)

    # D. CORNER CURB RETURNS AT MAJOR PERTIGAAN / INTERSECTIONS
    def build_corner_curb_return(name, center_pt, r=2.2, start_deg=0.0, end_deg=90.0, steps=6):
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

    # 1. East Avenue Junction at Y=0.0, X=56.61:
    build_corner_curb_return("CurbReturn_East_Ave_NW", (54.2, 2.3), r=2.0, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_East_Ave_SW", (54.2, -2.3), r=2.0, start_deg=0, end_deg=90)

    # 2. West Avenue Junction at Y=0.0, X=-143.39:
    build_corner_curb_return("CurbReturn_West_Ave_NE", (-141.2, 2.5), r=2.0, start_deg=180, end_deg=270)
    build_corner_curb_return("CurbReturn_West_Ave_SE", (-141.2, -2.5), r=2.0, start_deg=90, end_deg=180)

    # 3. East Avenue Junction at Y=-60.0, X=56.61:
    build_corner_curb_return("CurbReturn_East_Ave_S_NW", (54.2, -57.7), r=2.0, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_East_Ave_S_SW", (54.2, -62.3), r=2.0, start_deg=0, end_deg=90)

    # 4. West Avenue at X=-115.0 & Y=0.0 (Perempatan corners):
    build_corner_curb_return("CurbReturn_X115_Y0_NW", (-117.4, 2.3), r=2.0, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X115_Y0_NE", (-112.6, 2.3), r=2.0, start_deg=180, end_deg=270)
    build_corner_curb_return("CurbReturn_X115_Y0_SW", (-117.4, -2.3), r=2.0, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X115_Y0_SE", (-112.6, -2.3), r=2.0, start_deg=90, end_deg=180)

    # 5. Pertigaan at X=-75.0 & Y=0.0:
    build_corner_curb_return("CurbReturn_X75_Y0_NW", (-77.2, 2.3), r=1.8, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X75_Y0_NE", (-72.8, 2.3), r=1.8, start_deg=180, end_deg=270)

    # 6. Pertigaan at X=-84.0 & Y=0.0:
    build_corner_curb_return("CurbReturn_X84_Y0_SW", (-86.1, -2.3), r=1.8, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X84_Y0_SE", (-81.9, -2.3), r=1.8, start_deg=90, end_deg=180)

    # 7. Corner at X=-84.0 & Y=-22.0:
    build_corner_curb_return("CurbReturn_X84_Y22_NW", (-86.1, -19.9), r=1.8, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X84_Y22_NE", (-81.9, -19.9), r=1.8, start_deg=180, end_deg=270)

    # Save the blend file immediately
    bpy.ops.wm.save_mainfile()
    print("=== Successfully built and saved kampung & perumahan roads and drainage details! ===")

if __name__ == "__main__":
    run()
