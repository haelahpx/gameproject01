"""
Build Complete Indonesian Kampung Kos & Gang Environment v4 (Rich Low-Poly Everywhere):
- Pillar 1 (Buildings): Two-tone color blocking (wainscoting & decorative moldings),
  window overhang awnings with diagonal brackets, outdoor AC condenser units with piping,
  PLN digital electricity meters with PVC conduit, rooftop TV antennas, shoe racks with
  colorful sandals (sandal jepit), and doormats at every doorway.
- Pillar 2 (Road & Gang): Alternating black-and-white painted curb segments, dashed center road
  markings, low-poly asphalt repair patches, concrete got slabs with drainage slots, hazard-striped
  speed bumps, street trash bins, and painted tire planters.
- Pillar 3 (Trees & Nature): Faceted low-poly trees with 4-5 clustered flat-shaded icospheres in
  3 gradient shades of green with root buttresses, Indonesian banana trees with arching leaves and
  blossom, leaning coconut palms with fronds, low-poly flowering bougainvillea bush clumps,
  and scattered grass tufts.
"""

import bpy
import bmesh
import mathutils
import math
import os

def clear_scene():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for block in list(bpy.data.meshes) + list(bpy.data.materials) + list(bpy.data.collections) + list(bpy.data.curves):
        if block.users == 0:
            if isinstance(block, bpy.types.Mesh):
                bpy.data.meshes.remove(block)
            elif isinstance(block, bpy.types.Material):
                bpy.data.materials.remove(block)
            elif isinstance(block, bpy.types.Collection):
                bpy.data.collections.remove(block)
            elif isinstance(block, bpy.types.Curve):
                bpy.data.curves.remove(block)

def create_mat(name, color, roughness=0.7, metallic=0.0, emission=None, emission_strength=1.0, alpha=1.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    
    if len(color) == 3:
        color = (color[0], color[1], color[2], 1.0)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Alpha'].default_value = alpha
    
    if alpha < 1.0:
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.90
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 0.90
        if hasattr(mat, 'blend_method'):
            mat.blend_method = 'BLEND'
    
    if emission:
        em_col = (emission[0], emission[1], emission[2], 1.0) if len(emission) == 3 else emission
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = em_col
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = em_col
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat

def get_col(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def add_box(name, center, size, mat_name, col_name, origin_at_bottom=False, rot=(0,0,0)):
    x, y, z = center
    sx, sy, sz = size
    if origin_at_bottom:
        z = z + sz / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z), rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Ensure flat low-poly shading
    for poly in obj.data.polygons:
        poly.use_smooth = False
    mat = bpy.data.materials.get(mat_name)
    if mat:
        obj.data.materials.append(mat)
    col = get_col(col_name)
    if obj.name not in col.objects:
        col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)
    return obj

def add_cylinder(name, center, radius, height, mat_name, col_name, rot=(0,0,0), vertices=12):
    x, y, z = center
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=height,
        location=(x, y, z),
        rotation=rot
    )
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for poly in obj.data.polygons:
        poly.use_smooth = False
    mat = bpy.data.materials.get(mat_name)
    if mat:
        obj.data.materials.append(mat)
    col = get_col(col_name)
    if obj.name not in col.objects:
        col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)
    return obj

def add_icosphere(name, center, radius, mat_name, col_name, subdivisions=1, scale=(1.0, 1.0, 1.0), rot=(0,0,0)):
    x, y, z = center
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=subdivisions,
        radius=radius,
        location=(x, y, z),
        rotation=rot
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for poly in obj.data.polygons:
        poly.use_smooth = False
    mat = bpy.data.materials.get(mat_name)
    if mat:
        obj.data.materials.append(mat)
    col = get_col(col_name)
    if obj.name not in col.objects:
        col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)
    return obj

def add_angled_bar(name, p1, p2, width, height, mat_name, col_name):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    col = get_col(col_name)
    col.objects.link(obj)

    v1 = mathutils.Vector(p1)
    v2 = mathutils.Vector(p2)
    dir_vec = v2 - v1
    length = dir_vec.length
    if length < 0.0001:
        return obj

    bm = bmesh.new()
    hw = width / 2.0
    hh = height / 2.0

    verts_bottom = [
        bm.verts.new((-hw, -hh, 0.0)),
        bm.verts.new(( hw, -hh, 0.0)),
        bm.verts.new(( hw,  hh, 0.0)),
        bm.verts.new((-hw,  hh, 0.0)),
    ]
    bm.faces.new(verts_bottom)
    extruded = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    extruded_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, length), verts=extruded_verts)

    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = False

    obj.location = v1
    forward = mathutils.Vector((0.0, 0.0, 1.0))
    rot_quat = forward.rotation_difference(dir_vec)
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = rot_quat

    mat = bpy.data.materials.get(mat_name)
    if mat:
        obj.data.materials.append(mat)
    return obj

# ─── PROCEDURAL LOW-POLY GENERATORS ───

def add_stylized_tree(tname, pos, height, trunk_radius, crown_radius, col_name="GangEnvironment"):
    tx, ty, tz = pos
    # Tapered trunk with 6 sides for sharp low poly facets
    add_cylinder(f"{tname}_Trunk-col", (tx, ty, tz + height * 0.45), trunk_radius, height * 0.9, "tree_trunk", col_name, vertices=6)
    # Root buttresses flaring into ground
    for i, a in enumerate([0.2, 2.3, 4.4]):
        rx = tx + math.cos(a) * (trunk_radius * 1.5)
        ry = ty + math.sin(a) * (trunk_radius * 1.5)
        add_box(f"{tname}_Root_{i}", (rx, ry, tz + 0.12), (trunk_radius * 1.3, trunk_radius * 0.7, 0.24), "tree_trunk", col_name, rot=(0, 0, a))
    
    # 4 Clustered faceted icospheres with flat shading in 3 shades of green (gradient canopy effect)
    clusters = [
        (0.0, 0.0, height * 0.90, 1.05, "plant_green_dark"),
        (-crown_radius * 0.35,  crown_radius * 0.30, height * 1.10, 0.85, "plant_green"),
        ( crown_radius * 0.35, -crown_radius * 0.25, height * 1.05, 0.80, "plant_green_lime"),
        (0.0, 0.0, height * 1.30, 0.65, "plant_green_lime")
    ]
    for idx, (ox, oy, oz, sf, mat) in enumerate(clusters):
        add_icosphere(f"{tname}_Crown_{idx}", (tx + ox, ty + oy, tz + oz), crown_radius * sf, mat, col_name, subdivisions=1)

def add_banana_tree(name, pos, height=3.0, col_name="GangEnvironment"):
    x, y, z = pos
    # Segmented green stalk
    add_cylinder(f"{name}_Stalk-col", (x, y, z + height * 0.45), 0.12, height * 0.9, "plant_banana_stem", col_name, vertices=6)
    # 6 Arching low-poly banana leaves radiating out
    for i in range(6):
        angle = i * (math.pi / 3.0) + 0.25
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        leaf_len = height * 0.60
        leaf_w = 0.35
        lx = x + cos_a * (leaf_len * 0.5)
        ly = y + sin_a * (leaf_len * 0.5)
        lz = z + height * 0.80
        add_box(f"{name}_Leaf_{i}", (lx, ly, lz), (leaf_len, leaf_w, 0.02), "plant_banana_leaf", col_name,
                rot=(math.radians(-18) * sin_a, math.radians(-18) * cos_a, angle))
    # Hanging banana blossom (jantung pisang)
    add_cylinder(f"{name}_Blossom", (x + 0.22, y + 0.22, z + height * 0.70), 0.07, 0.22, "flower_magenta", col_name, vertices=5)

def add_palm_tree(name, pos, height=5.2, col_name="GangEnvironment"):
    x, y, z = pos
    # Segmented leaning trunk
    add_cylinder(f"{name}_Trunk_1-col", (x, y, z + height * 0.25), 0.16, height * 0.5, "tree_trunk", col_name, vertices=6, rot=(math.radians(4), math.radians(-3), 0))
    add_cylinder(f"{name}_Trunk_2-col", (x + 0.18, y - 0.18, z + height * 0.70), 0.12, height * 0.5, "tree_trunk", col_name, vertices=6, rot=(math.radians(7), math.radians(-5), 0))
    top_x, top_y, top_z = x + 0.32, y - 0.32, z + height * 0.95
    # Radiating low-poly palm fronds
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        fx = top_x + math.cos(ang) * 1.3
        fy = top_y + math.sin(ang) * 1.3
        fz = top_z - 0.22
        mat = "plant_green_dark" if i % 2 == 0 else "plant_green"
        add_box(f"{name}_Frond_{i}", (fx, fy, fz), (1.9, 0.42, 0.03), mat, col_name,
                rot=(math.radians(-22) * math.sin(ang), math.radians(22) * math.cos(ang), ang))
    # Coconuts
    for i, a in enumerate([0.5, 2.6, 4.7]):
        cx = top_x + math.cos(a) * 0.22
        cy = top_y + math.sin(a) * 0.22
        add_icosphere(f"{name}_Coconut_{i}", (cx, cy, top_z - 0.14), 0.11, "plant_coconut", col_name, subdivisions=1)

def add_bush_clump(bname, pos, radius, col_name="GangEnvironment", flower_mat=None):
    bx, by, bz = pos
    add_icosphere(f"{bname}_Main", (bx, by, bz + radius * 0.7), radius, "plant_green_dark", col_name, subdivisions=1)
    add_icosphere(f"{bname}_Side1", (bx - radius * 0.45, by + radius * 0.3, bz + radius * 0.6), radius * 0.75, "plant_green", col_name, subdivisions=1)
    add_icosphere(f"{bname}_Side2", (bx + radius * 0.45, by - radius * 0.3, bz + radius * 0.65), radius * 0.70, "plant_green_lime", col_name, subdivisions=1)
    if flower_mat:
        for fi, (fx, fy, fz) in enumerate([(0.2, 0.1, 0.8), (-0.3, 0.2, 0.7), (0.1, -0.3, 0.65), (-0.1, 0.35, 0.6)]):
            add_icosphere(f"{bname}_Flw_{fi}", (bx + fx * radius, by + fy * radius, bz + fz * radius), radius * 0.18, flower_mat, col_name, subdivisions=1)

def add_ac_unit(name, center, face_axis='X', sign=1, col_name="Props"):
    cx, cy, cz = center
    if face_axis == 'X':
        add_box(f"{name}_Bracket_1", (cx - sign * 0.14, cy - 0.26, cz - 0.26), (0.30, 0.04, 0.04), "kost_dark_grey", col_name)
        add_box(f"{name}_Bracket_2", (cx - sign * 0.14, cy + 0.26, cz - 0.26), (0.30, 0.04, 0.04), "kost_dark_grey", col_name)
        add_box(f"{name}_Body", (cx, cy, cz), (0.28, 0.68, 0.48), "paint_bucket", col_name)
        add_cylinder(f"{name}_Grille", (cx + sign * 0.145, cy - 0.10, cz), 0.17, 0.02, "kost_dark_grey", col_name, rot=(0, math.radians(90), 0), vertices=10)
        add_cylinder(f"{name}_Cap", (cx + sign * 0.155, cy - 0.10, cz), 0.04, 0.025, "paint_bucket", col_name, rot=(0, math.radians(90), 0), vertices=6)
        add_cylinder(f"{name}_Pipe", (cx - sign * 0.04, cy + 0.24, cz + 0.32), 0.025, 0.45, "paint_bucket", col_name, vertices=6)
    else:
        add_box(f"{name}_Bracket_1", (cx - 0.26, cy - sign * 0.14, cz - 0.26), (0.04, 0.30, 0.04), "kost_dark_grey", col_name)
        add_box(f"{name}_Bracket_2", (cx + 0.26, cy - sign * 0.14, cz - 0.26), (0.04, 0.30, 0.04), "kost_dark_grey", col_name)
        add_box(f"{name}_Body", (cx, cy, cz), (0.68, 0.28, 0.48), "paint_bucket", col_name)
        add_cylinder(f"{name}_Grille", (cx - 0.10, cy + sign * 0.145, cz), 0.17, 0.02, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0), vertices=10)
        add_cylinder(f"{name}_Cap", (cx - 0.10, cy + sign * 0.155, cz), 0.04, 0.025, "paint_bucket", col_name, rot=(math.radians(90), 0, 0), vertices=6)
        add_cylinder(f"{name}_Pipe", (cx + 0.24, cy - sign * 0.04, cz + 0.32), 0.025, 0.45, "paint_bucket", col_name, vertices=6)

def add_kwh_meter(name, center, face_axis='Y', sign=1, col_name="Props"):
    cx, cy, cz = center
    if face_axis == 'Y':
        add_box(f"{name}_Box", (cx, cy + sign * 0.06, cz), (0.22, 0.10, 0.32), "curb_concrete", col_name)
        add_box(f"{name}_Screen", (cx, cy + sign * 0.115, cz + 0.06), (0.13, 0.015, 0.07), "plant_green", col_name)
        add_box(f"{name}_Keypad", (cx, cy + sign * 0.115, cz - 0.05), (0.14, 0.015, 0.09), "kost_dark_grey", col_name)
        add_box(f"{name}_Breaker", (cx, cy + sign * 0.12, cz - 0.12), (0.03, 0.02, 0.03), "pvc_blue", col_name)
        add_cylinder(f"{name}_Conduit", (cx, cy + sign * 0.03, cz + 0.75), 0.018, 1.3, "paint_bucket", col_name, vertices=6)
    else:
        add_box(f"{name}_Box", (cx + sign * 0.06, cy, cz), (0.10, 0.22, 0.32), "curb_concrete", col_name)
        add_box(f"{name}_Screen", (cx + sign * 0.115, cy, cz + 0.06), (0.015, 0.13, 0.07), "plant_green", col_name)
        add_box(f"{name}_Keypad", (cx + sign * 0.115, cy, cz - 0.05), (0.015, 0.14, 0.09), "kost_dark_grey", col_name)
        add_box(f"{name}_Breaker", (cx + sign * 0.12, cy, cz - 0.12), (0.02, 0.03, 0.03), "pvc_blue", col_name)
        add_cylinder(f"{name}_Conduit", (cx + sign * 0.03, cy, cz + 0.75), 0.018, 1.3, "paint_bucket", col_name, vertices=6)

