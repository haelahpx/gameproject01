"""
Script to edit and upgrade the existing campus road mesh (Gang_Road_Main-col.002) in Blender:
- Modifies the existing shape directly (NO new objects added).
- Extends the cross-section to include:
  1. Main asphalt roadway (9.0m width)
  2. Elevated sidewalks (trotoar) on BOTH North and South sides (2.7m width each, raised 18cm)
  3. Painted curbs (alternating black and white curb stones)
  4. Road lines (white dashed center line, solid white edge lines)
  5. Zebra crossing pedestrian crosswalk directly aligned with the campus gate entrance.
"""

import bpy  # pyrefly: ignore[missing-import] # type: ignore
import bmesh  # pyrefly: ignore[missing-import] # type: ignore
import math

def upgrade_road():
    road_obj = bpy.data.objects.get("Gang_Road_Main-col.002")
    if not road_obj:
        print("Error: Gang_Road_Main-col.002 not found!")
        return

    # Ensure transforms are applied so local units = world meters
    bpy.context.view_layer.objects.active = road_obj
    road_obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    # -------------------------------------------------------------------------
    # 1. SETUP MATERIALS
    # -------------------------------------------------------------------------
    def get_or_create_mat(name, rgba, roughness=0.5, metallic=0.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = rgba
            bsdf.inputs['Roughness'].default_value = roughness
            bsdf.inputs['Metallic'].default_value = metallic
        return mat

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
    # 2. X PROFILE (Length along road: 246 meters)
    # -------------------------------------------------------------------------
    # Road runs from X = -123.0 to +123.0
    # Campus gate is at world X = -48.18. Since road origin is at X = -29.27:
    # Local gate X = -48.18 - (-29.27) = -18.91
    # Zebra cross will be from X = -22.5 to -15.5 (7m wide crosswalk)
    x_points = []
    
    # West of zebra cross: step 1.5m
    cur_x = -123.0
    while cur_x < -22.5:
        x_points.append(round(cur_x, 4))
        cur_x += 1.5
    
    # Zebra cross: step 0.5m (14 stripes: alternating white and asphalt)
    cur_x = -22.5
    while cur_x < -15.5:
        x_points.append(round(cur_x, 4))
        cur_x += 0.5
    
    # East of zebra cross: step 1.5m
    cur_x = -15.5
    while cur_x <= 123.001:
        x_points.append(round(cur_x, 4))
        cur_x += 1.5
    if x_points[-1] < 123.0:
        x_points.append(123.0)

    # -------------------------------------------------------------------------
    # 3. Y PROFILE (Cross-section: 16 points)
    # -------------------------------------------------------------------------
    # y0: South sidewalk outer bottom edge
    # y1: South sidewalk outer top edge
    # y2: South sidewalk inner / curb back
    # y3: South curb top front
    # y4: South curb bottom / gutter
    # y5: South white line outer
    # y6: South white line inner
    # y7: Center white line south
    # y8: Center white line north
    # y9: North white line inner
    # y10: North white line outer
    # y11: North curb bottom / gutter
    # y12: North curb top front
    # y13: North sidewalk inner / curb back
    # y14: North sidewalk outer top edge
    # y15: North sidewalk outer bottom edge
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

    # -------------------------------------------------------------------------
    # 4. BUILD MESH WITH BMESH
    # -------------------------------------------------------------------------
    bm = bmesh.new()

    # Create grid of vertices: grid[i][j] where i is x index, j is y index
    grid = []
    for i, x in enumerate(x_points):
        row = []
        for j, (y, z) in enumerate(y_z_profile):
            # If in zebra cross, lower sidewalk curb slightly for pedestrian ramp
            vz = z
            v = bm.verts.new((x, y, vz))
            row.append(v)
        grid.append(row)

    bm.verts.ensure_lookup_table()

    # Create faces along the segments
    for i in range(len(x_points) - 1):
        x_start = x_points[i]
        x_end = x_points[i + 1]
        x_mid = (x_start + x_end) / 2.0

        # Curb alternating color (every 1.5m)
        curb_seg_idx = int(math.floor((x_mid - (-123.0)) / 1.5))
        curb_slot = slot_curb_white if (curb_seg_idx % 2 == 0) else slot_curb_black

        # Center line dashed pattern (3m line, 3m gap)
        center_seg_idx = int(math.floor((x_mid - (-123.0)) / 3.0))
        center_is_dash = (center_seg_idx % 2 == 0)

        # Is this segment in the Zebra Cross zone?
        is_in_zebra_zone = (-22.5 <= x_start and x_end <= -15.5)
        zebra_stripe_idx = int(round((x_start - (-22.5)) / 0.5))
        is_zebra_white = is_in_zebra_zone and (zebra_stripe_idx % 2 == 0)

        # Build faces between row i and row i+1 for each y strip (0 to num_y - 2)
        for j in range(num_y - 1):
            v_bl = grid[i][j]
            v_br = grid[i + 1][j]
            v_tr = grid[i + 1][j + 1]
            v_tl = grid[i][j + 1]

            face = bm.faces.new((v_bl, v_br, v_tr, v_tl))

            # Assign material slot based on strip index j:
            if j == 0:
                # South outer vertical wall
                face.material_index = slot_sidewalk
            elif j == 1:
                # South sidewalk top surface (walking area)
                face.material_index = slot_sidewalk
            elif j == 2:
                # South curb top
                face.material_index = curb_slot
            elif j == 3:
                # South curb vertical face
                face.material_index = curb_slot
            elif j == 4:
                # South gutter asphalt
                face.material_index = slot_asphalt
            elif j == 5:
                # South solid white edge line
                face.material_index = slot_line_white
            elif j == 6:
                # South travel lane
                if is_in_zebra_zone:
                    face.material_index = slot_line_white if is_zebra_white else slot_asphalt
                else:
                    face.material_index = slot_asphalt
            elif j == 7:
                # Center line
                if is_in_zebra_zone:
                    face.material_index = slot_line_white if is_zebra_white else slot_asphalt
                else:
                    face.material_index = slot_line_white if center_is_dash else slot_asphalt
            elif j == 8:
                # North travel lane
                if is_in_zebra_zone:
                    face.material_index = slot_line_white if is_zebra_white else slot_asphalt
                else:
                    face.material_index = slot_asphalt
            elif j == 9:
                # North solid white edge line
                face.material_index = slot_line_white
            elif j == 10:
                # North gutter asphalt
                face.material_index = slot_asphalt
            elif j == 11:
                # North curb vertical face
                face.material_index = curb_slot
            elif j == 12:
                # North curb top
                face.material_index = curb_slot
            elif j == 13:
                # North sidewalk top surface (walking area)
                face.material_index = slot_sidewalk
            elif j == 14:
                # North outer vertical wall
                face.material_index = slot_sidewalk

        # Bottom face to close the solid underside (between y0 and y15)
        face_bot = bm.faces.new((grid[i][0], grid[i][num_y - 1], grid[i + 1][num_y - 1], grid[i + 1][0]))
        face_bot.material_index = slot_asphalt

    # End caps at x = -123.0 and x = +123.0
    bm.faces.new([grid[0][j] for j in range(num_y)]).material_index = slot_asphalt
    bm.faces.new([grid[-1][j] for j in reversed(range(num_y))]).material_index = slot_asphalt

    # Calculate UVs for all faces
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        for loop in face.loops:
            v_co = loop.vert.co
            loop[uv_layer].uv = (v_co.x * 0.5, v_co.y * 0.5)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    # -------------------------------------------------------------------------
    # 5. ASSIGN TO EXISTING OBJECT MESH
    # -------------------------------------------------------------------------
    old_mesh = road_obj.data
    new_mesh = bpy.data.meshes.new(road_obj.name + "_Mesh")
    bm.to_mesh(new_mesh)
    bm.free()

    # Assign material slots to new mesh
    for mat in materials:
        new_mesh.materials.append(mat)

    road_obj.data = new_mesh
    bpy.data.meshes.remove(old_mesh, do_unlink=True)

    print(f"Successfully upgraded {road_obj.name}:")
    print(f"  Vertices: {len(new_mesh.vertices)}, Polygons: {len(new_mesh.polygons)}")
    print(f"  Material slots: {[m.name for m in new_mesh.materials]}")
    print(f"  Total width: {y_z_profile[-1][0] - y_z_profile[0][0]}m (Roadway: 9m + Trotoar: 2x 2.7m)")

if __name__ == "__main__":
    upgrade_road()
