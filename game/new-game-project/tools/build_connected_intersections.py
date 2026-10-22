"""
Script to connect campus roads and build the 4-way intersection (perempatan):
1. Upgrades Gang_Road_Main-col.001 (East N-S Road) with 2-sided trotoar, markings, and perempatan opening.
2. Upgrades Gang_Road_Main-col.003 (West N-S Road) with 2-sided trotoar, markings, and intersection opening.
3. Updates Gang_Road_Main-col.002 (Campus Front E-W Road) so sidewalks/curbs open seamlessly at both intersections with zebra crossings.
4. Builds 4 working Traffic Light poles (Lampu Merah: Merah, Kuning, Hijau) at the East perempatan (X = 61.11, Y = -165.24).
"""

import bpy  # pyrefly: ignore[missing-import] # type: ignore
import bmesh  # pyrefly: ignore[missing-import] # type: ignore
import math

def get_or_create_mat(name, rgba, roughness=0.5, metallic=0.0, emission=None):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = rgba
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
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

def build_intersections():
    # Materials
    m_asphalt = bpy.data.materials.get("road_asphalt.005") or get_or_create_mat("road_asphalt.005", (0.16, 0.16, 0.18, 1.0), roughness=0.7)
    m_sidewalk = bpy.data.materials.get("Mat_Sidewalk.001") or get_or_create_mat("Mat_Sidewalk.001", (0.82, 0.83, 0.84, 1.0), roughness=0.55)
    m_line_white = bpy.data.materials.get("road_marking_white") or get_or_create_mat("road_marking_white", (0.94, 0.94, 0.92, 1.0), roughness=0.3)
    m_curb_white = bpy.data.materials.get("curb_white") or get_or_create_mat("curb_white", (0.88, 0.88, 0.86, 1.0), roughness=0.45)
    m_curb_black = bpy.data.materials.get("curb_black") or get_or_create_mat("curb_black", (0.14, 0.14, 0.16, 1.0), roughness=0.45)

    materials = [m_asphalt, m_sidewalk, m_line_white, m_curb_white, m_curb_black]
    slot_asphalt = 0
    slot_sidewalk = 1
    slot_line_white = 2
    slot_curb_white = 3
    slot_curb_black = 4

    # -------------------------------------------------------------------------
    # 1. UPGRADE Gang_Road_Main-col.002 (East-West Road in front of Campus)
    # -------------------------------------------------------------------------
    road_ew = bpy.data.objects.get("Gang_Road_Main-col.002")
    if road_ew:
        bpy.context.view_layer.objects.active = road_ew
        road_ew.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # X points from -123.0 to +123.0
        # West intersection center: X = -147.89 -> local x = -147.89 - (-29.27) = -118.62
        # Campus gate zebra cross: local x = -48.18 - (-29.27) = -18.91 (from -22.5 to -15.5)
        # East intersection center: X = 61.11 -> local x = 61.11 - (-29.27) = +90.38
        # West junction: from -123.12 to -114.12 (width 9m)
        # East junction: from 85.88 to 94.88 (width 9m)
        # East West-approach zebra cross: from 81.5 to 85.5
        # East East-approach zebra cross: from 95.0 to 99.0
        x_pts = []
        cur_x = -123.0
        while cur_x <= 123.001:
            # High-res steps in zebra zones and junction zones
            if -22.5 <= cur_x <= -15.5 or 81.5 <= cur_x <= 85.5 or 95.0 <= cur_x <= 99.0:
                x_pts.append(round(cur_x, 4))
                cur_x += 0.5
            elif -123.0 <= cur_x <= -114.0 or 85.5 <= cur_x <= 95.0:
                x_pts.append(round(cur_x, 4))
                cur_x += 1.0
            else:
                x_pts.append(round(cur_x, 4))
                cur_x += 1.5
        if x_pts[-1] < 123.0:
            x_pts.append(123.0)

        # Transverse Y profile
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

        bm = bmesh.new()
        grid = []
        for i, x in enumerate(x_pts):
            row = []
            # Check if this x slice is inside an intersection opening
            is_west_junction = (-123.0 <= x <= -114.12)
            is_east_junction = (85.88 <= x <= 94.88)
            is_junction = is_west_junction or is_east_junction

            for j, (y, z) in enumerate(y_z_profile):
                vz = z
                # If inside junction, lower curbs and sidewalks to road grade (z = 0.0) so intersecting traffic flows flush!
                if is_junction and (j in [1, 2, 3, 12, 13, 14]):
                    vz = 0.0
                v = bm.verts.new((x, y, vz))
                row.append(v)
            grid.append(row)
        bm.verts.ensure_lookup_table()

        for i in range(len(x_pts) - 1):
            x_start = x_pts[i]
            x_end = x_pts[i + 1]
            x_mid = (x_start + x_end) / 2.0

            is_west_junc = (-123.0 <= x_start and x_end <= -114.0)
            is_east_junc = (85.5 <= x_start and x_end <= 95.0)
            is_in_junc = is_west_junc or is_east_junc

            curb_seg_idx = int(math.floor((x_mid - (-123.0)) / 1.5))
            curb_slot = slot_curb_white if (curb_seg_idx % 2 == 0) else slot_curb_black

            center_seg_idx = int(math.floor((x_mid - (-123.0)) / 3.0))
            center_is_dash = (center_seg_idx % 2 == 0)

            # Check zebra crossing zones
            is_gate_zebra = (-22.5 <= x_start and x_end <= -15.5)
            gate_stripe_idx = int(round((x_start - (-22.5)) / 0.5))
            is_gate_white = is_gate_zebra and (gate_stripe_idx % 2 == 0)

            is_east_zebra_w = (81.5 <= x_start and x_end <= 85.5)
            east_stripe_idx_w = int(round((x_start - 81.5) / 0.5))
            is_ez_w_white = is_east_zebra_w and (east_stripe_idx_w % 2 == 0)

            is_east_zebra_e = (95.0 <= x_start and x_end <= 99.0)
            east_stripe_idx_e = int(round((x_start - 95.0) / 0.5))
            is_ez_e_white = is_east_zebra_e and (east_stripe_idx_e % 2 == 0)

            is_any_zebra_white = is_gate_white or is_ez_w_white or is_ez_e_white
            is_any_zebra_zone = is_gate_zebra or is_east_zebra_w or is_east_zebra_e

            for j in range(num_y - 1):
                face = bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))

                if is_in_junc:
                    # Inside the intersection junction, entire roadway and crossway is smooth asphalt
                    face.material_index = slot_asphalt
                else:
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

            face_bot = bm.faces.new((grid[i][0], grid[i][num_y - 1], grid[i + 1][num_y - 1], grid[i + 1][0]))
            face_bot.material_index = slot_asphalt

        bm.faces.new([grid[0][j] for j in range(num_y)]).material_index = slot_asphalt
        bm.faces.new([grid[-1][j] for j in reversed(range(num_y))]).material_index = slot_asphalt

        uv_layer = bm.loops.layers.uv.new("UVMap")
        for face in bm.faces:
            for loop in face.loops:
                v_co = loop.vert.co
                loop[uv_layer].uv = (v_co.x * 0.5, v_co.y * 0.5)

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        old_mesh = road_ew.data
        new_mesh = bpy.data.meshes.new(road_ew.name + "_Mesh")
        bm.to_mesh(new_mesh)
        bm.free()

        for mat in materials:
            new_mesh.materials.append(mat)
        road_ew.data = new_mesh
        bpy.data.meshes.remove(old_mesh, do_unlink=True)
        print("Updated Gang_Road_Main-col.002 with seamless intersection openings.")

    # -------------------------------------------------------------------------
    # 2. UPGRADE Gang_Road_Main-col.001 (East North-South Road) & .003 (West N-S Road)
    # -------------------------------------------------------------------------
    def build_ns_road(obj_name, is_east_road=True):
        road_ns = bpy.data.objects.get(obj_name)
        if not road_ns:
            print(f"Error: {obj_name} not found!")
            return

        bpy.context.view_layer.objects.active = road_ns
        road_ns.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # Road runs along Y: origin is at Y = -113.84
        # Length ~395.2m (from y = -197.6 to +197.6)
        # Intersection with E-W road is at world Y = -165.24 -> local y = -165.24 - (-113.84) = -51.40m
        # Intersection opening: from y = -55.90 to -46.90 (width 9m)
        # Zebra crosses on North approach (y in [-44.0, -40.0]) and South approach (y in [-62.0, -58.0])
        y_pts = []
        cur_y = -197.6
        while cur_y <= 197.601:
            if is_east_road and ((-62.0 <= cur_y <= -58.0) or (-44.0 <= cur_y <= -40.0)):
                y_pts.append(round(cur_y, 4))
                cur_y += 0.5
            elif -56.0 <= cur_y <= -46.5:
                y_pts.append(round(cur_y, 4))
                cur_y += 1.0
            else:
                y_pts.append(round(cur_y, 4))
                cur_y += 2.0
        if y_pts[-1] < 197.6:
            y_pts.append(197.6)

        # Transverse X profile across width 15m (from West to East):
        # 0: West outer bottom
        # 1: West outer top
        # 2: West sidewalk inner
        # 3: West curb top
        # 4: West gutter
        # 5: West edge line outer
        # 6: West edge line inner
        # 7: Center line west
        # 8: Center line east
        # 9: East edge line inner
        # 10: East edge line outer
        # 11: East gutter
        # 12: East curb top
        # 13: East sidewalk inner
        # 14: East outer top
        # 15: East outer bottom
        x_z_profile = [
            (-7.50, -0.15),
            (-7.50,  0.18),
            (-4.80,  0.18),
            (-4.50,  0.18),
            (-4.50,  0.00),
            (-4.20,  0.00),
            (-4.05,  0.00),
            (-0.10,  0.00),
            ( 0.10,  0.00),
            ( 4.05,  0.00),
            ( 4.20,  0.00),
            ( 4.50,  0.00),
            ( 4.50,  0.18),
            ( 4.80,  0.18),
            ( 7.50,  0.18),
            ( 7.50, -0.15),
        ]
        num_x = len(x_z_profile)

        bm = bmesh.new()
        grid = []
        for i, y in enumerate(y_pts):
            row = []
            is_junction = (-55.90 <= y <= -46.90)
            for j, (x, z) in enumerate(x_z_profile):
                vz = z
                # Inside intersection opening, lower sidewalks/curbs to road grade
                if is_junction:
                    if is_east_road:
                        # 4-way perempatan: both sides open!
                        if j in [1, 2, 3, 12, 13, 14]:
                            vz = 0.0
                    else:
                        # West road: East side connects to E-W road (j in [12, 13, 14])
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

            is_junc = (-55.90 <= y_start and y_end <= -46.90)

            curb_seg_idx = int(math.floor((y_mid - (-197.6)) / 1.5))
            curb_slot = slot_curb_white if (curb_seg_idx % 2 == 0) else slot_curb_black

            center_seg_idx = int(math.floor((y_mid - (-197.6)) / 3.0))
            center_is_dash = (center_seg_idx % 2 == 0)

            # Zebra crossing zones on approaches
            is_south_zebra = is_east_road and (-62.0 <= y_start and y_end <= -58.0)
            s_stripe_idx = int(round((y_start - (-62.0)) / 0.5)) if is_south_zebra else 0
            is_s_zebra_white = is_south_zebra and (s_stripe_idx % 2 == 0)

            is_north_zebra = is_east_road and (-44.0 <= y_start and y_end <= -40.0)
            n_stripe_idx = int(round((y_start - (-44.0)) / 0.5)) if is_north_zebra else 0
            is_n_zebra_white = is_north_zebra and (n_stripe_idx % 2 == 0)

            is_any_zebra_white = is_s_zebra_white or is_n_zebra_white
            is_any_zebra_zone = is_south_zebra or is_north_zebra

            for j in range(num_x - 1):
                face = bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))

                if is_junc:
                    face.material_index = slot_asphalt
                else:
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

            face_bot = bm.faces.new((grid[i][0], grid[i + 1][0], grid[i + 1][num_x - 1], grid[i][num_x - 1]))
            face_bot.material_index = slot_asphalt

        bm.faces.new([grid[0][j] for j in reversed(range(num_x))]).material_index = slot_asphalt
        bm.faces.new([grid[-1][j] for j in range(num_x)]).material_index = slot_asphalt

        uv_layer = bm.loops.layers.uv.new("UVMap")
        for face in bm.faces:
            for loop in face.loops:
                v_co = loop.vert.co
                loop[uv_layer].uv = (v_co.x * 0.5, v_co.y * 0.5)

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        old_mesh = road_ns.data
        new_mesh = bpy.data.meshes.new(road_ns.name + "_Mesh")
        bm.to_mesh(new_mesh)
        bm.free()

        for mat in materials:
            new_mesh.materials.append(mat)
        road_ns.data = new_mesh
        bpy.data.meshes.remove(old_mesh, do_unlink=True)
        print(f"Successfully upgraded {obj_name} with trotoar on both sides and intersection.")

    build_ns_road("Gang_Road_Main-col.001", is_east_road=True)
    build_ns_road("Gang_Road_Main-col.003", is_east_road=False)

    # -------------------------------------------------------------------------
    # 3. BUILD WORKING TRAFFIC LIGHTS AT THE EAST PEREMPATAN (X = 61.11, Y = -165.24)
    # -------------------------------------------------------------------------
    ca = bpy.data.collections.get("CampusArea") or bpy.context.scene.collection

    # Clean previous traffic light objects if any
    old_tl = [o for o in bpy.data.objects if o.name.startswith("TrafficLight_")]
    for o in old_tl:
        bpy.data.objects.remove(o, do_unlink=True)

    m_tl_pole = get_or_create_mat("Mat_Traffic_Pole", (0.24, 0.25, 0.27, 1.0), roughness=0.35, metallic=0.85)
    m_tl_housing = get_or_create_mat("Mat_Traffic_Housing", (0.08, 0.08, 0.09, 1.0), roughness=0.55)
    m_tl_red = get_or_create_mat("Mat_Traffic_Red", (0.95, 0.08, 0.08, 1.0), roughness=0.15, emission=((0.95, 0.08, 0.08, 1.0), 3.0))
    m_tl_yellow = get_or_create_mat("Mat_Traffic_Yellow", (0.95, 0.75, 0.05, 1.0), roughness=0.15, emission=((0.95, 0.75, 0.05, 1.0), 3.0))
    m_tl_green = get_or_create_mat("Mat_Traffic_Green", (0.05, 0.95, 0.25, 1.0), roughness=0.15, emission=((0.05, 0.95, 0.25, 1.0), 3.0))

    # 4 Corner Traffic Light Posts at Perempatan (Center: X=61.11, Y=-165.24)
    # Sidewalk corners are at X = 61.11 +/- 6.2m, Y = -165.24 +/- 6.2m
    tl_corners = [
        ("NE", 61.11 + 6.2, -165.24 + 6.2, "South"),  # Northeast corner: faces traffic coming from South/East
        ("NW", 61.11 - 6.2, -165.24 + 6.2, "East"),   # Northwest corner: faces traffic coming from East/North
        ("SE", 61.11 + 6.2, -165.24 - 6.2, "West"),   # Southeast corner: faces traffic coming from West/South
        ("SW", 61.11 - 6.2, -165.24 - 6.2, "North"),  # Southwest corner: faces traffic coming from North/West
    ]

    for corner_id, px, py, face_dir in tl_corners:
        base_name = f"TrafficLight_{corner_id}"

        # Vertical Mast Pole (height 6.0m)
        create_cyl(f"{base_name}_Pole-col", (px, py, 3.0), radius=0.14, depth=6.0, mat=m_tl_pole, rot=(0,0,0), collection=ca)
        create_cyl(f"{base_name}_Base", (px, py, 0.2), radius=0.28, depth=0.4, mat=m_tl_pole, rot=(0,0,0), collection=ca)

        # Overhead Cantilever Mast Arm extending over roadway
        if "N" in corner_id:
            arm_dy = -3.5
            arm_py = py - 1.75
        else:
            arm_dy = 3.5
            arm_py = py + 1.75
        create_box(f"{base_name}_Arm", (px, arm_py, 5.8), (0.12, abs(arm_dy), 0.12), m_tl_pole, ca)

        # Overhead Signal Head Housing (at height 5.2m over the roadway)
        hx = px
        hy = py + arm_dy
        create_box(f"{base_name}_Head_Overhead-col", (hx, hy, 5.2), (0.45, 0.35, 1.30), m_tl_housing, ca)
        # Red, Yellow, Green signal lenses (Overhead)
        create_cyl(f"{base_name}_Lens_Red_Overhead", (hx, hy, 5.55), radius=0.14, depth=0.08, mat=m_tl_red, rot=(math.pi/2, 0, 0), collection=ca)
        create_cyl(f"{base_name}_Lens_Yellow_Overhead", (hx, hy, 5.20), radius=0.14, depth=0.08, mat=m_tl_yellow, rot=(math.pi/2, 0, 0), collection=ca)
        create_cyl(f"{base_name}_Lens_Green_Overhead", (hx, hy, 4.85), radius=0.14, depth=0.08, mat=m_tl_green, rot=(math.pi/2, 0, 0), collection=ca)

        # Eye-level Signal Head Housing (mounted on post at height 3.0m)
        create_box(f"{base_name}_Head_Post-col", (px, py, 3.0), (0.40, 0.30, 1.10), m_tl_housing, ca)
        create_cyl(f"{base_name}_Lens_Red_Post", (px, py, 3.32), radius=0.12, depth=0.06, mat=m_tl_red, rot=(math.pi/2, 0, 0), collection=ca)
        create_cyl(f"{base_name}_Lens_Yellow_Post", (px, py, 3.00), radius=0.12, depth=0.06, mat=m_tl_yellow, rot=(math.pi/2, 0, 0), collection=ca)
        create_cyl(f"{base_name}_Lens_Green_Post", (px, py, 2.68), radius=0.12, depth=0.06, mat=m_tl_green, rot=(math.pi/2, 0, 0), collection=ca)

    print("All road connections, trotoars, markings, and 4 traffic light structures successfully built!")

if __name__ == "__main__":
    build_intersections()