def add_shoe_rack(name, center, col_name="KostBuilding"):
    cx, cy, cz = center
    add_box(f"{name}_Leg_FL", (cx - 0.32, cy - 0.11, cz + 0.26), (0.03, 0.03, 0.52), "wood_door_dark", col_name)
    add_box(f"{name}_Leg_FR", (cx + 0.32, cy - 0.11, cz + 0.26), (0.03, 0.03, 0.52), "wood_door_dark", col_name)
    add_box(f"{name}_Leg_BL", (cx - 0.32, cy + 0.11, cz + 0.26), (0.03, 0.03, 0.52), "wood_door_dark", col_name)
    add_box(f"{name}_Leg_BR", (cx + 0.32, cy + 0.11, cz + 0.26), (0.03, 0.03, 0.52), "wood_door_dark", col_name)
    for sz in [0.08, 0.26, 0.44]:
        add_box(f"{name}_Shelf_{sz}", (cx, cy, cz + sz), (0.68, 0.24, 0.02), "wood_light", col_name)
    # Pairs of low-poly flip-flops (sandal jepit Swallow)
    sandals = [
        (-0.18, 0.0, 0.09, "paint_bucket", "pvc_blue"),
        ( 0.18, 0.0, 0.09, "paint_bucket", "plant_green"),
        (-0.18, 0.0, 0.27, "paint_bucket", "clothes_red"),
        ( 0.18, 0.0, 0.27, "kost_dark_grey", "warsun_yellow")
    ]
    for si, (sx, sy, sz, sole_m, strap_m) in enumerate(sandals):
        add_box(f"{name}_Sandal_L_{si}", (cx + sx - 0.04, cy + sy, cz + sz + 0.015), (0.065, 0.18, 0.015), sole_m, col_name)
        add_box(f"{name}_Strap_L_{si}", (cx + sx - 0.04, cy + sy - 0.02, cz + sz + 0.025), (0.05, 0.04, 0.012), strap_m, col_name)
        add_box(f"{name}_Sandal_R_{si}", (cx + sx + 0.04, cy + sy, cz + sz + 0.015), (0.065, 0.18, 0.015), sole_m, col_name)
        add_box(f"{name}_Strap_R_{si}", (cx + sx + 0.04, cy + sy - 0.02, cz + sz + 0.025), (0.05, 0.04, 0.012), strap_m, col_name)

def add_doormat(name, center, mat_name, col_name="KostBuilding"):
    cx, cy, cz = center
    add_box(f"{name}_Border", (cx, cy, cz + 0.006), (0.68, 0.40, 0.012), "kost_dark_grey", col_name)
    add_box(f"{name}_Pad", (cx, cy, cz + 0.010), (0.62, 0.34, 0.012), mat_name, col_name)

def add_window_awning(name, center, size, face_axis='Y', sign=1, col_name="Props"):
    cx, cy, cz = center
    w, d, h = size
    # Angled canopy roof
    if face_axis == 'Y':
        canopy_y = cy + sign * (d * 0.5)
        add_box(f"{name}_Roof", (cx, canopy_y, cz), (w, d, 0.03), "tin_roof", col_name,
                rot=(math.radians(12) * sign, 0, 0))
        # Left & Right diagonal strut supports
        add_box(f"{name}_Strut_L", (cx - w*0.45, canopy_y, cz - 0.12), (0.03, d * 0.9, 0.03), "kost_railing_metal", col_name,
                rot=(math.radians(-30) * sign, 0, 0))
        add_box(f"{name}_Strut_R", (cx + w*0.45, canopy_y, cz - 0.12), (0.03, d * 0.9, 0.03), "kost_railing_metal", col_name,
                rot=(math.radians(-30) * sign, 0, 0))
    else:
        canopy_x = cx + sign * (d * 0.5)
        add_box(f"{name}_Roof", (canopy_x, cy, cz), (d, w, 0.03), "tin_roof", col_name,
                rot=(0, math.radians(-12) * sign, 0))
        add_box(f"{name}_Strut_L", (canopy_x, cy - w*0.45, cz - 0.12), (d * 0.9, 0.03, 0.03), "kost_railing_metal", col_name,
                rot=(0, math.radians(30) * sign, 0))
        add_box(f"{name}_Strut_R", (canopy_x, cy + w*0.45, cz - 0.12), (d * 0.9, 0.03, 0.03), "kost_railing_metal", col_name,
                rot=(0, math.radians(30) * sign, 0))

def add_tv_antenna(name, pos, height=2.0, col_name="GangHouses"):
    x, y, z = pos
    add_cylinder(f"{name}_Pole", (x, y, z + height * 0.5), 0.022, height, "kost_railing_metal", col_name, vertices=6)
    add_box(f"{name}_Boom", (x, y + 0.45, z + height), (0.03, 1.0, 0.03), "kost_railing_metal", col_name)
    for dy in [-0.35, -0.15, 0.05, 0.25]:
        ew = 0.50 - (dy + 0.35) * 0.25
        add_box(f"{name}_Elem_{dy}", (x, y + 0.45 + dy, z + height), (ew, 0.02, 0.02), "kost_railing_metal", col_name)

def build_all():
    print("Rebuilding Indonesian Kampung Kos with Rich Low-Poly Aesthetics v4...")
    clear_scene()

    # ─── 1. EXTENDED MATERIALS PALETTE ───
    create_mat("kost_wall_white", (0.92, 0.93, 0.94), roughness=0.75)
    create_mat("kost_wall_lower", (0.28, 0.34, 0.38), roughness=0.70)  # Two-tone slate-teal wainscoting
    create_mat("kost_wall_molding", (0.95, 0.95, 0.95), roughness=0.60) # Wainscoting trim
    create_mat("kost_concrete_grey", (0.55, 0.58, 0.62), roughness=0.85)
    create_mat("kost_dark_grey", (0.22, 0.24, 0.27), roughness=0.6)
    create_mat("kost_railing_metal", (0.75, 0.77, 0.80), roughness=0.3, metallic=0.7)
    create_mat("kost_floor_paving", (0.80, 0.82, 0.84), roughness=0.8)
    create_mat("kost_floor_interior", (0.88, 0.89, 0.90), roughness=0.7)
    create_mat("wall_plinth_grey", (0.22, 0.23, 0.25), roughness=0.85)
    create_mat("roster_vent", (0.35, 0.36, 0.38), roughness=0.85)

    create_mat("wc_tile_white", (0.92, 0.94, 0.96), roughness=0.25)
    create_mat("wc_water", (0.15, 0.65, 0.90), roughness=0.05, alpha=0.78)
    create_mat("pvc_blue", (0.18, 0.52, 0.82), roughness=0.3)
    create_mat("wood_door", (0.38, 0.20, 0.10), roughness=0.65)
    create_mat("wood_door_dark", (0.20, 0.11, 0.06), roughness=0.7)
    create_mat("wood_light", (0.75, 0.58, 0.38), roughness=0.7)

    # Glass materials
    create_mat("window_glass_transparent", (0.88, 0.95, 1.0), roughness=0.02, alpha=0.12)
    create_mat("glass_frosted", (0.82, 0.88, 0.94), roughness=0.65, alpha=0.40)
    create_mat("glass_showcase_transparent", (0.88, 0.95, 1.0), roughness=0.02, alpha=0.15)

    create_mat("toren_orange", (0.92, 0.42, 0.05), roughness=0.3)
    create_mat("warsun_yellow", (0.95, 0.75, 0.12), roughness=0.4)
    create_mat("warsun_orange", (0.90, 0.35, 0.08), roughness=0.4)
    create_mat("warsun_tile_floor", (0.88, 0.85, 0.80), roughness=0.6)
    create_mat("stainless_tray", (0.75, 0.77, 0.80), roughness=0.2, metallic=0.8)

    # Road & Infrastructure
    create_mat("road_asphalt", (0.16, 0.16, 0.18), roughness=0.90)
    create_mat("road_asphalt_dark", (0.10, 0.10, 0.12), roughness=0.85)  # Fresh bitumen patch
    create_mat("road_asphalt_worn", (0.22, 0.22, 0.24), roughness=0.95)  # Worn asphalt patch
    create_mat("road_marking_white", (0.92, 0.92, 0.90), roughness=0.60)
    create_mat("curb_black", (0.14, 0.14, 0.16), roughness=0.80)
    create_mat("curb_white", (0.88, 0.88, 0.86), roughness=0.75)
    create_mat("curb_concrete", (0.42, 0.42, 0.44), roughness=0.80)
    create_mat("drain_trench", (0.10, 0.10, 0.12), roughness=0.9)
    create_mat("got_slab", (0.48, 0.48, 0.50), roughness=0.85)

    create_mat("grass_lawn", (0.18, 0.38, 0.14), roughness=0.90)
    create_mat("iron_fence_black", (0.12, 0.13, 0.15), roughness=0.4, metallic=0.8)
    create_mat("brick_red", (0.60, 0.25, 0.16), roughness=0.9)
    create_mat("tin_roof", (0.48, 0.50, 0.52), roughness=0.5, metallic=0.4)
    create_mat("tile_roof_brown", (0.42, 0.18, 0.10), roughness=0.85)
    create_mat("roof_ridge_dark", (0.28, 0.12, 0.06), roughness=0.85)

    # House Two-Tone Wall Colors
    create_mat("wall_h1_lower", (0.24, 0.25, 0.27), roughness=0.85) # Architectural grey stone
    create_mat("wall_tosca", (0.24, 0.52, 0.48), roughness=0.8)
    create_mat("wall_tosca_lower", (0.14, 0.35, 0.32), roughness=0.8) # Deep teal wainscoting
    create_mat("wall_yellow", (0.82, 0.68, 0.28), roughness=0.8)
    create_mat("wall_yellow_lower", (0.58, 0.24, 0.14), roughness=0.8) # Terracotta lower band
    create_mat("wall_cream", (0.85, 0.82, 0.72), roughness=0.8)
    create_mat("wall_cream_lower", (0.25, 0.38, 0.24), roughness=0.8) # Forest sage lower band
    create_mat("wall_h4_lower", (0.16, 0.22, 0.34), roughness=0.8) # Deep navy lower band
    create_mat("wall_h6_lower", (0.38, 0.24, 0.18), roughness=0.8) # Clay umber lower band

    # Plants & Nature (Multi-Tone Gradient Palette)
    create_mat("plant_green_dark", (0.12, 0.30, 0.10), roughness=0.75)
    create_mat("plant_green", (0.18, 0.44, 0.14), roughness=0.70)
    create_mat("plant_green_lime", (0.32, 0.58, 0.18), roughness=0.65)
    create_mat("plant_banana_leaf", (0.22, 0.52, 0.15), roughness=0.60)
    create_mat("plant_banana_stem", (0.35, 0.55, 0.25), roughness=0.70)
    create_mat("plant_coconut", (0.30, 0.22, 0.10), roughness=0.80)
    create_mat("tree_trunk", (0.32, 0.20, 0.10), roughness=0.9)
    create_mat("flower_magenta", (0.85, 0.12, 0.45), roughness=0.5)
    create_mat("flower_yellow", (0.95, 0.80, 0.15), roughness=0.5)

    create_mat("paint_bucket", (0.85, 0.85, 0.82), roughness=0.5)
    create_mat("clothes_red", (0.80, 0.14, 0.14), roughness=0.9)
    create_mat("clothes_blue", (0.14, 0.32, 0.80), roughness=0.9)
    create_mat("clothes_yellow", (0.85, 0.75, 0.14), roughness=0.9)
    create_mat("lamp_bulb", (1.0, 0.95, 0.7), roughness=0.1, emission=(1.0, 0.95, 0.7), emission_strength=4.0)
    create_mat("teleport_cyan", (0.05, 0.85, 0.95), roughness=0.2, emission=(0.05, 0.85, 0.95), emission_strength=5.0)
    create_mat("motor_body_white", (0.85, 0.85, 0.85), roughness=0.3)
    create_mat("motor_body_red", (0.75, 0.10, 0.12), roughness=0.3)
    create_mat("motor_body_black", (0.10, 0.10, 0.12), roughness=0.4)
    create_mat("motor_tire", (0.08, 0.08, 0.08), roughness=0.9)
    create_mat("mattress_foam", (0.30, 0.45, 0.70), roughness=0.9)
    create_mat("pillow_white", (0.90, 0.90, 0.88), roughness=0.9)
    create_mat("laptop_dark", (0.12, 0.12, 0.14), roughness=0.4, metallic=0.5)
    create_mat("laptop_screen", (0.75, 0.85, 0.95), roughness=0.2, emission=(0.75, 0.85, 0.95), emission_strength=2.0)
    create_mat("tikar_mat", (0.70, 0.60, 0.40), roughness=0.9)

    # Food materials
    create_mat("dish_ayam_goreng", (0.42, 0.22, 0.08), roughness=0.8)
    create_mat("dish_telur_balado", (0.82, 0.14, 0.08), roughness=0.6)
    create_mat("dish_tempe_orek", (0.32, 0.16, 0.07), roughness=0.7)
    create_mat("dish_sayur_hijau", (0.14, 0.50, 0.12), roughness=0.7)
    create_mat("dish_mie_kuning", (0.85, 0.70, 0.18), roughness=0.7)
    create_mat("dish_sayur_lodeh", (0.82, 0.65, 0.32), roughness=0.5)
    create_mat("dish_ayam_bakar", (0.20, 0.10, 0.05), roughness=0.8)
    create_mat("dish_terong_balado", (0.60, 0.10, 0.22), roughness=0.6)
    create_mat("dish_sambal_ijo", (0.16, 0.55, 0.14), roughness=0.6)
    create_mat("kerupuk_kaleng_blue", (0.12, 0.35, 0.75), roughness=0.4, metallic=0.5)

    # ─── 2. GROUND, ROAD & STREET INFRASTRUCTURE ───
    add_box("World_Grass_Ground-col", (0.0, 3.0, -0.12), (90.0, 70.0, 0.15), "grass_lawn", "GangEnvironment")
    add_box("Gang_Road_Main-col", (-3.0, 0, -0.04), (60.0, 4.0, 0.08), "road_asphalt", "GangRoad")

    # Road Markings: Center Dashed White Line
    for xi in range(-25, 23, 3):
        add_box(f"Road_Center_Stripe_{xi}", (float(xi), 0.0, 0.003), (1.5, 0.12, 0.005), "road_marking_white", "GangRoad")

    # Low-Poly Asphalt Repair Patches (Characteristic Indonesian Gang)
    road_patches = [
        (-18.0, 0.6, 1.6, 0.9, "road_asphalt_dark"),
        (-11.5, -0.7, 2.0, 1.1, "road_asphalt_worn"),
        (-3.0, 0.8, 1.4, 0.8, "road_asphalt_dark"),
        (4.5, -0.5, 1.8, 1.0, "road_asphalt_worn"),
        (12.0, 0.4, 1.5, 0.9, "road_asphalt_dark"),
        (17.5, -0.6, 2.2, 1.1, "road_asphalt_worn")
    ]
    for pi, (px, py, pw, pl, pmat) in enumerate(road_patches):
        add_box(f"Road_Patch_{pi}", (px, py, 0.002), (pw, pl, 0.004), pmat, "GangRoad")

    # Two-Tone Alternating Curbs (Black & White Painted Curbs - Iconic Indonesian Gang)
    for i, curbx in enumerate(range(-30, 26, 2)):
        cmat = "curb_black" if i % 2 == 0 else "curb_white"
        # North curb
        add_box(f"Curb_N_{i}-col", (float(curbx), 2.05, 0.05), (2.0, 0.15, 0.10), cmat, "GangRoad")
        # South curb
        add_box(f"Curb_S_{i}-col", (float(curbx), -2.05, 0.05), (2.0, 0.15, 0.10), cmat, "GangRoad")

    # Drainage Gutters
    add_box("Gang_Drain_North", (-3.0, 1.94, -0.01), (60.0, 0.08, 0.04), "drain_trench", "GangRoad")
    add_box("Gang_Drain_South", (-3.0, -1.94, -0.01), (60.0, 0.08, 0.04), "drain_trench", "GangRoad")

    # Concrete Got Slabs (Penutup Got Selokan) with twin drainage slots
    for si, gx in enumerate([-22.0, -15.0, -8.0, 1.0, 8.0, 15.0]):
        # North slab
        add_box(f"Got_Slab_N_{si}", (gx, 1.94, 0.01), (1.2, 0.14, 0.03), "got_slab", "GangRoad")
        add_box(f"Got_Slot_N_{si}_1", (gx - 0.25, 1.94, 0.02), (0.20, 0.04, 0.02), "drain_trench", "GangRoad")
        add_box(f"Got_Slot_N_{si}_2", (gx + 0.25, 1.94, 0.02), (0.20, 0.04, 0.02), "drain_trench", "GangRoad")
        # South slab
        add_box(f"Got_Slab_S_{si}", (gx, -1.94, 0.01), (1.2, 0.14, 0.03), "got_slab", "GangRoad")
        add_box(f"Got_Slot_S_{si}_1", (gx - 0.25, -1.94, 0.02), (0.20, 0.04, 0.02), "drain_trench", "GangRoad")
        add_box(f"Got_Slot_S_{si}_2", (gx + 0.25, -1.94, 0.02), (0.20, 0.04, 0.02), "drain_trench", "GangRoad")

    # Speed Bumps (Polisi Tidur) with yellow/black hazard stripes
    for sbi, bx in enumerate([-12.0, 6.0]):
        add_box(f"Polisi_Tidur_{sbi}-col", (bx, 0.0, 0.04), (0.40, 3.8, 0.08), "kost_dark_grey", "GangRoad")
        for zi in range(-16, 17, 4):
            zy = zi * 0.1
            add_box(f"Polisi_Stripe_{sbi}_{zi}", (bx, zy, 0.045), (0.36, 0.20, 0.08), "warsun_yellow", "GangRoad")

    # ─── 3. KOST BUILDING FLOORS & TWO-TONE ARCHITECTURE ───
    # Courtyard Paving with paver divider bands
    add_box("Kost_Courtyard_Floor-col", (0.0, 8.35, 0.0), (7.0, 12.3, 0.08), "kost_floor_paving", "KostBuilding")
    for band_y in [4.2, 6.2, 8.3, 10.3, 12.4, 14.5]:
        add_box(f"Kost_Courtyard_Band_{band_y}", (0.0, band_y, 0.042), (7.0, 0.18, 0.005), "curb_concrete", "KostBuilding")

    for py in [4.5, 6.0, 7.5, 9.0]:
        add_box(f"Kost_Parking_Line_{py}", (1.5, py, 0.045), (2.4, 0.08, 0.01), "paint_bucket", "KostBuilding")

    add_box("Kost_L_Floor1-col", (-5.75, 10.1, 0.0), (4.5, 15.8, 0.1), "kost_floor_interior", "KostBuilding")
    add_box("Kost_R_Floor1-col", (5.75, 10.1, 0.0), (4.5, 15.8, 0.1), "kost_floor_interior", "KostBuilding")
    add_box("Kost_B_Floor1-col", (0.0, 16.25, 0.0), (16.0, 3.5, 0.1), "kost_floor_interior", "KostBuilding")

    # 2nd Floor slabs: CENTER Z=2.90, thickness 0.20 -> TOP SURFACE IS EXACTLY Z=3.00!
    add_box("Kost_L_Floor2-col", (-5.15, 10.1, 2.90), (5.7, 15.8, 0.20), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_R_Floor2-col", (5.15, 10.1, 2.90), (5.7, 15.8, 0.20), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_B_Floor2-col", (0.0, 16.25, 2.90), (16.0, 3.5, 0.20), "kost_concrete_grey", "KostBuilding")

    # Roof
    add_box("Kost_L_Roof-col", (-5.75, 10.1, 6.0), (4.7, 16.0, 0.2), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_R_Roof-col", (5.75, 10.1, 6.0), (4.7, 16.0, 0.2), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_B_Roof-col", (0.0, 16.25, 6.0), (16.2, 3.7, 0.2), "kost_concrete_grey", "KostBuilding")

    add_box("Kost_Parapet_L-col", (-8.05, 10.1, 6.4), (0.2, 16.0, 0.7), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_Parapet_R-col", (8.05, 10.1, 6.4), (0.2, 16.0, 0.7), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_Parapet_B-col", (0.0, 18.05, 6.4), (16.3, 0.2, 0.7), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_Parapet_FL-col", (-5.75, 2.15, 6.4), (4.7, 0.2, 0.7), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_Parapet_FR-col", (5.75, 2.15, 6.4), (4.7, 0.2, 0.7), "kost_concrete_grey", "KostBuilding")

    # Outer Walls
    add_box("Kost_L_OuterWall-col", (-8.05, 10.1, 3.0), (0.2, 15.8, 6.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_R_OuterWall-col", (8.05, 10.1, 3.0), (0.2, 15.8, 6.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_B_OuterWall-col", (0.0, 18.05, 3.0), (16.3, 0.2, 6.0), "kost_wall_white", "KostBuilding")

    # TWO-TONE WAINSCOTING (Lower 0.9m wall band + molding trim for rich low-poly aesthetics)
    # Left corridor wall
    add_box("Kost_L_Wainscot_F1", (-3.52, 8.35, 0.45), (0.04, 12.3, 0.90), "kost_wall_lower", "KostBuilding")
    add_box("Kost_L_Molding_F1", (-3.51, 8.35, 0.92), (0.05, 12.3, 0.05), "kost_wall_molding", "KostBuilding")
    add_box("Kost_L_Wainscot_F2", (-3.52, 8.35, 3.45), (0.04, 12.3, 0.90), "kost_wall_lower", "KostBuilding")
    add_box("Kost_L_Molding_F2", (-3.51, 8.35, 3.92), (0.05, 12.3, 0.05), "kost_wall_molding", "KostBuilding")

    # Right corridor wall
    add_box("Kost_R_Wainscot_F1", (3.52, 8.35, 0.45), (0.04, 12.3, 0.90), "kost_wall_lower", "KostBuilding")
    add_box("Kost_R_Molding_F1", (3.51, 8.35, 0.92), (0.05, 12.3, 0.05), "kost_wall_molding", "KostBuilding")
    add_box("Kost_R_Wainscot_F2", (3.52, 8.35, 3.45), (0.04, 12.3, 0.90), "kost_wall_lower", "KostBuilding")
    add_box("Kost_R_Molding_F2", (3.51, 8.35, 3.92), (0.05, 12.3, 0.05), "kost_wall_molding", "KostBuilding")

    # Plinth Skirting
    add_box("Kost_L_Plinth", (-3.52, 8.35, 0.12), (0.06, 12.3, 0.24), "wall_plinth_grey", "KostBuilding")
    add_box("Kost_R_Plinth", (3.52, 8.35, 0.12), (0.06, 12.3, 0.24), "wall_plinth_grey", "KostBuilding")

    # Front Wall Floor 1 Left (Player Street Window - CRYSTAL CLEAR GLASS)
    add_box("Kost_L_FrontWall_F1_L-col", (-7.2, 2.2, 1.5), (1.5, 0.2, 3.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_FrontWall_F1_R-col", (-4.3, 2.2, 1.5), (1.5, 0.2, 3.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_FrontWall_F1_Sill-col", (-5.75, 2.2, 0.5), (1.4, 0.2, 1.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_FrontWall_F1_Lintel-col", (-5.75, 2.2, 2.6), (1.4, 0.2, 0.8), "kost_wall_white", "KostBuilding")
    add_box("Player_WinStreet_Frame_Bottom", (-5.75, 2.2, 1.03), (1.42, 0.16, 0.06), "kost_dark_grey", "KostBuilding")
    add_box("Player_WinStreet_Frame_Top", (-5.75, 2.2, 2.17), (1.42, 0.16, 0.06), "kost_dark_grey", "KostBuilding")
    add_box("Player_WinStreet_Frame_L", (-6.42, 2.2, 1.6), (0.06, 0.16, 1.10), "kost_dark_grey", "KostBuilding")
    add_box("Player_WinStreet_Frame_R", (-5.08, 2.2, 1.6), (0.06, 0.16, 1.10), "kost_dark_grey", "KostBuilding")
    add_box("Player_WinStreet_Frame_Mid", (-5.75, 2.2, 1.6), (0.04, 0.16, 1.10), "kost_dark_grey", "KostBuilding")
    add_box("Player_Window_Street_Glass", (-5.75, 2.2, 1.6), (1.34, 0.02, 1.10), "window_glass_transparent", "KostBuilding")

    # Window Overhang Awning for Player Room Street Window
    add_window_awning("Player_WinStreet_Awning", (-5.75, 2.05, 2.30), (1.6, 0.65, 0.1), face_axis='Y', sign=-1)

    # Front Wall F2 Windows (Frosted/Blurred Privacy Glass)
    add_box("Kost_L_FrontWall_F2-col", (-5.75, 2.2, 4.5), (4.5, 0.2, 3.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_Window_F2_Frame", (-5.75, 2.15, 4.6), (1.2, 0.12, 1.2), "kost_dark_grey", "KostBuilding")
    add_box("Kost_L_Window_F2_Glass", (-5.75, 2.15, 4.6), (1.05, 0.05, 1.05), "glass_frosted", "KostBuilding")
    add_window_awning("Kost_L_WinF2_Awning", (-5.75, 2.05, 5.30), (1.4, 0.60, 0.1), face_axis='Y', sign=-1)

    add_box("Kost_R_FrontWall_F1-col", (5.75, 2.2, 1.5), (4.5, 0.2, 3.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_R_Window_F1_Frame", (5.75, 2.15, 1.6), (1.2, 0.12, 1.2), "kost_dark_grey", "KostBuilding")
    add_box("Kost_R_Window_F1_Glass", (5.75, 2.15, 1.6), (1.05, 0.05, 1.05), "glass_frosted", "KostBuilding")
    add_window_awning("Kost_R_WinF1_Awning", (5.75, 2.05, 2.30), (1.4, 0.60, 0.1), face_axis='Y', sign=-1)

    add_box("Kost_R_FrontWall_F2-col", (5.75, 2.2, 4.5), (4.5, 0.2, 3.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_R_Window_F2_Frame", (5.75, 2.15, 4.6), (1.2, 0.12, 1.2), "kost_dark_grey", "KostBuilding")
    add_box("Kost_R_Window_F2_Glass", (5.75, 2.15, 4.6), (1.05, 0.05, 1.05), "glass_frosted", "KostBuilding")
    add_window_awning("Kost_R_WinF2_Awning", (5.75, 2.05, 5.30), (1.4, 0.60, 0.1), face_axis='Y', sign=-1)

    add_box("Kost_L_Col_Front-col", (-7.9, 2.2, 3.0), (0.5, 0.4, 6.0), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_L_Col_Inner-col", (-3.6, 2.2, 3.0), (0.5, 0.4, 6.0), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_R_Col_Inner-col", (3.6, 2.2, 3.0), (0.5, 0.4, 6.0), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_R_Col_Front-col", (7.9, 2.2, 3.0), (0.5, 0.4, 6.0), "kost_concrete_grey", "KostBuilding")

    # Corridor Wall Left Floor 1 (Player Room Doorway & CRYSTAL CLEAR Courtyard Window)
    add_box("Kost_L_CorridorWall_F1_Front-col", (-3.55, 2.65, 1.5), (0.15, 0.9, 3.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_CorridorWall_F1_DoorLintel-col", (-3.55, 3.6, 2.55), (0.15, 1.0, 0.9), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_CorridorWall_F1_Mid-col", (-3.55, 4.35, 1.5), (0.15, 0.5, 3.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_CorridorWall_F1_WinSill-col", (-3.55, 5.2, 0.5), (0.15, 1.2, 1.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_CorridorWall_F1_WinLintel-col", (-3.55, 5.2, 2.6), (0.15, 1.2, 0.8), "kost_wall_white", "KostBuilding")
    add_box("Player_WinCourt_Frame_Bottom", (-3.55, 5.2, 1.03), (0.16, 1.22, 0.06), "kost_dark_grey", "KostBuilding")
    add_box("Player_WinCourt_Frame_Top", (-3.55, 5.2, 2.17), (0.16, 1.22, 0.06), "kost_dark_grey", "KostBuilding")
    add_box("Player_WinCourt_Frame_L", (-3.55, 4.63, 1.6), (0.16, 0.06, 1.10), "kost_dark_grey", "KostBuilding")
    add_box("Player_WinCourt_Frame_R", (-3.55, 5.77, 1.6), (0.16, 0.06, 1.10), "kost_dark_grey", "KostBuilding")
    add_box("Player_WinCourt_Frame_Mid", (-3.55, 5.2, 1.6), (0.16, 0.04, 1.10), "kost_dark_grey", "KostBuilding")
    add_box("Player_Window_Courtyard_Glass", (-3.55, 5.2, 1.6), (0.02, 1.14, 1.10), "window_glass_transparent", "KostBuilding")
    add_box("Kost_L_CorridorWall_F1_Post-col", (-3.55, 6.0, 1.5), (0.15, 0.4, 3.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_CorridorWall_F1_Back-col", (-3.55, 10.35, 1.5), (0.15, 8.3, 3.0), "kost_wall_white", "KostBuilding")

    add_box("Kost_L_CorridorWall_F2-col", (-3.55, 8.35, 4.5), (0.15, 12.3, 3.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_R_CorridorWall_F1-col", (3.55, 8.35, 1.5), (0.15, 12.3, 3.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_R_CorridorWall_F2-col", (3.55, 8.35, 4.5), (0.15, 12.3, 3.0), "kost_wall_white", "KostBuilding")

    # Partitions
    add_box("Kost_L_Partition_1-col", (-5.75, 6.2, 3.0), (4.4, 0.15, 6.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_Partition_2-col", (-5.75, 10.3, 3.0), (4.4, 0.15, 6.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_L_Partition_Back-col", (-5.75, 14.5, 3.0), (4.4, 0.15, 6.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_R_Partition_1-col", (5.75, 6.2, 3.0), (4.4, 0.15, 6.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_R_Partition_2-col", (5.75, 10.3, 3.0), (4.4, 0.15, 6.0), "kost_wall_white", "KostBuilding")
    add_box("Kost_R_Partition_Back-col", (5.75, 14.5, 3.0), (4.4, 0.15, 6.0), "kost_wall_white", "KostBuilding")

    # ─── OUTDOOR AC COMPRESSORS ON KOST EXTERIOR ───
    # Mounted on Left and Right outer walls
    add_ac_unit("AC_Kost_Player", (-8.25, 3.6, 2.2), face_axis='X', sign=-1, col_name="KostBuilding")
    add_ac_unit("AC_Kost_Room02", (-8.25, 8.2, 2.2), face_axis='X', sign=-1, col_name="KostBuilding")
    add_ac_unit("AC_Kost_Room03", (-8.25, 12.4, 2.2), face_axis='X', sign=-1, col_name="KostBuilding")
    add_ac_unit("AC_Kost_Room08", (-8.25, 8.2, 5.2), face_axis='X', sign=-1, col_name="KostBuilding")

    # ─── 4. UNIFIED ROOM DOORS, FROSTED WINDOWS, SHOE RACKS & DOORMATS ───
    def add_room_door(name_prefix, room_number_str, pos, is_right_wing=False):
        dx, dy, dz = pos
        inward_sign = -1.0 if is_right_wing else 1.0
        leaf_x = dx + inward_sign * 0.08
        jamb_x = dx + inward_sign * 0.07

        # 1. Door Frame Jambs
        add_box(f"{name_prefix}_Jamb_L", (jamb_x, dy - 0.46, dz + 1.05), (0.06, 0.05, 2.15), "wood_door_dark", "KostBuilding")
        add_box(f"{name_prefix}_Jamb_R", (jamb_x, dy + 0.46, dz + 1.05), (0.06, 0.05, 2.15), "wood_door_dark", "KostBuilding")
        add_box(f"{name_prefix}_Lintel", (jamb_x, dy, dz + 2.13), (0.06, 0.98, 0.06), "wood_door_dark", "KostBuilding")

        # 2. Teak Wood Door Leaf + Inset Bevel Panels
        add_box(f"{name_prefix}_Leaf", (leaf_x, dy, dz + 1.05), (0.035, 0.88, 2.08), "wood_door", "KostBuilding")
        add_box(f"{name_prefix}_Leaf_Bevel1", (leaf_x + inward_sign * 0.01, dy, dz + 0.65), (0.02, 0.68, 0.80), "wood_door_dark", "KostBuilding")
        add_box(f"{name_prefix}_Leaf_Bevel2", (leaf_x + inward_sign * 0.01, dy, dz + 1.55), (0.02, 0.68, 0.80), "wood_door_dark", "KostBuilding")

        # 3. Silver Metal Lever Handle
        hx = leaf_x + inward_sign * 0.03
        hy = dy + (-0.32 if not is_right_wing else 0.32)
        add_box(f"{name_prefix}_Handle_Plate", (hx, hy, dz + 1.0), (0.015, 0.06, 0.16), "kost_dark_grey", "KostBuilding")
        add_box(f"{name_prefix}_Handle", (hx + inward_sign * 0.015, hy, dz + 1.0), (0.03, 0.12, 0.03), "kost_railing_metal", "KostBuilding")

        # 4. Room Number Plate
        add_box(f"{name_prefix}_Plate_Border", (leaf_x, dy, dz + 2.25), (0.025, 0.28, 0.14), "kost_dark_grey", "KostBuilding")
        add_box(f"{name_prefix}_Plate", (leaf_x + inward_sign * 0.01, dy, dz + 2.25), (0.02, 0.24, 0.10), "warsun_yellow", "KostBuilding")

        # 5. Roster Air Vent
        add_box(f"{name_prefix}_Roster", (leaf_x, dy, dz + 2.45), (0.04, 0.65, 0.18), "roster_vent", "KostBuilding")

        # 6. Window beside door with FROSTED PRIVACY GLASS!
        wy = dy + 1.20
        add_box(f"{name_prefix}_Win_Sill", (jamb_x, wy, dz + 1.10), (0.08, 0.88, 0.05), "wood_door_dark", "KostBuilding")
        add_box(f"{name_prefix}_Win_Top", (jamb_x, wy, dz + 2.10), (0.07, 0.84, 0.05), "wood_door_dark", "KostBuilding")
        add_box(f"{name_prefix}_Win_Jamb_L", (jamb_x, wy - 0.40, dz + 1.60), (0.06, 0.05, 0.95), "wood_door_dark", "KostBuilding")
        add_box(f"{name_prefix}_Win_Jamb_R", (jamb_x, wy + 0.40, dz + 1.60), (0.06, 0.05, 0.95), "wood_door_dark", "KostBuilding")
        add_box(f"{name_prefix}_Win_Mullion", (jamb_x, wy, dz + 1.60), (0.05, 0.04, 0.95), "wood_door_dark", "KostBuilding")
        add_box(f"{name_prefix}_Win_Transom", (jamb_x, wy, dz + 1.60), (0.05, 0.76, 0.04), "wood_door_dark", "KostBuilding")
        add_box(f"{name_prefix}_Window_Glass", (leaf_x, wy, dz + 1.60), (0.02, 0.76, 0.95), "glass_frosted", "KostBuilding")
        add_box(f"{name_prefix}_Win_Roster", (leaf_x, wy, dz + 2.25), (0.04, 0.65, 0.16), "roster_vent", "KostBuilding")

        # 7. Low-Poly Doormat in front of door
        mat_col = "clothes_red" if int(room_number_str) % 3 == 0 else ("clothes_blue" if int(room_number_str) % 2 == 0 else "wall_tosca")
        add_doormat(f"Doormat_{name_prefix}", (dx + inward_sign * 0.42, dy, dz), mat_col, "KostBuilding")

    # Ground floor & 2nd floor room doors
    # Floor 1 Left
    add_room_door("Door_Room02", "02", (-3.50, 8.2, 0.0), is_right_wing=False)
    add_room_door("Door_Room03", "03", (-3.50, 12.4, 0.0), is_right_wing=False)
    # Floor 1 Right
    add_room_door("Door_Room04", "04", (3.50, 4.0, 0.0), is_right_wing=True)
    add_room_door("Door_Room05", "05", (3.50, 8.2, 0.0), is_right_wing=True)
    add_room_door("Door_Room06", "06", (3.50, 12.4, 0.0), is_right_wing=True)
    # Floor 2 Left
    add_room_door("Door_Room07", "07", (-3.50, 4.0, 3.0), is_right_wing=False)
    add_room_door("Door_Room08", "08", (-3.50, 8.2, 3.0), is_right_wing=False)
    add_room_door("Door_Room09", "09", (-3.50, 12.4, 3.0), is_right_wing=False)
    # Floor 2 Right
    add_room_door("Door_Room10", "10", (3.50, 4.0, 3.0), is_right_wing=True)
    add_room_door("Door_Room11", "11", (3.50, 8.2, 3.0), is_right_wing=True)
    add_room_door("Door_Room12", "12", (3.50, 12.4, 3.0), is_right_wing=True)

    # Doormat for User Room
    add_doormat("Doormat_UserRoom", (-3.10, 3.6, 0.0), "clothes_blue", "KostBuilding")

    # Low-Poly Shoe Racks outside rooms
    add_shoe_rack("ShoeRack_F1_L", (-3.10, 6.8, 0.0), "KostBuilding")
    add_shoe_rack("ShoeRack_F1_R", (3.10, 6.2, 0.0), "KostBuilding")
    add_shoe_rack("ShoeRack_F2_L", (-3.10, 6.2, 3.0), "KostBuilding")
    add_shoe_rack("ShoeRack_F2_R", (3.10, 6.2, 3.0), "KostBuilding")

    # ─── 5. STAIRCASE & SEAMLESS 2ND FLOOR LANDING ───
    for i in range(12):
        sy = 10.5 + (i + 0.5) * (4.0 / 12.0)
        sz = (i + 0.5) * (3.0 / 12.0)
        add_box(f"Kost_Stair_Step_{i}", (1.70, sy, sz), (1.20, 4.0 / 12.0, 3.0 / 12.0), "kost_concrete_grey", "KostBuilding")

    add_box("Kost_Stair_Landing_Slab", (1.70, 14.65, 2.95), (1.20, 0.35, 0.10), "kost_concrete_grey", "KostBuilding")

    add_angled_bar("Stair_Stringer_L", (1.08, 10.5, 0.15), (1.08, 14.5, 3.15), 0.06, 0.30, "kost_concrete_grey", "KostBuilding")
    add_angled_bar("Stair_Stringer_R", (2.32, 10.5, 0.15), (2.32, 14.5, 3.15), 0.06, 0.30, "kost_concrete_grey", "KostBuilding")

    for py in [10.5, 11.5, 12.5, 13.5, 14.5]:
        t = (py - 10.5) / 4.0
        base_z = t * 3.0
        add_cylinder(f"Stair_Post_{py}", (1.08, py, base_z + 0.45), 0.03, 0.90, "kost_railing_metal", "KostBuilding")

    add_angled_bar("Stair_Handrail_Top", (1.08, 10.5, 0.90), (1.08, 14.5, 3.90), 0.05, 0.05, "kost_railing_metal", "KostBuilding")
    add_angled_bar("Stair_Handrail_Mid", (1.08, 10.5, 0.45), (1.08, 14.5, 3.45), 0.03, 0.03, "kost_railing_metal", "KostBuilding")

    # 2nd Floor Railings
    for zr in [3.3, 3.6, 3.9]:
        add_box(f"Railing_L_Bar_{zr}", (-2.32, 8.35, zr), (0.04, 12.3, 0.04), "kost_railing_metal", "KostBuilding")
    for yp in [2.3, 5.0, 8.0, 11.0, 14.5]:
        add_box(f"Railing_L_Post_{yp}", (-2.32, yp, 3.5), (0.06, 0.06, 1.0), "kost_railing_metal", "KostBuilding")

    for zr in [3.3, 3.6, 3.9]:
        add_box(f"Railing_R_Bar_{zr}", (2.32, 6.35, zr), (0.04, 8.3, 0.04), "kost_railing_metal", "KostBuilding")
    for yp in [2.3, 5.0, 8.0, 10.5]:
        add_box(f"Railing_R_Post_{yp}", (2.32, yp, 3.5), (0.06, 0.06, 1.0), "kost_railing_metal", "KostBuilding")

    for zr in [3.3, 3.6, 3.9]:
        add_box(f"Railing_B_Bar_{zr}", (-0.62, 14.55, zr), (3.4, 0.04, 0.04), "kost_railing_metal", "KostBuilding")
    for xp in [-2.32, -1.0, 0.0, 1.08]:
        add_box(f"Railing_B_Post_{xp}", (xp, 14.55, 3.5), (0.06, 0.06, 1.0), "kost_railing_metal", "KostBuilding")

    # Rooftop Water Tower (4-legged steel lattice structure)
    add_box("Toren_Platform-col", (0.0, 16.2, 6.2), (2.0, 2.0, 0.2), "kost_dark_grey", "KostBuilding")
    for leg_x in [-0.85, 0.85]:
        for leg_y in [15.35, 17.05]:
            add_cylinder(f"Toren_Leg_{leg_x}_{leg_y}", (leg_x, leg_y, 6.8), 0.04, 1.2, "kost_railing_metal", "KostBuilding", vertices=6)
    add_box("Toren_Tower_Deck", (0.0, 16.2, 7.4), (1.9, 1.9, 0.08), "kost_dark_grey", "KostBuilding")
    add_cylinder("Toren_Tank", (0.0, 16.2, 8.4), 0.82, 1.9, "toren_orange", "KostBuilding", vertices=16)
    add_cylinder("Toren_Lid", (0.0, 16.2, 9.4), 0.45, 0.15, "kost_dark_grey", "KostBuilding")
    add_cylinder("Toren_Pipe_PVC", (0.8, 15.8, 5.0), 0.04, 5.0, "pvc_blue", "KostBuilding", vertices=6)

    # ─── 6. MONUMENTAL ENTRANCE PANEL "KOST WINDAH" WITH 3D TEXT ───
    add_box("Kost_Front_Wall-col", (5.75, 2.2, 0.8), (4.5, 0.25, 1.6), "kost_concrete_grey", "KostBuilding")

    add_box("Kost_Sign_Base-col", (0.0, 2.2, 0.08), (3.6, 0.30, 0.16), "kost_dark_grey", "KostBuilding")
    add_box("Kost_Front_Panel-col", (0.0, 2.2, 0.88), (3.3, 0.22, 1.44), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_Sign_TopCap", (0.0, 2.2, 1.63), (3.5, 0.26, 0.08), "kost_dark_grey", "KostBuilding")

    add_box("Kost_Sign_Plate_Front", (0.0, 2.07, 0.90), (3.0, 0.02, 1.15), "kost_dark_grey", "KostBuilding")
    add_box("Kost_Sign_Border_F_Top", (0.0, 2.05, 1.48), (3.04, 0.03, 0.04), "warsun_yellow", "KostBuilding")
    add_box("Kost_Sign_Border_F_Bot", (0.0, 2.05, 0.32), (3.04, 0.03, 0.04), "warsun_yellow", "KostBuilding")
    add_box("Kost_Sign_Border_F_L", (-1.50, 2.05, 0.90), (0.04, 0.03, 1.16), "warsun_yellow", "KostBuilding")
    add_box("Kost_Sign_Border_F_R", (1.50, 2.05, 0.90), (0.04, 0.03, 1.16), "warsun_yellow", "KostBuilding")

    add_box("Kost_Sign_Plate_Back", (0.0, 2.33, 0.90), (3.0, 0.02, 1.15), "kost_dark_grey", "KostBuilding")
    add_box("Kost_Sign_Border_B_Top", (0.0, 2.35, 1.48), (3.04, 0.03, 0.04), "warsun_yellow", "KostBuilding")
    add_box("Kost_Sign_Border_B_Bot", (0.0, 2.35, 0.32), (3.04, 0.03, 0.04), "warsun_yellow", "KostBuilding")
    add_box("Kost_Sign_Border_B_L", (-1.50, 2.35, 0.90), (0.04, 0.03, 1.16), "warsun_yellow", "KostBuilding")
    add_box("Kost_Sign_Border_B_R", (1.50, 2.35, 0.90), (0.04, 0.03, 1.16), "warsun_yellow", "KostBuilding")

    def create_3d_text(name, text, loc, rot_euler, size=0.28, extrude=0.04, mat_name="warsun_yellow", col_name="KostBuilding"):
        curve = bpy.data.curves.new(type="FONT", name=f"{name}_Curve")
        curve.body = text
        curve.size = size
        curve.extrude = extrude
        curve.align_x = 'CENTER'
        curve.align_y = 'CENTER'
        obj = bpy.data.objects.new(name, curve)
        obj.location = loc
        obj.rotation_euler = rot_euler
        col = get_col(col_name)
        col.objects.link(obj)
        mat = bpy.data.materials.get(mat_name)
        if mat:
            curve.materials.append(mat)
        return obj

    create_3d_text("Sign_Text_Kost_Windah_Front", "KOST WINDAH", (0.0, 2.04, 1.12), (math.radians(90), 0, 0), size=0.30, extrude=0.04)
    create_3d_text("Sign_Subtext_Front", "PUTRA & PUTRI", (0.0, 2.04, 0.72), (math.radians(90), 0, 0), size=0.14, extrude=0.02)
    create_3d_text("Sign_Text_Kost_Windah_Back", "KOST WINDAH", (0.0, 2.36, 1.12), (math.radians(90), 0, math.radians(180)), size=0.30, extrude=0.04)
    create_3d_text("Sign_Subtext_Back", "PUTRA & PUTRI", (0.0, 2.36, 0.72), (math.radians(90), 0, math.radians(180)), size=0.14, extrude=0.02)

    # ─── 7. REALISTIC PLAYER ROOM INTERIOR & PLN TOKEN METER ───
    add_box("Player_Kasur_Visual", (-7.1, 5.0, 0.08), (1.1, 1.9, 0.16), "mattress_foam", "KostRoom")
    add_box("Player_Bantal", (-7.1, 5.7, 0.20), (0.6, 0.35, 0.1), "pillow_white", "KostRoom")
    add_box("Player_Selimut", (-7.1, 4.4, 0.18), (0.9, 0.7, 0.06), "clothes_blue", "KostRoom")

    add_box("Player_Tikar", (-5.4, 4.5, 0.02), (1.8, 1.8, 0.01), "tikar_mat", "KostRoom")
    add_box("Player_Meja_Top-col", (-5.4, 5.8, 0.35), (1.1, 0.6, 0.04), "wood_light", "KostRoom")
    for lx in [-5.85, -4.95]:
        for ly in [5.55, 6.05]:
            add_box(f"Player_Meja_Leg_{lx}_{ly}-col", (lx, ly, 0.17), (0.06, 0.06, 0.32), "wood_light", "KostRoom")

    add_box("Player_Laptop_Base", (-5.4, 5.75, 0.38), (0.32, 0.24, 0.015), "laptop_dark", "KostRoom")
    add_box("Player_Laptop_Lid", (-5.4, 5.87, 0.50), (0.32, 0.015, 0.22), "laptop_dark", "KostRoom", rot=(math.radians(15), 0, 0))
    add_box("Player_Laptop_Screen", (-5.4, 5.86, 0.50), (0.29, 0.01, 0.19), "laptop_screen", "KostRoom", rot=(math.radians(15), 0, 0))

    # PLN Token Meter for Player Room
    add_box("Token_Meter_Box", (-3.46, 2.7, 1.55), (0.05, 0.22, 0.32), "paint_bucket", "KostBuilding")
    add_box("Token_Meter_Screen", (-3.43, 2.7, 1.63), (0.015, 0.12, 0.06), "plant_green", "KostBuilding")
    add_box("Token_Meter_Keypad", (-3.43, 2.7, 1.50), (0.015, 0.14, 0.10), "kost_dark_grey", "KostBuilding")
    add_box("Token_Meter_LED", (-3.43, 2.76, 1.63), (0.015, 0.02, 0.02), "clothes_red", "KostBuilding")
    add_box("Token_Meter_Breaker", (-3.43, 2.7, 1.41), (0.02, 0.04, 0.04), "pvc_blue", "KostBuilding")

    # ─── 8. WC UMUM (FULLY ENCLOSED, REAL CERAMIC TUB & KLOSET) ───
    add_box("WC_Wall_Divider-col", (-1.45, 16.25, 1.5), (0.15, 3.5, 3.0), "wc_tile_white", "KostWC")
    add_box("Kost_B_BackWall_Ground-col", (-0.18, 14.5, 1.5), (2.54, 0.15, 3.0), "kost_wall_white", "KostBuilding")
    add_box("WC_FrontWall_L-col", (-3.125, 14.5, 1.5), (0.85, 0.15, 3.0), "wc_tile_white", "KostWC")
    add_box("WC_FrontWall_R-col", (-1.50, 14.5, 1.5), (0.10, 0.15, 3.0), "wc_tile_white", "KostWC")
    add_box("WC_FrontWall_Lintel-col", (-2.125, 14.5, 2.55), (1.15, 0.15, 0.90), "wc_tile_white", "KostWC")

    add_box("WC_Door_Frame_L", (-2.69, 14.47, 1.05), (0.06, 0.12, 2.15), "kost_dark_grey", "KostWC")
    add_box("WC_Door_Frame_R", (-1.56, 14.47, 1.05), (0.06, 0.12, 2.15), "kost_dark_grey", "KostWC")
    add_box("WC_Door_Frame_Top", (-2.125, 14.47, 2.12), (1.19, 0.12, 0.06), "kost_dark_grey", "KostWC")

    # Bak Mandi
    add_box("WC_BakMandi_Bottom-col", (-1.90, 17.20, 0.05), (0.84, 1.20, 0.10), "wc_tile_white", "KostWC")
    add_box("WC_BakMandi_Wall_Front-col", (-1.90, 16.64, 0.45), (0.84, 0.08, 0.70), "wc_tile_white", "KostWC")
    add_box("WC_BakMandi_Wall_Back-col", (-1.90, 17.76, 0.45), (0.84, 0.08, 0.70), "wc_tile_white", "KostWC")
    add_box("WC_BakMandi_Wall_Left-col", (-2.28, 17.20, 0.45), (0.08, 1.04, 0.70), "wc_tile_white", "KostWC")
    add_box("WC_BakMandi_Wall_Right-col", (-1.52, 17.20, 0.45), (0.08, 1.04, 0.70), "wc_tile_white", "KostWC")
    add_box("WC_Water_Surface", (-1.90, 17.20, 0.62), (0.68, 1.04, 0.02), "wc_water", "KostWC")

    add_cylinder("WC_Gayung_Cup", (-2.15, 16.64, 0.86), 0.09, 0.12, "pvc_blue", "KostWC")
    add_box("WC_Gayung_Handle", (-2.28, 16.64, 0.88), (0.18, 0.03, 0.03), "pvc_blue", "KostWC")

    add_cylinder("WC_Kran_Pipe", (-1.90, 17.85, 1.05), 0.02, 0.15, "stainless_tray", "KostWC", rot=(math.radians(90), 0, 0))
    add_cylinder("WC_Kran_Spout", (-1.90, 17.75, 0.98), 0.015, 0.12, "stainless_tray", "KostWC")

    # Kloset Jongkok
    add_box("WC_Kloset_Base-col", (-2.95, 16.3, 0.08), (0.80, 0.95, 0.16), "wc_tile_white", "KostWC")
    add_box("WC_Kloset_Bowl", (-2.95, 16.3, 0.14), (0.30, 0.48, 0.04), "kost_dark_grey", "KostWC")
    add_cylinder("WC_Kloset_Drain", (-2.95, 16.45, 0.10), 0.06, 0.06, "kost_dark_grey", "KostWC")
    add_box("WC_FootTread_L", (-3.20, 16.3, 0.17), (0.15, 0.44, 0.02), "curb_concrete", "KostWC")
    add_box("WC_FootTread_R", (-2.70, 16.3, 0.17), (0.15, 0.44, 0.02), "curb_concrete", "KostWC")
    for gy in [16.15, 16.25, 16.35, 16.45]:
        add_box(f"WC_Grip_L_{gy}", (-3.20, gy, 0.182), (0.12, 0.02, 0.005), "kost_dark_grey", "KostWC")
        add_box(f"WC_Grip_R_{gy}", (-2.70, gy, 0.182), (0.12, 0.02, 0.005), "kost_dark_grey", "KostWC")

    add_cylinder("WC_Bidet_Kran", (-3.48, 16.0, 0.65), 0.02, 0.10, "stainless_tray", "KostWC", rot=(0, math.radians(90), 0))
    add_cylinder("WC_Bidet_Hose", (-3.44, 16.0, 0.40), 0.015, 0.45, "pvc_blue", "KostWC")
    add_box("WC_Lampu_Bulb", (-2.45, 16.25, 2.7), (0.08, 0.08, 0.08), "lamp_bulb", "KostWC")

    # Communal Wash Area
    add_box("Dapur_Meja_Wastafel-col", (-0.15, 17.2, 0.45), (1.8, 0.7, 0.9), "kost_concrete_grey", "KostBuilding")
    add_box("Dapur_Wastafel_Bowl", (-0.45, 17.15, 0.88), (0.50, 0.40, 0.06), "stainless_tray", "KostBuilding")
    add_cylinder("Dapur_Kran_Wastafel", (-0.45, 17.38, 1.05), 0.015, 0.20, "stainless_tray", "KostBuilding")
    add_cylinder("Dapur_Galon_Air", (0.45, 17.2, 1.25), 0.18, 0.45, "pvc_blue", "KostBuilding")
    add_box("Dapur_Dispenser-col", (0.45, 17.2, 0.95), (0.35, 0.35, 0.3), "paint_bucket", "KostBuilding")

    # ─── 9. MOTORBIKES ───
    def make_motorbike_x_aligned(name, pos, body_mat):
        mx, my, mz = pos
        add_cylinder(f"{name}_Wheel_F", (mx + 0.55, my, mz + 0.25), 0.25, 0.08, "motor_tire", "KostBuilding", rot=(math.radians(90), 0, 0))
        add_cylinder(f"{name}_Wheel_R", (mx - 0.55, my, mz + 0.25), 0.25, 0.08, "motor_tire", "KostBuilding", rot=(math.radians(90), 0, 0))
        add_box(f"{name}_Chassis-col", (mx, my, mz + 0.4), (1.1, 0.35, 0.35), body_mat, "KostBuilding")
        add_box(f"{name}_Seat", (mx - 0.15, my, mz + 0.62), (0.65, 0.32, 0.10), "kost_dark_grey", "KostBuilding")
        add_box(f"{name}_Headlight", (mx + 0.52, my, mz + 0.78), (0.18, 0.35, 0.22), body_mat, "KostBuilding")
        add_box(f"{name}_Handlebars", (mx + 0.50, my, mz + 0.88), (0.05, 0.65, 0.05), "kost_dark_grey", "KostBuilding")
        add_box(f"{name}_Mirror_L", (mx + 0.48, my + 0.28, mz + 0.98), (0.04, 0.08, 0.06), "kost_dark_grey", "KostBuilding")
        add_box(f"{name}_Mirror_R", (mx + 0.48, my - 0.28, mz + 0.98), (0.04, 0.08, 0.06), "kost_dark_grey", "KostBuilding")
        add_cylinder(f"{name}_Exhaust", (mx - 0.2, my - 0.20, mz + 0.22), 0.04, 0.6, "kost_dark_grey", "KostBuilding", rot=(0, math.radians(90), 0))
        add_box(f"{name}_Kickstand", (mx - 0.1, my + 0.18, mz + 0.12), (0.04, 0.04, 0.24), "kost_dark_grey", "KostBuilding")

    make_motorbike_x_aligned("Motor_White", (1.5, 5.25, 0.0), "motor_body_white")
    make_motorbike_x_aligned("Motor_Black", (1.5, 6.75, 0.0), "motor_body_black")
    make_motorbike_x_aligned("Motor_Red", (1.5, 8.25, 0.0), "motor_body_red")

    # ─── 10. WARSUN BAHARI ───
    add_box("Warsun_Floor-col", (13.0, 6.35, 0.05), (9.0, 8.3, 0.1), "warsun_tile_floor", "WarsunBuilding")
    add_box("Warsun_BackWall-col", (13.0, 10.55, 1.8), (9.2, 0.2, 3.6), "warsun_orange", "WarsunBuilding")
    add_box("Warsun_RightWall-col", (17.55, 6.35, 1.8), (0.2, 8.4, 3.6), "warsun_orange", "WarsunBuilding")
    add_box("Warsun_LeftWall-col", (8.45, 6.35, 1.8), (0.2, 8.4, 3.6), "kost_wall_white", "WarsunBuilding")
    add_box("Warsun_Roof-col", (13.0, 6.35, 3.75), (9.4, 8.8, 0.25), "tin_roof", "WarsunBuilding")
    add_box("Warsun_Canopy-col", (13.0, 2.2, 3.1), (9.2, 2.0, 0.1), "tin_roof", "WarsunBuilding")
    add_cylinder("Warsun_Post_L", (8.6, 1.3, 1.5), 0.05, 3.0, "kost_dark_grey", "WarsunBuilding")
    add_cylinder("Warsun_Post_R", (17.4, 1.3, 1.5), 0.05, 3.0, "kost_dark_grey", "WarsunBuilding")
    
    add_box("Warsun_Banner", (13.0, 2.15, 3.2), (8.8, 0.06, 0.8), "warsun_yellow", "WarsunBuilding")
    add_box("Warsun_Banner_Accent", (13.0, 2.12, 3.45), (8.6, 0.04, 0.2), "warsun_orange", "WarsunBuilding")

    add_box("Warsun_Counter_Long-col", (13.5, 5.5, 0.5), (5.4, 0.8, 1.0), "kost_wall_white", "WarsunBuilding")
    add_box("Warsun_Counter_Trim_Long", (13.5, 5.08, 0.98), (5.5, 0.08, 0.06), "warsun_orange", "WarsunBuilding")
    add_box("Warsun_Counter_Short-col", (10.5, 7.0, 0.5), (0.9, 2.2, 1.0), "kost_wall_white", "WarsunBuilding")
    add_box("Warsun_Counter_Trim_Short", (10.02, 7.0, 0.98), (0.12, 2.3, 0.06), "warsun_orange", "WarsunBuilding")

    add_box("Warsun_Showcase_Glass_Front", (13.5, 5.12, 1.4), (4.96, 0.02, 0.76), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warsun_Showcase_Glass_Top", (13.5, 5.5, 1.79), (4.96, 0.76, 0.02), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warsun_Showcase_Glass_L", (11.02, 5.5, 1.4), (0.02, 0.76, 0.76), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warsun_Showcase_Glass_R", (15.98, 5.5, 1.4), (0.02, 0.76, 0.76), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warsun_Showcase_Shelf", (13.5, 5.5, 1.38), (4.92, 0.72, 0.02), "glass_showcase_transparent", "WarsunBuilding")

    for cx in [11.02, 15.98]:
        for cy in [5.12, 5.88]:
            add_box(f"Warsun_Showcase_Post_{cx}_{cy}", (cx, cy, 1.4), (0.03, 0.03, 0.8), "kost_railing_metal", "WarsunBuilding")
    add_box("Warsun_Showcase_Bar_FT", (13.5, 5.12, 1.79), (5.0, 0.03, 0.03), "kost_railing_metal", "WarsunBuilding")
    add_box("Warsun_Showcase_Bar_FB", (13.5, 5.12, 1.01), (5.0, 0.03, 0.03), "kost_railing_metal", "WarsunBuilding")
    add_box("Warsun_Showcase_Bar_BT", (13.5, 5.88, 1.79), (5.0, 0.03, 0.03), "kost_railing_metal", "WarsunBuilding")
    add_box("Warsun_Showcase_Bar_LT", (11.02, 5.5, 1.79), (0.03, 0.76, 0.03), "kost_railing_metal", "WarsunBuilding")
    add_box("Warsun_Showcase_Bar_RT", (15.98, 5.5, 1.79), (0.03, 0.76, 0.03), "kost_railing_metal", "WarsunBuilding")

    # Stainless Food Trays
    food_dishes_lower = ["dish_ayam_goreng", "dish_telur_balado", "dish_tempe_orek", "dish_sayur_hijau", "dish_mie_kuning"]
    food_dishes_upper = ["dish_sayur_lodeh", "dish_ayam_bakar", "dish_terong_balado", "dish_sambal_ijo", "dish_ayam_goreng"]
    for i, dx in enumerate([11.5, 12.5, 13.5, 14.5, 15.5]):
        add_box(f"Warsun_Tray_L_{i}", (dx, 5.5, 1.03), (0.85, 0.60, 0.04), "stainless_tray", "WarsunBuilding")
        add_box(f"Warsun_Food_L_{i}", (dx, 5.5, 1.06), (0.80, 0.55, 0.05), food_dishes_lower[i], "WarsunBuilding")
        add_box(f"Warsun_Tray_U_{i}", (dx, 5.5, 1.40), (0.85, 0.60, 0.04), "stainless_tray", "WarsunBuilding")
        add_box(f"Warsun_Food_U_{i}", (dx, 5.5, 1.43), (0.80, 0.55, 0.05), food_dishes_upper[i], "WarsunBuilding")

    add_box("Warsun_Dine_Table-col", (13.5, 3.6, 0.75), (5.4, 0.9, 0.06), "wood_light", "WarsunBuilding")
    for lx in [11.0, 16.0]:
        for ly in [3.25, 3.95]:
            add_box(f"Warsun_Table_Leg_{lx}_{ly}-col", (lx, ly, 0.36), (0.08, 0.08, 0.72), "kost_dark_grey", "WarsunBuilding")
    add_box("Warsun_Bench_Front-col", (13.5, 2.7, 0.45), (5.0, 0.35, 0.05), "warsun_orange", "WarsunBuilding")
    for bx in [11.2, 13.5, 15.8]:
        add_box(f"Warsun_Bench_F_Leg_{bx}-col", (bx, 2.7, 0.22), (0.06, 0.30, 0.44), "kost_dark_grey", "WarsunBuilding")
    add_box("Warsun_Bench_Side_A-col", (13.5, 7.8, 0.23), (4.6, 0.35, 0.46), "warsun_orange", "WarsunBuilding")
    add_box("Warsun_Bench_Side_B-col", (13.5, 9.2, 0.23), (4.6, 0.35, 0.46), "warsun_orange", "WarsunBuilding")
    
    add_cylinder("Warsun_Kerupuk_Kaleng", (11.5, 3.6, 0.95), 0.22, 0.45, "kerupuk_kaleng_blue", "WarsunBuilding")
    add_box("Warsun_Kerupuk_Window", (11.5, 3.39, 0.95), (0.24, 0.02, 0.24), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warsun_Tisu_Dispenser", (13.5, 3.6, 0.84), (0.2, 0.2, 0.15), "paint_bucket", "WarsunBuilding")
    add_cylinder("Warsun_Teko_Air", (15.2, 3.6, 0.9), 0.12, 0.25, "stainless_tray", "WarsunBuilding")
    for i, sx in enumerate([11.5, 12.5, 13.5, 14.5, 15.5]):
        add_box(f"Warsun_Sachet_Strip_{i}", (sx, 10.42, 2.2), (0.25, 0.03, 1.2), "warsun_yellow", "WarsunBuilding")
    add_cylinder("Warsun_WallFan_Base", (17.42, 5.5, 2.5), 0.12, 0.04, "kost_dark_grey", "WarsunBuilding", rot=(0, math.radians(90), 0))
    add_cylinder("Warsun_WallFan_Cage", (17.2, 5.5, 2.5), 0.3, 0.1, "kost_dark_grey", "WarsunBuilding", rot=(0, math.radians(90), 0))

    # ─── 11. GANG HOUSES (TWO-TONE WALLS, AWNINGS, AC, KWH METERS & RICH LOW-POLY DETAILS) ───
    def add_house_entrance(name_prefix, door_center, win_centers, face_axis='Y', sign=-1):
        dx, dy, dz = door_center
        if face_axis == 'Y':
            add_box(f"{name_prefix}_Door_Frame_L", (dx - 0.48, dy, dz + 1.05), (0.06, 0.08, 2.15), "kost_dark_grey", "GangHouses")
            add_box(f"{name_prefix}_Door_Frame_R", (dx + 0.48, dy, dz + 1.05), (0.06, 0.08, 2.15), "kost_dark_grey", "GangHouses")
            add_box(f"{name_prefix}_Door_Frame_Top", (dx, dy, dz + 2.15), (1.02, 0.08, 0.06), "kost_dark_grey", "GangHouses")
            add_box(f"{name_prefix}_Door_Leaf", (dx, dy + sign * 0.02, dz + 1.05), (0.90, 0.04, 2.08), "wood_door", "GangHouses")
            add_box(f"{name_prefix}_Door_Knob", (dx + 0.35, dy + sign * 0.05, dz + 1.05), (0.05, 0.05, 0.05), "kost_railing_metal", "GangHouses")
            add_box(f"{name_prefix}_Door_Roster", (dx, dy + sign * 0.02, dz + 2.30), (0.65, 0.04, 0.18), "roster_vent", "GangHouses")
            # Doormat at house entrance
            add_doormat(f"Doormat_{name_prefix}", (dx, dy + sign * 0.35, dz), "clothes_red", "GangHouses")

            # Windows + Overhang Awnings
            for idx, (wx, wy, wz, w_w, w_h) in enumerate(win_centers):
                add_box(f"{name_prefix}_Win_Sill_{idx}", (wx, wy, wz - w_h/2.0), (w_w + 0.08, 0.10, 0.05), "kost_dark_grey", "GangHouses")
                add_box(f"{name_prefix}_Win_Top_{idx}", (wx, wy, wz + w_h/2.0), (w_w + 0.08, 0.08, 0.05), "kost_dark_grey", "GangHouses")
                add_box(f"{name_prefix}_Win_Jamb_L_{idx}", (wx - w_w/2.0, wy, wz), (0.05, 0.08, w_h), "kost_dark_grey", "GangHouses")
                add_box(f"{name_prefix}_Win_Jamb_R_{idx}", (wx + w_w/2.0, wy, wz), (0.05, 0.08, w_h), "kost_dark_grey", "GangHouses")
                add_box(f"{name_prefix}_Win_Mullion_{idx}", (wx, wy, wz), (0.04, 0.06, w_h), "kost_dark_grey", "GangHouses")
                add_box(f"{name_prefix}_Window_Glass_{idx}", (wx, wy + sign * 0.02, wz), (w_w - 0.08, 0.02, w_h - 0.08), "glass_frosted", "GangHouses")
                add_box(f"{name_prefix}_Win_Roster_{idx}", (wx, wy + sign * 0.02, wz + w_h/2.0 + 0.15), (w_w - 0.10, 0.04, 0.16), "roster_vent", "GangHouses")
                # Window Awning
                add_window_awning(f"{name_prefix}_WinAwning_{idx}", (wx, wy, wz + w_h/2.0 + 0.12), (w_w + 0.20, 0.55, 0.08), face_axis='Y', sign=sign, col_name="GangHouses")

    # HOUSE 1: 2-Story Residence with Proper Functional Balcony!
    add_box("House1_FrontLawn-col", (-1.5, -3.8, 0.02), (7.8, 3.0, 0.05), "grass_lawn", "GangHouses")
    for step_y in [-2.8, -3.5, -4.2, -4.9]:
        add_box(f"House1_Step_{step_y}", (0.8, step_y, 0.05), (0.7, 0.45, 0.03), "kost_concrete_grey", "GangHouses")
    add_box("House1_Fence_Wall_L-col", (-3.5, -2.25, 0.5), (3.8, 0.12, 1.0), "iron_fence_black", "GangHouses")
    add_box("House1_Fence_Wall_R-col", (1.6, -2.25, 0.5), (1.6, 0.12, 1.0), "iron_fence_black", "GangHouses")
    add_box("House1_Gate_Post_L-col", (0.0, -2.25, 0.6), (0.2, 0.2, 1.2), "kost_concrete_grey", "GangHouses")
    add_box("House1_Gate_Post_R-col", (1.0, -2.25, 0.6), (0.2, 0.2, 1.2), "kost_concrete_grey", "GangHouses")
    add_box("House1_Iron_Gate", (0.5, -2.25, 0.5), (0.9, 0.04, 1.0), "kost_railing_metal", "GangHouses")

    # Main Building & Two-Tone Wainscoting
    add_box("House1_Main_Building-col", (-1.5, -7.8, 2.6), (7.6, 5.6, 5.2), "kost_wall_white", "GangHouses")
    add_box("House1_Wainscot_F1", (-1.5, -4.96, 0.55), (7.64, 0.06, 1.10), "wall_h1_lower", "GangHouses")
    add_box("House1_Molding_F1", (-1.5, -4.95, 1.12), (7.66, 0.08, 0.05), "kost_wall_molding", "GangHouses")
    add_box("House1_Plinth", (-1.5, -4.96, 0.14), (7.68, 0.08, 0.28), "wall_plinth_grey", "GangHouses")

    # Roof & Eaves
    add_box("House1_Roof-col", (-1.5, -7.8, 5.3), (8.0, 6.0, 0.4), "tile_roof_brown", "GangHouses")
    add_box("House1_Roof_Ridge", (-1.5, -7.8, 5.52), (8.1, 0.25, 0.12), "roof_ridge_dark", "GangHouses")

    # Ground Floor Entrance
    add_house_entrance("House1_GF", (0.8, -4.96, 0.0), [(-2.6, -4.96, 1.35, 2.6, 1.3)], face_axis='Y', sign=1)
    add_kwh_meter("House1_KWH", (1.6, -4.96, 1.5), face_axis='Y', sign=1, col_name="GangHouses")
    add_ac_unit("House1_AC", (-4.2, -4.96, 2.3), face_axis='Y', sign=1, col_name="GangHouses")

    # House 1 2nd Floor Balcony: REAL FORWARD-PROJECTING BALCONY SLAB!
    add_box("House1_Balcony_Floor-col", (-1.5, -4.30, 2.85), (6.0, 1.40, 0.18), "kost_concrete_grey", "GangHouses")
    for corbel_x in [-4.0, -1.5, 1.0]:
        add_box(f"House1_Balcony_Corbel_{corbel_x}", (corbel_x, -4.40, 2.35), (0.18, 1.10, 0.80), "kost_concrete_grey", "GangHouses")

    for rz in [3.15, 3.45, 3.75]:
        add_box(f"House1_Balcony_Rail_Front_{rz}", (-1.5, -3.65, rz), (5.9, 0.04, 0.04), "kost_railing_metal", "GangHouses")
    for px in [-4.45, -1.5, 1.45]:
        add_box(f"House1_Balcony_Post_{px}", (px, -3.65, 3.45), (0.05, 0.05, 0.90), "kost_railing_metal", "GangHouses")
    for rz in [3.15, 3.45, 3.75]:
        add_box(f"House1_Balcony_Rail_L_{rz}", (-4.45, -4.32, rz), (0.04, 1.30, 0.04), "kost_railing_metal", "GangHouses")
        add_box(f"House1_Balcony_Rail_R_{rz}", (1.45, -4.32, rz), (0.04, 1.30, 0.04), "kost_railing_metal", "GangHouses")

    # 2nd Floor Balcony Access Doors & Window
    add_box("House1_Balcony_Door_Frame", (0.5, -4.96, 3.95), (1.40, 0.08, 2.10), "kost_dark_grey", "GangHouses")
    add_box("House1_Balcony_Door_L", (0.2, -4.94, 3.95), (0.58, 0.04, 2.02), "wood_door", "GangHouses")
    add_box("House1_Balcony_Door_R", (0.8, -4.94, 3.95), (0.58, 0.04, 2.02), "wood_door", "GangHouses")
    add_box("House1_Balcony_Door_Glass_L", (0.2, -4.93, 3.95), (0.44, 0.02, 1.50), "glass_frosted", "GangHouses")
    add_box("House1_Balcony_Door_Glass_R", (0.8, -4.93, 3.95), (0.44, 0.02, 1.50), "glass_frosted", "GangHouses")
    add_box("House1_Balcony_Win_Frame", (-2.6, -4.96, 4.05), (2.0, 0.08, 1.20), "kost_dark_grey", "GangHouses")
    add_box("House1_Balcony_Win_Glass", (-2.6, -4.94, 4.05), (1.86, 0.02, 1.06), "glass_frosted", "GangHouses")

    # HOUSE 2: Tosca House with brick accent wall, two-tone wainscoting, and TV Antenna
    add_box("House2_Main_Building-col", (-10.5, -7.0, 1.8), (8.8, 6.8, 3.6), "wall_tosca", "GangHouses")
    add_box("House2_Wainscot", (-10.5, -3.56, 0.50), (8.84, 0.06, 1.00), "wall_tosca_lower", "GangHouses")
    add_box("House2_Molding", (-10.5, -3.55, 1.02), (8.86, 0.08, 0.05), "kost_wall_molding", "GangHouses")
    add_box("House2_Plinth", (-10.5, -3.56, 0.14), (8.84, 0.08, 0.28), "wall_plinth_grey", "GangHouses")
    add_box("House2_SideBrickWall-col", (-5.95, -7.0, 1.8), (0.25, 6.8, 3.6), "brick_red", "GangHouses")
    add_box("House2_Roof-col", (-10.5, -7.0, 3.9), (9.2, 7.2, 0.8), "tile_roof_brown", "GangHouses")
    add_box("House2_Roof_Ridge", (-10.5, -7.0, 4.35), (9.3, 0.25, 0.12), "roof_ridge_dark", "GangHouses")
    add_tv_antenna("House2_Antenna", (-7.5, -7.0, 4.3), height=2.2, col_name="GangHouses")
    add_kwh_meter("House2_KWH", (-7.2, -3.56, 1.5), face_axis='Y', sign=1, col_name="GangHouses")

    add_house_entrance("House2", (-8.5, -3.56, 0.0), [(-11.5, -3.56, 1.4, 1.4, 1.1)], face_axis='Y', sign=1)
    add_box("House2_Awning-col", (-8.5, -3.2, 2.4), (5.0, 1.8, 0.06), "tin_roof", "GangHouses")
    add_cylinder("House2_Awning_Post_L", (-10.8, -2.4, 1.2), 0.04, 2.4, "kost_dark_grey", "GangHouses")
    add_cylinder("House2_Awning_Post_R", (-6.2, -2.4, 1.2), 0.04, 2.4, "kost_dark_grey", "GangHouses")
    add_box("House2_Chair_1-col", (-8.0, -3.2, 0.4), (0.5, 0.5, 0.45), "wood_light", "GangHouses")
    add_box("House2_Chair_2-col", (-9.0, -3.2, 0.4), (0.5, 0.5, 0.45), "wood_light", "GangHouses")
    add_box("House2_Low_Wall_L-col", (-12.8, -2.3, 0.6), (4.2, 0.15, 1.2), "kost_concrete_grey", "GangHouses")
    add_box("House2_Iron_Gate", (-10.2, -2.3, 0.6), (1.2, 0.04, 1.2), "kost_dark_grey", "GangHouses")
    add_box("House2_Low_Wall_R-col", (-8.0, -2.3, 0.6), (3.0, 0.15, 1.2), "kost_concrete_grey", "GangHouses")
    add_box("House2_Jemuran_Frame_L", (-6.8, -2.5, 0.65), (0.03, 0.6, 1.3), "kost_railing_metal", "GangHouses")
    add_box("House2_Jemuran_Frame_R", (-5.2, -2.5, 0.65), (0.03, 0.6, 1.3), "kost_railing_metal", "GangHouses")
    add_box("House2_Jemuran_Baju_Red", (-6.3, -2.5, 0.75), (0.45, 0.03, 0.6), "clothes_red", "GangHouses")
    add_box("House2_Jemuran_Handuk_Blue", (-5.8, -2.5, 0.70), (0.45, 0.03, 0.7), "clothes_blue", "GangHouses")
    add_box("House2_Jemuran_Baju_Yellow", (-5.4, -2.5, 0.75), (0.35, 0.03, 0.55), "clothes_yellow", "GangHouses")

    # HOUSE 3: Warm Yellow House with two-tone wainscoting & picket fence
    add_box("House3_Main_Building-col", (8.0, -7.0, 1.8), (9.0, 6.8, 3.6), "wall_yellow", "GangHouses")
    add_box("House3_Wainscot", (8.0, -3.56, 0.50), (9.04, 0.06, 1.00), "wall_yellow_lower", "GangHouses")
    add_box("House3_Molding", (8.0, -3.55, 1.02), (9.06, 0.08, 0.05), "kost_wall_molding", "GangHouses")
    add_box("House3_Plinth", (8.0, -3.56, 0.14), (9.04, 0.08, 0.28), "wall_plinth_grey", "GangHouses")
    add_box("House3_Roof-col", (8.0, -7.0, 3.9), (9.4, 7.2, 0.8), "tin_roof", "GangHouses")
    add_box("House3_Roof_Ridge", (8.0, -7.0, 4.35), (9.5, 0.25, 0.12), "roof_ridge_dark", "GangHouses")
    add_tv_antenna("House3_Antenna", (10.0, -7.0, 4.3), height=2.0, col_name="GangHouses")
    add_kwh_meter("House3_KWH", (5.4, -3.56, 1.5), face_axis='Y', sign=1, col_name="GangHouses")

    add_house_entrance("House3", (6.5, -3.56, 0.0), [(4.8, -3.56, 1.4, 1.2, 1.1), (9.5, -3.56, 1.4, 1.2, 1.1)], face_axis='Y', sign=1)
    add_box("House3_Yard-col", (8.0, -3.5, 0.02), (8.8, 2.4, 0.05), "kost_floor_paving", "GangHouses")
    add_box("House3_Picket_Fence_L-col", (5.2, -2.25, 0.4), (3.6, 0.08, 0.8), "wood_light", "GangHouses")
    add_box("House3_Picket_Fence_R-col", (10.5, -2.25, 0.4), (3.6, 0.08, 0.8), "wood_light", "GangHouses")
    add_box("House3_Picket_Gate", (7.8, -2.25, 0.4), (0.9, 0.04, 0.8), "wood_door", "GangHouses")

    # Blue Plastic Trash Drum outside House 3
    add_cylinder("House3_Trash_Drum", (3.6, -2.25, 0.38), 0.26, 0.76, "pvc_blue", "GangHouses", vertices=8)
    add_cylinder("House3_Trash_Lid", (3.6, -2.25, 0.78), 0.28, 0.06, "kost_dark_grey", "GangHouses", vertices=8)

    # HOUSE 4: Blue/Cream House (North side) with two-tone wainscoting
    add_box("House4_North-col", (-20.0, 7.0, 1.8), (9.5, 8.5, 3.6), "wall_tosca", "GangHouses")
    add_box("House4_Wainscot", (-20.0, 2.71, 0.50), (9.54, 0.06, 1.00), "wall_h4_lower", "GangHouses")
    add_box("House4_Molding", (-20.0, 2.70, 1.02), (9.56, 0.08, 0.05), "kost_wall_molding", "GangHouses")
    add_box("House4_Plinth", (-20.0, 2.71, 0.14), (9.54, 0.08, 0.28), "wall_plinth_grey", "GangHouses")
    add_box("House4_North_Roof-col", (-20.0, 7.0, 3.9), (9.8, 8.8, 0.8), "tile_roof_brown", "GangHouses")
    add_box("House4_Roof_Ridge", (-20.0, 7.0, 4.35), (9.9, 0.25, 0.12), "roof_ridge_dark", "GangHouses")
    add_house_entrance("House4", (-18.0, 2.71, 0.0), [(-21.5, 2.71, 1.4, 1.3, 1.1), (-16.0, 2.71, 1.4, 1.1, 1.1)], face_axis='Y', sign=-1)
    add_box("House4_Porch-col", (-18.0, 2.0, 0.06), (3.0, 1.4, 0.12), "kost_floor_paving", "GangHouses")
    add_box("House4_Awning", (-18.0, 2.0, 2.5), (3.2, 1.6, 0.06), "tin_roof", "GangHouses")

    # HOUSE 5: South House with Planter Pots & two-tone wainscoting
    add_box("House5_South-col", (-20.0, -7.0, 1.8), (9.5, 7.0, 3.6), "wall_cream", "GangHouses")
    add_box("House5_Wainscot", (-20.0, -3.46, 0.50), (9.54, 0.06, 1.00), "wall_cream_lower", "GangHouses")
    add_box("House5_Molding", (-20.0, -3.45, 1.02), (9.56, 0.08, 0.05), "kost_wall_molding", "GangHouses")
    add_box("House5_Plinth", (-20.0, -3.46, 0.14), (9.54, 0.08, 0.28), "wall_plinth_grey", "GangHouses")
    add_box("House5_South_Roof-col", (-20.0, -7.0, 3.9), (9.8, 7.4, 0.8), "tile_roof_brown", "GangHouses")
    add_box("House5_Roof_Ridge", (-20.0, -7.0, 4.35), (9.9, 0.25, 0.12), "roof_ridge_dark", "GangHouses")
    add_house_entrance("House5", (-18.5, -3.46, 0.0), [(-21.5, -3.46, 1.4, 1.4, 1.1), (-16.2, -3.46, 1.4, 1.1, 1.1)], face_axis='Y', sign=1)
    add_box("House5_Terrace-col", (-18.5, -2.85, 0.05), (4.5, 1.2, 0.1), "kost_floor_paving", "GangHouses")
    add_box("House5_Fence_L-col", (-22.5, -2.25, 0.5), (4.8, 0.12, 1.0), "iron_fence_black", "GangHouses")
    add_box("House5_Gate_Post_L-col", (-20.0, -2.25, 0.6), (0.2, 0.2, 1.2), "kost_concrete_grey", "GangHouses")
    add_box("House5_Iron_Gate", (-19.0, -2.25, 0.5), (1.8, 0.04, 1.0), "kost_railing_metal", "GangHouses")
    add_box("House5_Gate_Post_R-col", (-18.0, -2.25, 0.6), (0.2, 0.2, 1.2), "kost_concrete_grey", "GangHouses")
    add_box("House5_Fence_R-col", (-16.5, -2.25, 0.5), (2.8, 0.12, 1.0), "iron_fence_black", "GangHouses")

    # Colorful Potted Plants in House 5
    for i, px in enumerate([-17.2, -16.5, -15.8]):
        pot_mat = "paint_bucket" if i % 2 == 0 else "brick_red"
        add_cylinder(f"House5_Pot_{i}", (px, -2.8, 0.18), 0.14, 0.30, pot_mat, "GangHouses", vertices=8)
        flw_mat = "flower_magenta" if i == 0 else ("flower_yellow" if i == 1 else "flower_magenta")
        add_bush_clump(f"House5_Plant_{i}", (px, -2.8, 0.32), 0.22, "GangHouses", flower_mat=flw_mat)

    # HOUSE 6: East House with Picket Fence & two-tone wainscoting
    add_box("House6_East-col", (17.5, -7.0, 1.8), (8.5, 6.8, 3.6), "wall_cream", "GangHouses")
    add_box("House6_Wainscot", (17.5, -3.56, 0.50), (8.54, 0.06, 1.00), "wall_h6_lower", "GangHouses")
    add_box("House6_Molding", (17.5, -3.55, 1.02), (8.56, 0.08, 0.05), "kost_wall_molding", "GangHouses")
    add_box("House6_Plinth", (17.5, -3.56, 0.14), (8.54, 0.08, 0.28), "wall_plinth_grey", "GangHouses")
    add_box("House6_East_Roof-col", (17.5, -7.0, 3.9), (8.8, 7.2, 0.8), "tile_roof_brown", "GangHouses")
    add_box("House6_Roof_Ridge", (17.5, -7.0, 4.35), (8.9, 0.25, 0.12), "roof_ridge_dark", "GangHouses")
    add_house_entrance("House6", (15.5, -3.56, 0.0), [(18.5, -3.56, 1.4, 1.4, 1.1)], face_axis='Y', sign=1)
    add_box("House6_Picket_Fence-col", (17.5, -2.25, 0.4), (7.8, 0.08, 0.8), "wood_light", "GangHouses")

    # Repurposed painted tire planter outside House 6
    add_cylinder("House6_Tire_Planter", (13.5, -2.25, 0.16), 0.30, 0.22, "clothes_red", "GangHouses", vertices=10)
    add_bush_clump("House6_Tire_Bush", (13.5, -2.25, 0.28), 0.25, "GangHouses", flower_mat="flower_yellow")

    # ─── 12. TREES & FLORA (FACETED STYLIZED TREES, BANANA PLANTS & BOUGAINVILLEA) ───
    # 1. Stylized Faceted Shade Trees with multi-tier flat icosphere canopies
    stylized_trees = [
        ("Tree_N1", (-10.5, 14.0, 0.0), 4.4, 0.20, 1.5),
        ("Tree_N2", (-12.0, 8.0, 0.0), 3.8, 0.16, 1.3),
        ("Tree_N3", (-3.0, 19.5, 0.0), 4.6, 0.22, 1.6),
        ("Tree_N4", (4.0, 19.5, 0.0), 4.2, 0.19, 1.4),
        ("Tree_N5", (12.0, 13.0, 0.0), 4.3, 0.19, 1.5),
        ("Tree_N6", (18.5, 12.0, 0.0), 3.7, 0.16, 1.2),
        ("Tree_N7", (21.5, 7.0, 0.0), 4.0, 0.18, 1.3),
        ("Tree_W1", (-27.0, 4.0, 0.0), 4.5, 0.20, 1.5),
        ("Tree_W2", (-27.0, -4.0, 0.0), 4.1, 0.18, 1.4),
        ("Tree_W3", (-17.0, 14.0, 0.0), 3.9, 0.17, 1.3),
        ("Tree_W4", (-22.0, -13.0, 0.0), 4.5, 0.20, 1.5),
        ("Tree_S1", (-11.0, -13.0, 0.0), 4.3, 0.19, 1.4),
        ("Tree_S2", (-4.0, -13.0, 0.0), 4.7, 0.22, 1.6),
        ("Tree_S3", (1.0, -13.0, 0.0), 3.9, 0.17, 1.3),
        ("Tree_S4", (8.0, -13.0, 0.0), 4.4, 0.19, 1.5),
        ("Tree_S5", (15.0, -13.0, 0.0), 4.1, 0.18, 1.4),
        ("Tree_S6", (22.0, -11.0, 0.0), 4.2, 0.18, 1.4),
        ("Tree_Yard_H1", (-4.2, -3.5, 0.0), 3.6, 0.15, 1.2)
    ]
    for tname, pos, th, tr, cr in stylized_trees:
        add_stylized_tree(tname, pos, th, tr, cr, col_name="GangEnvironment")

    # 2. Iconic Indonesian Banana Trees (Pohon Pisang)
    banana_trees = [
        ("Banana_1", (-14.5, -3.5, 0.0), 3.2),
        ("Banana_2", (-13.8, -3.8, 0.0), 2.7),
        ("Banana_3", (2.8, -3.8, 0.0), 3.1),
        ("Banana_4", (12.5, -3.6, 0.0), 2.9),
        ("Banana_5", (-15.0, 3.2, 0.0), 3.3),
        ("Banana_6", (18.5, 3.2, 0.0), 2.8)
    ]
    for bname, bpos, bh in banana_trees:
        add_banana_tree(bname, bpos, height=bh, col_name="GangEnvironment")

    # 3. Leaning Coconut Palms
    add_palm_tree("Palm_West", (-25.0, 7.0, 0.0), height=5.5, col_name="GangEnvironment")
    add_palm_tree("Palm_East", (22.0, -4.5, 0.0), height=5.2, col_name="GangEnvironment")

    # 4. Low-Poly Flowering Bougainvillea Bush Clumps along walls & fences
    flower_bushes = [
        ("Bush_F1", (-5.5, -2.4, 0.0), 0.45, "flower_magenta"),
        ("Bush_F2", (-2.0, -2.4, 0.0), 0.40, "flower_yellow"),
        ("Bush_F3", (3.2, -2.4, 0.0), 0.42, "flower_magenta"),
        ("Bush_F4", (11.8, -2.4, 0.0), 0.45, "flower_yellow"),
        ("Bush_F5", (-14.0, 2.4, 0.0), 0.42, "flower_magenta"),
        ("Bush_F6", (7.8, 2.4, 0.0), 0.40, "flower_yellow"),
        ("Bush_Kos_L", (-3.6, 3.2, 0.0), 0.35, "flower_magenta"),
        ("Bush_Kos_R", (3.6, 3.2, 0.0), 0.35, "flower_yellow")
    ]
    for bname, bpos, br, bmat in flower_bushes:
        add_bush_clump(bname, bpos, br, col_name="GangEnvironment", flower_mat=bmat)

    # ─── 13. STREET LIGHT POLES, OVERHEAD WIRES & TELEPORT GATE ───
    for px, py in [(-12.0, 2.2), (8.5, 2.2)]:
        add_cylinder(f"Tiang_Listrik_{px}", (px, py, 3.5), 0.10, 7.0, "kost_concrete_grey", "GangInfrastructure", vertices=8)
        add_box(f"Trafo_Box_{px}", (px, py, 5.5), (0.4, 0.4, 0.6), "kost_dark_grey", "GangInfrastructure")
        add_box(f"Lampu_Arm_{px}", (px, py - 0.4, 5.8), (0.05, 0.8, 0.05), "kost_railing_metal", "GangInfrastructure")
        add_cylinder(f"Lampu_Cap_{px}", (px, py - 0.75, 5.75), 0.15, 0.08, "kost_dark_grey", "GangInfrastructure", vertices=8)
        add_box(f"Lampu_Bulb_{px}", (px, py - 0.75, 5.68), (0.1, 0.1, 0.1), "lamp_bulb", "GangInfrastructure")

        # Coiled fiber optic / Wi-Fi cable loop on utility pole (Iconic Indonesian street detail!)
        add_cylinder(f"Cable_Coil_{px}", (px, py + 0.12, 4.2), 0.25, 0.06, "kost_dark_grey", "GangInfrastructure", rot=(math.radians(90), 0, 0), vertices=10)

    # Overhead Power Wires
    add_angled_bar("Kabel_Listrik_1", (-12.0, 2.1, 6.6), (8.5, 2.1, 6.6), 0.02, 0.02, "kost_dark_grey", "GangInfrastructure")
    add_angled_bar("Kabel_Listrik_2", (-12.0, 2.2, 6.4), (8.5, 2.2, 6.4), 0.02, 0.02, "kost_dark_grey", "GangInfrastructure")

    # Campus Teleport Gate
    add_box("Teleport_Pole_L-col", (20.0, 2.0, 1.8), (0.2, 0.2, 3.6), "kost_concrete_grey", "TeleportArea")
    add_box("Teleport_Pole_R-col", (20.0, -2.0, 1.8), (0.2, 0.2, 3.6), "kost_concrete_grey", "TeleportArea")
    add_box("Teleport_Beam-col", (20.0, 0.0, 3.5), (0.25, 4.2, 0.3), "kost_concrete_grey", "TeleportArea")
    add_box("Teleport_Portal_Visual", (20.0, 0.0, 1.7), (0.06, 3.6, 3.2), "teleport_cyan", "TeleportArea")
    add_box("Teleport_Sign_Board", (20.0, 0.0, 3.9), (0.08, 3.2, 0.5), "pvc_blue", "TeleportArea")
    add_angled_bar("Teleport_Chain", (20.0, -1.8, 0.6), (20.0, 1.8, 0.6), 0.04, 0.04, "kost_railing_metal", "TeleportArea")

    # ─── 14. SAVE AND EXPORT GLB ───
    blend_path = "/home/haelahpx/Documents/GitHub/gameproject01/game/new-game-project/assets/models/kampung_kos_scene.blend"
    glb_path = "/home/haelahpx/Documents/GitHub/gameproject01/game/new-game-project/assets/models/kampung_kos_gang.glb"

    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved Blend file to: {blend_path}")

    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    print(f"Exported GLB to: {glb_path}")

if __name__ == "__main__":
    build_all()
