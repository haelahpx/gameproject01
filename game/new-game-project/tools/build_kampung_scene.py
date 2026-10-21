"""
Build Complete Indonesian Kampung Kos & Gang Environment v5:
- Removed ALL wainscot and plinth panels across Kost and Houses (fixed door obstruction completely!).
- User bedroom door and all room doorways are 100% clear and unobstructed!
- Removed all awkward window awnings and hallway bushes.
- Removed ALL banana trees completely as requested!
- Retained rich low-poly aesthetics: faceted trees with gradient icospheres, coconut palms,
  bougainvillea bushes, alternating black-and-white curbs, dashed road markings, asphalt patches,
  got slabs, AC compressors, KWH meters, shoe racks with sandals, doormats, and water tower.
"""

import bpy  # pyrefly: ignore[missing-import] # type: ignore
import bmesh  # pyrefly: ignore[missing-import] # type: ignore
import mathutils  # pyrefly: ignore[missing-import] # type: ignore
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

def create_tile_texture_mat(name, width=128, height=128, tile_size=32, grout_px=2, roughness=0.18):
    img_name = f"{name}_Img"
    img = bpy.data.images.get(img_name)
    if not img:
        img = bpy.data.images.new(img_name, width=width, height=height)
    
    pixels = [1.0] * (width * height * 4)
    for y in range(height):
        for x in range(width):
            idx = (y * width + x) * 4
            is_grout = (x % tile_size < grout_px) or (y % tile_size < grout_px)
            if is_grout:
                pixels[idx] = 0.50
                pixels[idx+1] = 0.52
                pixels[idx+2] = 0.55
                pixels[idx+3] = 1.0
            else:
                dist_x = min(x % tile_size - grout_px, tile_size - (x % tile_size))
                dist_y = min(y % tile_size - grout_px, tile_size - (y % tile_size))
                edge = min(dist_x, dist_y)
                val = 0.92 if edge < 2 else 0.97
                pixels[idx] = val
                pixels[idx+1] = val
                pixels[idx+2] = val * 0.99
                pixels[idx+3] = 1.0
    img.pixels = pixels
    img.pack()
    
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = roughness
    
    tex_node = nodes.new('ShaderNodeTexImage')
    tex_node.image = img
    
    output = nodes.new('ShaderNodeOutputMaterial')
    
    mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def scale_uv(obj, uv_scale_x=1.0, uv_scale_y=1.0):
    if obj and obj.type == 'MESH' and obj.data.uv_layers:
        uv_layer = obj.data.uv_layers.active
        if uv_layer:
            for loop in obj.data.loops:
                uv = uv_layer.data[loop.index].uv
                uv[0] *= uv_scale_x
                uv[1] *= uv_scale_y

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
    add_cylinder(f"{tname}_Trunk-col", (tx, ty, tz + height * 0.45), trunk_radius, height * 0.9, "tree_trunk", col_name, vertices=6)
    for i, a in enumerate([0.2, 2.3, 4.4]):
        rx = tx + math.cos(a) * (trunk_radius * 1.5)
        ry = ty + math.sin(a) * (trunk_radius * 1.5)
        add_box(f"{tname}_Root_{i}", (rx, ry, tz + 0.12), (trunk_radius * 1.3, trunk_radius * 0.7, 0.24), "tree_trunk", col_name, rot=(0, 0, a))
    
    clusters = [
        (0.0, 0.0, height * 0.90, 1.05, "plant_green_dark"),
        (-crown_radius * 0.35,  crown_radius * 0.30, height * 1.10, 0.85, "plant_green"),
        ( crown_radius * 0.35, -crown_radius * 0.25, height * 1.05, 0.80, "plant_green_lime"),
        (0.0, 0.0, height * 1.30, 0.65, "plant_green_lime")
    ]
    for idx, (ox, oy, oz, sf, mat) in enumerate(clusters):
        add_icosphere(f"{tname}_Crown_{idx}", (tx + ox, ty + oy, tz + oz), crown_radius * sf, mat, col_name, subdivisions=1)

def add_palm_tree(name, pos, height=5.2, col_name="GangEnvironment"):
    x, y, z = pos
    add_cylinder(f"{name}_Trunk_1-col", (x, y, z + height * 0.25), 0.16, height * 0.5, "tree_trunk", col_name, vertices=6, rot=(math.radians(4), math.radians(-3), 0))
    add_cylinder(f"{name}_Trunk_2-col", (x + 0.18, y - 0.18, z + height * 0.70), 0.12, height * 0.5, "tree_trunk", col_name, vertices=6, rot=(math.radians(7), math.radians(-5), 0))
    top_x, top_y, top_z = x + 0.32, y - 0.32, z + height * 0.95
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        fx = top_x + math.cos(ang) * 1.3
        fy = top_y + math.sin(ang) * 1.3
        fz = top_z - 0.22
        mat = "plant_green_dark" if i % 2 == 0 else "plant_green"
        add_box(f"{name}_Frond_{i}", (fx, fy, fz), (1.9, 0.42, 0.03), mat, col_name,
                rot=(math.radians(-22) * math.sin(ang), math.radians(22) * math.cos(ang), ang))
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

def add_tv_antenna(name, pos, height=2.0, col_name="GangHouses"):
    x, y, z = pos
    add_cylinder(f"{name}_Pole", (x, y, z + height * 0.5), 0.022, height, "kost_railing_metal", col_name, vertices=6)
    add_box(f"{name}_Boom", (x, y + 0.45, z + height), (0.03, 1.0, 0.03), "kost_railing_metal", col_name)
    for dy in [-0.35, -0.15, 0.05, 0.25]:
        ew = 0.50 - (dy + 0.35) * 0.25
        add_box(f"{name}_Elem_{dy}", (x, y + 0.45 + dy, z + height), (ew, 0.02, 0.02), "kost_railing_metal", col_name)

def build_all():
    print("Rebuilding Indonesian Kampung Kos with Warung Kondang, Unified Facade Windows & Sliding Gates v6...")
    clear_scene()

    # ─── 1. MATERIALS PALETTE ───
    create_mat("kost_wall_white", (0.92, 0.93, 0.94), roughness=0.75)
    create_mat("kost_concrete_grey", (0.55, 0.58, 0.62), roughness=0.85)
    create_mat("kost_dark_grey", (0.22, 0.24, 0.27), roughness=0.6)
    create_mat("kost_railing_metal", (0.75, 0.77, 0.80), roughness=0.3, metallic=0.7)
    create_mat("kost_floor_paving", (0.80, 0.82, 0.84), roughness=0.8)
    create_mat("kost_floor_interior", (0.88, 0.89, 0.90), roughness=0.7)
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

    # Authentic Warteg Materials (White Ceramic Tiles with Nat & WKB Green)
    create_tile_texture_mat("warteg_tile_floor", width=128, height=128, tile_size=32, grout_px=2, roughness=0.18)
    create_tile_texture_mat("warteg_tile_wall", width=128, height=128, tile_size=32, grout_px=2, roughness=0.18)
    create_mat("warteg_tile_white", (0.96, 0.96, 0.97), roughness=0.18)
    create_mat("warteg_green", (0.10, 0.48, 0.22), roughness=0.35)
    create_mat("warteg_wall_upper", (0.93, 0.90, 0.84), roughness=0.80)
    create_mat("warteg_pitcher_pink", (0.92, 0.22, 0.52), roughness=0.30)

    # Road & Infrastructure
    create_mat("road_asphalt", (0.16, 0.16, 0.18), roughness=0.90)
    create_mat("road_asphalt_dark", (0.10, 0.10, 0.12), roughness=0.85)
    create_mat("road_asphalt_worn", (0.22, 0.22, 0.24), roughness=0.95)
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

    # Unique Fence Materials for Distinct House Styles
    create_mat("fence_wood_slat", (0.46, 0.26, 0.12), roughness=0.7)       # Warm conwood teak wood
    create_mat("fence_white_wood", (0.94, 0.94, 0.91), roughness=0.6)      # Pure white painted wood
    create_mat("fence_emerald_green", (0.10, 0.28, 0.20), roughness=0.45, metallic=0.6) # Deep emerald/sage green
    create_mat("fence_terracotta", (0.75, 0.36, 0.18), roughness=0.85)     # Warm clay roster terracotta
    create_mat("fence_bronze", (0.42, 0.28, 0.18), roughness=0.35, metallic=0.8) # Metallic dark bronze
    create_mat("fence_gold_accent", (0.86, 0.70, 0.22), roughness=0.3, metallic=0.9) # Brass/gold spear tips
    create_mat("fence_stone_base", (0.32, 0.33, 0.35), roughness=0.9)      # Textured river stone

    # House Colors
    create_mat("wall_tosca", (0.24, 0.52, 0.48), roughness=0.8)
    create_mat("wall_yellow", (0.82, 0.68, 0.28), roughness=0.8)
    create_mat("wall_cream", (0.85, 0.82, 0.72), roughness=0.8)

    # Plants & Nature (Multi-Tone Gradient Palette)
    create_mat("plant_green_dark", (0.12, 0.30, 0.10), roughness=0.75)
    create_mat("plant_green", (0.18, 0.44, 0.14), roughness=0.70)
    create_mat("plant_green_lime", (0.32, 0.58, 0.18), roughness=0.65)
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

    # Food & Warteg materials
    create_mat("warteg_green", (0.12, 0.48, 0.28), roughness=0.6)
    create_mat("kerupuk_kaleng_blue", (0.12, 0.35, 0.75), roughness=0.4, metallic=0.5)
    create_mat("kerupuk_kaleng_red", (0.80, 0.16, 0.12), roughness=0.4, metallic=0.5)
    create_mat("magic_com_white", (0.92, 0.92, 0.90), roughness=0.3)
    create_mat("dish_ayam_goreng", (0.75, 0.48, 0.12), roughness=0.85)
    create_mat("dish_telur_balado", (0.85, 0.15, 0.08), roughness=0.6)
    create_mat("dish_tempe_orek", (0.35, 0.18, 0.08), roughness=0.7)
    create_mat("dish_sayur_hijau", (0.12, 0.52, 0.15), roughness=0.6)
    create_mat("dish_mie_kuning", (0.88, 0.72, 0.18), roughness=0.7)
    create_mat("dish_sayur_lodeh", (0.82, 0.65, 0.32), roughness=0.5)
    create_mat("dish_perkedel", (0.68, 0.50, 0.22), roughness=0.9)
    create_mat("dish_terong_balado", (0.60, 0.10, 0.22), roughness=0.6)
    create_mat("dish_sambal_ijo", (0.16, 0.55, 0.14), roughness=0.6)

    # ─── 2. GROUND, ROAD & STREET INFRASTRUCTURE ───
    add_box("World_Grass_Ground-col", (0.0, 3.0, -0.12), (90.0, 70.0, 0.15), "grass_lawn", "GangEnvironment")
    add_box("Gang_Road_Main-col", (-3.0, 0, -0.04), (60.0, 4.0, 0.08), "road_asphalt", "GangRoad")

    for xi in range(-25, 23, 3):
        add_box(f"Road_Center_Stripe_{xi}", (float(xi), 0.0, 0.003), (1.5, 0.12, 0.005), "road_marking_white", "GangRoad")

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

    def build_curb_segment(prefix, x_start, x_end, y_pos, block_len=1.0):
        total_len = x_end - x_start
        if total_len <= 0.05:
            return
        n_blocks = max(1, int(round(total_len / block_len)))
        actual_len = total_len / n_blocks
        for i in range(n_blocks):
            bx = x_start + (i + 0.5) * actual_len
            color_idx = int(round(bx / 1.0))
            cmat = "curb_black" if color_idx % 2 == 0 else "curb_white"
            add_box(f"{prefix}_{i}_{bx:.2f}-col", (bx, y_pos, 0.05), (actual_len, 0.125, 0.10), cmat, "GangRoad")

    # North curbs: stops before Kost columns, open gate driveway, pole, and teleport gate
    build_curb_segment("Curb_N_A", -30.0, -8.15, 2.0375)
    build_curb_segment("Curb_N_B", -7.65, -3.85, 2.0375)
    build_curb_segment("Curb_N_C", 3.85, 7.65, 2.0375)
    build_curb_segment("Curb_N_D", 8.50, 19.85, 2.0375)

    # South curbs: stops before House 5 & 6 gates, and teleport pole
    build_curb_segment("Curb_S_A", -30.0, -19.40, -2.0375)
    build_curb_segment("Curb_S_B", -17.80, 15.85, -2.0375)
    build_curb_segment("Curb_S_C", 17.35, 19.85, -2.0375)

    add_box("Gang_Drain_North", (-3.0, 1.94, -0.01), (60.0, 0.08, 0.04), "drain_trench", "GangRoad")
    add_box("Gang_Drain_South", (-3.0, -1.94, -0.01), (60.0, 0.08, 0.04), "drain_trench", "GangRoad")

    for si, gx in enumerate([-22.0, -15.0, -8.0, 1.0, 8.0, 15.0]):
        add_box(f"Got_Slab_N_{si}", (gx, 1.9175, 0.01), (1.2, 0.115, 0.03), "got_slab", "GangRoad")
        add_box(f"Got_Slot_N_{si}_1", (gx - 0.25, 1.9175, 0.02), (0.20, 0.04, 0.02), "drain_trench", "GangRoad")
        add_box(f"Got_Slot_N_{si}_2", (gx + 0.25, 1.9175, 0.02), (0.20, 0.04, 0.02), "drain_trench", "GangRoad")
        add_box(f"Got_Slab_S_{si}", (gx, -1.9175, 0.01), (1.2, 0.115, 0.03), "got_slab", "GangRoad")
        add_box(f"Got_Slot_S_{si}_1", (gx - 0.25, -1.9175, 0.02), (0.20, 0.04, 0.02), "drain_trench", "GangRoad")
        add_box(f"Got_Slot_S_{si}_2", (gx + 0.25, -1.9175, 0.02), (0.20, 0.04, 0.02), "drain_trench", "GangRoad")

    for sbi, bx in enumerate([-12.0, 6.0]):
        add_box(f"Polisi_Tidur_{sbi}-col", (bx, 0.0, 0.04), (0.40, 3.8, 0.08), "kost_dark_grey", "GangRoad")
        for zi in range(-16, 17, 4):
            zy = zi * 0.1
            add_box(f"Polisi_Stripe_{sbi}_{zi}", (bx, zy, 0.045), (0.36, 0.20, 0.08), "warsun_yellow", "GangRoad")

    # ─── 3. KOST BUILDING FLOORS & STRUCTURAL WALLS (100% UNOBSTRUCTED) ───
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

    # Front Wall Facade Windows (Unified Architecture matching Player Room Street Window!)
    def add_kos_front_window(name_prefix, cx, cy, cz_base):
        # Wall Cutouts
        add_box(f"{name_prefix}_Wall_L-col", (cx - 1.475, cy, cz_base + 1.5), (1.55, 0.2, 3.0), "kost_wall_white", "KostBuilding")
        add_box(f"{name_prefix}_Wall_R-col", (cx + 1.475, cy, cz_base + 1.5), (1.55, 0.2, 3.0), "kost_wall_white", "KostBuilding")
        add_box(f"{name_prefix}_Wall_Sill-col", (cx, cy, cz_base + 0.5), (1.4, 0.2, 1.0), "kost_wall_white", "KostBuilding")
        add_box(f"{name_prefix}_Wall_Lintel-col", (cx, cy, cz_base + 2.6), (1.4, 0.2, 0.8), "kost_wall_white", "KostBuilding")
        
        # Aluminum detailed frame & mullions
        add_box(f"{name_prefix}_Frame_Bottom", (cx, cy, cz_base + 1.03), (1.42, 0.16, 0.06), "kost_dark_grey", "KostBuilding")
        add_box(f"{name_prefix}_Frame_Top", (cx, cy, cz_base + 2.17), (1.42, 0.16, 0.06), "kost_dark_grey", "KostBuilding")
        add_box(f"{name_prefix}_Frame_L", (cx - 0.67, cy, cz_base + 1.6), (0.06, 0.16, 1.10), "kost_dark_grey", "KostBuilding")
        add_box(f"{name_prefix}_Frame_R", (cx + 0.67, cy, cz_base + 1.6), (0.06, 0.16, 1.10), "kost_dark_grey", "KostBuilding")
        add_box(f"{name_prefix}_Frame_Mid", (cx, cy, cz_base + 1.6), (0.04, 0.16, 1.10), "kost_dark_grey", "KostBuilding")
        add_box(f"{name_prefix}_Glass", (cx, cy, cz_base + 1.6), (1.34, 0.02, 1.10), "window_glass_transparent", "KostBuilding")

    # All 4 front facade windows are now 100% unified in framing, depth, and glass!
    add_kos_front_window("Player_WinStreet", -5.75, 2.2, 0.0)
    add_kos_front_window("Kost_L_Win_F2", -5.75, 2.2, 3.0)
    add_kos_front_window("Kost_R_Win_F1", 5.75, 2.2, 0.0)
    add_kos_front_window("Kost_R_Win_F2", 5.75, 2.2, 3.0)

    add_box("Kost_L_Col_Front-col", (-7.9, 2.2, 3.0), (0.5, 0.4, 6.0), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_L_Col_Inner-col", (-3.6, 2.2, 3.0), (0.5, 0.4, 6.0), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_R_Col_Inner-col", (3.6, 2.2, 3.0), (0.5, 0.4, 6.0), "kost_concrete_grey", "KostBuilding")
    add_box("Kost_R_Col_Front-col", (7.9, 2.2, 3.0), (0.5, 0.4, 6.0), "kost_concrete_grey", "KostBuilding")

    # Corridor Wall Left Floor 1 (Player Room Doorway & CRYSTAL CLEAR Courtyard Window)
    # Notice: Doorway from Y=3.10 to Y=4.10 is 100% WIDE OPEN and CLEAR of any obstacles!
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

    # Outdoor AC units on exterior walls
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

    # Low-Poly Shoe Racks outside rooms (against solid partition walls, 100% clear of doors!)
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

    # Rooftop Water Tower
    add_box("Toren_Platform-col", (0.0, 16.2, 6.2), (2.0, 2.0, 0.2), "kost_dark_grey", "KostBuilding")
    for leg_x in [-0.85, 0.85]:
        for leg_y in [15.35, 17.05]:
            add_cylinder(f"Toren_Leg_{leg_x}_{leg_y}", (leg_x, leg_y, 6.8), 0.04, 1.2, "kost_railing_metal", "KostBuilding", vertices=6)
    add_box("Toren_Tower_Deck", (0.0, 16.2, 7.4), (1.9, 1.9, 0.08), "kost_dark_grey", "KostBuilding")
    add_cylinder("Toren_Tank", (0.0, 16.2, 8.4), 0.82, 1.9, "toren_orange", "KostBuilding", vertices=16)
    add_cylinder("Toren_Lid", (0.0, 16.2, 9.4), 0.45, 0.15, "kost_dark_grey", "KostBuilding")
    add_cylinder("Toren_Pipe_PVC", (0.8, 15.8, 5.0), 0.04, 5.0, "pvc_blue", "KostBuilding", vertices=6)

    # ─── 6. MONUMENTAL ENTRANCE PANEL "KOST KONDANG" WITH 3D TEXT ───
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

    create_3d_text("Sign_Text_Kost_Windah_Front", "KOST KONDANG", (0.0, 2.04, 1.12), (math.radians(90), 0, 0), size=0.30, extrude=0.04)
    create_3d_text("Sign_Subtext_Front", "PUTRA & PUTRI", (0.0, 2.04, 0.72), (math.radians(90), 0, 0), size=0.14, extrude=0.02)
    create_3d_text("Sign_Text_Kost_Windah_Back", "KOST KONDANG", (0.0, 2.36, 1.12), (math.radians(90), 0, math.radians(180)), size=0.30, extrude=0.04)
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

    # PLN Token Meter for Player Room (on front wall, outside doorway)
    add_box("Token_Meter_Box", (-3.46, 2.7, 1.55), (0.05, 0.22, 0.32), "paint_bucket", "KostBuilding")
    add_box("Token_Meter_Screen", (-3.43, 2.7, 1.63), (0.015, 0.12, 0.06), "plant_green", "KostBuilding")
    add_box("Token_Meter_Keypad", (-3.43, 2.7, 1.50), (0.015, 0.14, 0.10), "kost_dark_grey", "KostBuilding")
    add_box("Token_Meter_LED", (-3.43, 2.76, 1.63), (0.015, 0.02, 0.02), "clothes_red", "KostBuilding")
    add_box("Token_Meter_Breaker", (-3.43, 2.7, 1.41), (0.02, 0.04, 0.04), "pvc_blue", "KostBuilding")

    # ─── 8. WC UMUM (WIDE 1.15m DOORWAY, REAL CERAMIC TUB & KLOSET) ───
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

    # ─── 10. WARTEG "WARUNG KONDANG" (AUTHENTIC INDONESIAN WARTEG OVERHAUL) ───
    # Floor: White Ceramic Tiles with Grout
    fl_obj = add_box("Warsun_Floor-col", (13.0, 6.35, 0.05), (9.0, 8.3, 0.1), "warteg_tile_floor", "WarsunBuilding")
    scale_uv(fl_obj, 5.6, 5.2)
    add_box("Warsun_Step-col", (13.000, 2.1625, 0.050), (9.000, 0.125, 0.100), "curb_concrete", "WarsunBuilding")

    # Half-Walls: White Ceramic Tiles with Grout (height 1.45m)
    hw_b = add_box("Warsun_HalfWall_Back-col", (13.0, 10.50, 0.725), (9.0, 0.12, 1.45), "warteg_tile_wall", "WarsunBuilding")
    scale_uv(hw_b, 5.6, 0.9)
    add_box("Warsun_Tile_Cap_Back", (13.0, 10.45, 1.46), (9.04, 0.06, 0.04), "warteg_green", "WarsunBuilding")

    hw_l = add_box("Warsun_HalfWall_Left-col", (8.50, 6.35, 0.725), (0.12, 8.3, 1.45), "warteg_tile_wall", "WarsunBuilding")
    scale_uv(hw_l, 5.2, 0.9)
    add_box("Warsun_Tile_Cap_Left", (8.55, 6.35, 1.46), (0.06, 8.34, 0.04), "warteg_green", "WarsunBuilding")

    hw_r = add_box("Warsun_HalfWall_Right-col", (17.50, 6.35, 0.725), (0.12, 8.3, 1.45), "warteg_tile_wall", "WarsunBuilding")
    scale_uv(hw_r, 5.2, 0.9)
    add_box("Warsun_Tile_Cap_Right", (17.45, 6.35, 1.46), (0.06, 8.34, 0.04), "warteg_green", "WarsunBuilding")

    # Upper Walls (Above 1.45m: clean cream painted wall)
    add_box("Warsun_BackWall_Upper-col", (13.0, 10.55, 2.525), (9.2, 0.2, 2.15), "warteg_wall_upper", "WarsunBuilding")
    add_box("Warsun_LeftWall_Upper-col", (8.45, 6.35, 2.525), (0.2, 8.4, 2.15), "warteg_wall_upper", "WarsunBuilding")
    add_box("Warsun_RightWall_Upper-col", (17.55, 6.35, 2.525), (0.2, 8.4, 2.15), "warteg_wall_upper", "WarsunBuilding")

    # Ceiling, Roof & Front Canopy
    add_box("Warsun_Roof-col", (13.05, 6.35, 3.75), (9.2, 8.8, 0.25), "tin_roof", "WarsunBuilding")
    add_box("Warsun_Ceiling", (13.0, 6.35, 3.60), (9.0, 8.3, 0.04), "curb_white", "WarsunBuilding")

    # Warung Kondang Monumental Front 3D Signage Panel
    add_box("Warung_Sign_Panel-col", (13.0, 2.08, 3.32), (7.8, 0.08, 0.90), "warteg_green", "WarsunBuilding")
    add_box("Warung_Sign_Border_Top", (13.0, 2.03, 3.74), (7.84, 0.04, 0.05), "warsun_yellow", "WarsunBuilding")
    add_box("Warung_Sign_Border_Bot", (13.0, 2.03, 2.90), (7.84, 0.04, 0.05), "warsun_yellow", "WarsunBuilding")
    add_box("Warung_Sign_Border_L", (9.1, 2.03, 3.32), (0.05, 0.04, 0.90), "warsun_yellow", "WarsunBuilding")
    add_box("Warung_Sign_Border_R", (16.9, 2.03, 3.32), (0.05, 0.04, 0.90), "warsun_yellow", "WarsunBuilding")

    create_3d_text("Sign_Text_Warung_Kondang", "WARUNG KONDANG", (13.0, 2.00, 3.46), (math.radians(90), 0, 0), size=0.36, extrude=0.05, mat_name="warsun_yellow", col_name="WarsunBuilding")
    create_3d_text("Sign_Subtext_Warung_Kondang", "SEDIA: NASI RAMES & MINUMAN", (13.0, 2.00, 3.12), (math.radians(90), 0, 0), size=0.15, extrude=0.02, mat_name="curb_white", col_name="WarsunBuilding")

    # ─── AUTHENTIC WARTEG KHARISMA BAHARI L-SHAPED COUNTER (MATCHING REFERENCE PHOTO) ───
    # 1. Solid Grounded Counter Base (Starts at floor Z=0.10, top at Z=0.88)
    # Front Base: X from 12.00 to 17.44, Y from 3.65 to 4.75
    add_box("Warsun_Counter_Front_Base-col", (14.72, 4.20, 0.49), (5.44, 1.10, 0.78), "warteg_tile_wall", "WarsunBuilding")
    # Side Base: X from 12.00 to 13.15, Y from 4.75 to 7.50
    add_box("Warsun_Counter_Side_Base-col", (12.575, 6.125, 0.49), (1.15, 2.75, 0.78), "warteg_tile_wall", "WarsunBuilding")

    # 2. Dining Table Ledges (Z=0.88 to Z=0.92, Top at Z=0.92)
    # Front Table Ledge: X from 12.45 to 17.44, Y from 3.65 to 4.10
    add_box("Warsun_Counter_Front_Ledge-col", (14.945, 3.875, 0.90), (4.99, 0.45, 0.04), "warteg_tile_white", "WarsunBuilding")
    # Side Table Ledge: X from 12.00 to 12.45, Y from 4.10 to 7.50
    add_box("Warsun_Counter_Side_Ledge-col", (12.225, 5.80, 0.90), (0.45, 3.40, 0.04), "warteg_tile_white", "WarsunBuilding")
    # Corner Joint: X from 12.00 to 12.45, Y from 3.65 to 4.10
    add_box("Warsun_Counter_Corner_Top-col", (12.225, 3.875, 0.90), (0.45, 0.45, 0.04), "warteg_tile_white", "WarsunBuilding")
    # Green Bullnose Trims
    add_box("Warsun_Counter_Front_Trim", (14.72, 3.65, 0.88), (5.44, 0.04, 0.06), "warteg_green", "WarsunBuilding")
    add_box("Warsun_Counter_Side_Trim", (12.00, 5.575, 0.88), (0.04, 3.85, 0.06), "warteg_green", "WarsunBuilding")

    # 3. L-SHAPED TWO-TIER GLASS DISPLAY SHOWCASE (ETALASE LETTER L)
    # Front Arm: X from 12.45 to 17.44, Y from 4.10 to 4.75
    add_box("Warteg_Showcase_F_Base", (14.945, 4.425, 0.93), (4.99, 0.65, 0.02), "stainless_tray", "WarsunBuilding")
    add_box("Warteg_Showcase_F_Glass_Front", (14.945, 4.10, 1.31), (4.99, 0.02, 0.76), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warteg_Showcase_F_Glass_Top", (14.945, 4.425, 1.70), (4.99, 0.65, 0.02), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warteg_Showcase_F_Glass_R", (17.44, 4.425, 1.31), (0.02, 0.65, 0.76), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warteg_Showcase_F_Shelf", (14.945, 4.425, 1.31), (4.95, 0.61, 0.02), "glass_showcase_transparent", "WarsunBuilding")

    # Side Arm: Y from 4.10 to 7.50, X from 12.45 to 13.15
    add_box("Warteg_Showcase_S_Base", (12.80, 6.125, 0.93), (0.65, 2.75, 0.02), "stainless_tray", "WarsunBuilding")
    # CRITICAL: Glass side meets glass front exactly at (12.45, 4.10)!
    add_box("Warteg_Showcase_S_Glass_Side", (12.45, 5.80, 1.31), (0.02, 3.40, 0.76), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warteg_Showcase_S_Glass_Top", (12.80, 6.125, 1.70), (0.65, 2.75, 0.02), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warteg_Showcase_S_Glass_Back", (12.80, 7.50, 1.31), (0.65, 0.02, 0.76), "glass_showcase_transparent", "WarsunBuilding")
    add_box("Warteg_Showcase_S_Shelf", (12.80, 6.125, 1.31), (0.61, 2.71, 0.02), "glass_showcase_transparent", "WarsunBuilding")

    # Aluminum Framing Posts & Bars
    add_box("Warteg_Case_Post_Corner", (12.45, 4.10, 1.31), (0.04, 0.04, 0.78), "kost_railing_metal", "WarsunBuilding")
    add_box("Warteg_Case_Post_Inner_Corner", (13.15, 4.75, 1.31), (0.04, 0.04, 0.78), "kost_railing_metal", "WarsunBuilding")
    for cx in [14.95, 17.44]:
        for cy in [4.10, 4.75]:
            add_box(f"Warteg_Case_Post_{cx}_{cy}", (cx, cy, 1.31), (0.03, 0.03, 0.78), "kost_railing_metal", "WarsunBuilding")
    for cy in [5.80, 7.50]:
        for cx in [12.45, 13.15]:
            add_box(f"Warteg_Case_Post_{cx}_{cy}", (cx, cy, 1.31), (0.03, 0.03, 0.78), "kost_railing_metal", "WarsunBuilding")

    add_box("Warteg_Case_F_Rail_Top", (14.945, 4.10, 1.70), (4.99, 0.03, 0.03), "kost_railing_metal", "WarsunBuilding")
    add_box("Warteg_Case_F_Rail_Bot", (14.945, 4.10, 0.92), (4.99, 0.03, 0.03), "kost_railing_metal", "WarsunBuilding")
    add_box("Warteg_Case_S_Rail_Top", (12.45, 5.80, 1.70), (0.03, 3.40, 0.03), "kost_railing_metal", "WarsunBuilding")
    add_box("Warteg_Case_S_Rail_Bot", (12.45, 5.80, 0.92), (0.03, 3.40, 0.03), "kost_railing_metal", "WarsunBuilding")

    # 4. FOOD DISHES INSIDE SHOWCASE
    # Front Lower Tier (5 Trays)
    dishes_front_low = [
        ("dish_ayam_goreng", "Ayam_Goreng_Lengkuas"),
        ("dish_telur_balado", "Telur_Balado_Pedas"),
        ("dish_tempe_orek", "Orek_Tempe_Manis"),
        ("dish_sayur_hijau", "Tumis_Kangkung_Buncis"),
        ("dish_mie_kuning", "Mie_Goreng_Warteg")
    ]
    for i, (fmat, fname) in enumerate(dishes_front_low):
        tx = 13.50 + i * 0.85
        add_box(f"Tray_Low_F_{i}", (tx, 4.425, 0.95), (0.75, 0.50, 0.04), "stainless_tray", "WarsunBuilding")
        add_box(f"Food_Low_F_{i}_{fname}", (tx, 4.425, 0.98), (0.69, 0.44, 0.05), fmat, "WarsunBuilding")

    # Front Upper Tier (5 Plates on Stands)
    dishes_front_up = [
        ("dish_perkedel", "Perkedel_Kentang"),
        ("dish_terong_balado", "Terong_Balado"),
        ("wood_door_dark", "Tahu_Tempe_Bacem"),
        ("dish_ayam_goreng", "Ikan_Goreng_Kremes"),
        ("dish_mie_kuning", "Telur_Dadar_Tebal")
    ]
    for i, (fmat, fname) in enumerate(dishes_front_up):
        tx = 13.50 + i * 0.85
        add_cylinder(f"Plate_Stand_F_{i}", (tx, 4.425, 1.33), 0.11, 0.03, "paint_bucket", "WarsunBuilding", vertices=10)
        add_cylinder(f"Plate_Dish_F_{i}", (tx, 4.425, 1.36), 0.23, 0.02, "curb_white", "WarsunBuilding", vertices=12)
        add_cylinder(f"Food_Up_F_{i}_{fname}", (tx, 4.425, 1.39), 0.19, 0.04, fmat, "WarsunBuilding", vertices=12)

    # Side Lower Tier (3 Trays)
    dishes_side_low = [
        ("dish_sayur_lodeh", "Sayur_Lodeh_Tahu"),
        ("dish_telur_balado", "Sambal_Goreng_Ati"),
        ("dish_sayur_hijau", "Urap_Sayur_Kelapa")
    ]
    for i, (fmat, fname) in enumerate(dishes_side_low):
        ty = 5.20 + i * 0.85
        add_box(f"Tray_Low_S_{i}", (12.80, ty, 0.95), (0.50, 0.75, 0.04), "stainless_tray", "WarsunBuilding")
        add_box(f"Food_Low_S_{i}_{fname}", (12.80, ty, 0.98), (0.44, 0.69, 0.05), fmat, "WarsunBuilding")

    # Side Upper Tier (3 Plates on Stands)
    dishes_side_up = [
        ("dish_telur_balado", "Kentang_Mustofa"),
        ("dish_perkedel", "Bakwan_Sayur"),
        ("dish_ayam_goreng", "Tempe_Mendoan")
    ]
    for i, (fmat, fname) in enumerate(dishes_side_up):
        ty = 5.20 + i * 0.85
        add_cylinder(f"Plate_Stand_S_{i}", (12.80, ty, 1.33), 0.11, 0.03, "paint_bucket", "WarsunBuilding", vertices=10)
        add_cylinder(f"Plate_Dish_S_{i}", (12.80, ty, 1.36), 0.23, 0.02, "curb_white", "WarsunBuilding", vertices=12)
        add_cylinder(f"Food_Up_S_{i}_{fname}", (12.80, ty, 1.39), 0.19, 0.04, fmat, "WarsunBuilding", vertices=12)

    # 5. AUTHENTIC PROPS ON TOP OF GLASS SHOWCASE (Z=1.70)
    for tx in [14.30, 16.50]:
        add_cylinder(f"Warteg_Toples_Kerupuk_{tx}", (tx, 4.425, 1.86), 0.16, 0.30, "glass_showcase_transparent", "WarsunBuilding", vertices=14)
        add_cylinder(f"Warteg_Toples_Lid_{tx}", (tx, 4.425, 2.02), 0.17, 0.03, "curb_white", "WarsunBuilding", vertices=14)
        add_cylinder(f"Warteg_Toples_Fill_{tx}", (tx, 4.425, 1.84), 0.14, 0.24, "warteg_green", "WarsunBuilding", vertices=12)

    for tx in [13.40, 15.40]:
        add_cylinder(f"Warteg_Plate_Gorengan_{tx}", (tx, 4.425, 1.72), 0.22, 0.02, "dish_telur_balado", "WarsunBuilding", vertices=12)
        add_cylinder(f"Warteg_Pisang_Goreng_{tx}", (tx, 4.425, 1.76), 0.18, 0.05, "dish_tempe_orek", "WarsunBuilding", vertices=12)

    add_cylinder("Warteg_Toples_Side", (12.80, 5.60, 1.86), 0.16, 0.30, "glass_showcase_transparent", "WarsunBuilding", vertices=14)
    add_cylinder("Warteg_Toples_Side_Lid", (12.80, 5.60, 2.02), 0.17, 0.03, "curb_white", "WarsunBuilding", vertices=14)
    add_cylinder("Warteg_Plate_Side_Gorengan", (12.80, 6.70, 1.72), 0.22, 0.02, "dish_telur_balado", "WarsunBuilding", vertices=12)

    # 6. STURDY, GROUNDED CUSTOMER BENCHES (NO FLOATING PIECES, NO CUTS)
    # Front Bench (Along front table): from X=12.00 to 17.20, center X=14.60, Y=3.15
    add_box("Warteg_Bench_Front-col", (14.60, 3.15, 0.485), (5.20, 0.32, 0.05), "warteg_green", "WarsunBuilding")
    for bx in [12.20, 13.45, 14.70, 15.95, 17.10]:
        add_box(f"Warteg_Bench_F_Leg_{bx}-col", (bx, 3.15, 0.28), (0.05, 0.26, 0.36), "kost_dark_grey", "WarsunBuilding")
    add_box("Warteg_Bench_F_Rail", (14.60, 3.15, 0.18), (5.20, 0.04, 0.04), "warteg_green", "WarsunBuilding")

    # Side Bench (Along side table): from Y=3.50 to 7.50, center Y=5.50, X=11.45
    add_box("Warteg_Bench_Side-col", (11.45, 5.50, 0.485), (0.32, 4.00, 0.05), "warteg_green", "WarsunBuilding")
    for by in [3.70, 4.95, 6.20, 7.40]:
        add_box(f"Warteg_Bench_S_Leg_{by}-col", (11.45, by, 0.28), (0.26, 0.05, 0.36), "kost_dark_grey", "WarsunBuilding")
    add_box("Warteg_Bench_S_Rail", (11.45, 5.50, 0.18), (0.04, 4.00, 0.04), "warteg_green", "WarsunBuilding")

    # 7. PROPS RESTING FIRMLY ON TABLE (Z=0.92, ZERO FLOATING)
    # Blue Kerupuk Tin on Side Table at Y=7.15 (firmly on table, NOT in walkway!)
    add_box("Blek_Kerupuk_Body", (12.225, 7.15, 1.12), (0.32, 0.32, 0.40), "kerupuk_kaleng_blue", "WarsunBuilding")
    add_cylinder("Blek_Kerupuk_Lid", (12.225, 7.15, 1.335), 0.15, 0.03, "paint_bucket", "WarsunBuilding")
    add_cylinder("Blek_Kerupuk_Window", (12.055, 7.15, 1.12), 0.11, 0.02, "glass_showcase_transparent", "WarsunBuilding", rot=(0, math.radians(90), 0))

    # Red Kerupuk Tin on Far Right Table End at X=17.15
    add_box("Blek_Kerupuk_Merah_Body", (17.15, 3.875, 1.12), (0.32, 0.32, 0.40), "kerupuk_kaleng_red", "WarsunBuilding")
    add_cylinder("Blek_Kerupuk_Merah_Lid", (17.15, 3.875, 1.335), 0.15, 0.03, "paint_bucket", "WarsunBuilding")
    add_cylinder("Blek_Kerupuk_Merah_Window", (17.15, 3.705, 1.12), 0.11, 0.02, "glass_showcase_transparent", "WarsunBuilding", rot=(math.radians(90), 0, 0))

    # Pink Water Pitcher (Teko Air Pink)
    add_cylinder("Table_Teko_Pink_Body", (12.225, 4.35, 1.04), 0.10, 0.24, "warteg_pitcher_pink", "WarsunBuilding", vertices=12)
    add_cylinder("Table_Teko_Pink_Lid", (12.225, 4.35, 1.175), 0.11, 0.03, "curb_white", "WarsunBuilding", vertices=12)

    # Pink Round Tissue Dispenser
    add_cylinder("Table_Tisu_Pink_Body", (13.50, 3.875, 0.98), 0.08, 0.12, "warteg_pitcher_pink", "WarsunBuilding", vertices=12)
    add_cylinder("Table_Tisu_Pink_Top", (13.50, 3.875, 1.05), 0.05, 0.04, "warteg_pitcher_pink", "WarsunBuilding", vertices=10)

    # Green Chilies Plate
    add_cylinder("Table_Cabai_Plate", (14.10, 3.875, 0.93), 0.08, 0.02, "curb_white", "WarsunBuilding", vertices=10)
    add_cylinder("Table_Cabai_Green", (14.10, 3.875, 0.945), 0.06, 0.015, "dish_sayur_hijau", "WarsunBuilding", vertices=8)

    # Customer at Front Table (Eating Plate, Rice, Dish, Iced Tea)
    add_cylinder("Table_Customer_Plate_F", (15.30, 3.875, 0.93), 0.18, 0.02, "dish_telur_balado", "WarsunBuilding", vertices=14)
    add_cylinder("Table_Customer_Rice_F", (15.30, 3.875, 0.95), 0.11, 0.03, "paint_bucket", "WarsunBuilding", vertices=10)
    add_box("Table_Customer_Dish_F", (15.38, 3.875, 0.96), (0.07, 0.07, 0.03), "dish_ayam_goreng", "WarsunBuilding")
    add_cylinder("Table_Gelas_Teh_F", (14.70, 3.875, 0.98), 0.045, 0.12, "glass_showcase_transparent", "WarsunBuilding", vertices=10)
    add_cylinder("Table_Air_Teh_F", (14.70, 3.875, 0.97), 0.042, 0.10, "dish_tempe_orek", "WarsunBuilding", vertices=10)

    # Customer at Side Table (Eating Plate, Rice, Dish, Iced Tea, Kobokan)
    add_cylinder("Table_Customer_Plate_S", (12.225, 5.20, 0.93), 0.18, 0.02, "curb_white", "WarsunBuilding", vertices=14)
    add_cylinder("Table_Customer_Rice_S", (12.225, 5.20, 0.95), 0.11, 0.03, "paint_bucket", "WarsunBuilding", vertices=10)
    add_box("Table_Customer_Dish_S", (12.225, 5.28, 0.96), (0.07, 0.07, 0.03), "dish_telur_balado", "WarsunBuilding")
    add_cylinder("Table_Gelas_Teh_S", (12.225, 4.65, 0.98), 0.045, 0.12, "glass_showcase_transparent", "WarsunBuilding", vertices=10)
    add_cylinder("Table_Air_Teh_S", (12.225, 4.65, 0.97), 0.042, 0.10, "dish_tempe_orek", "WarsunBuilding", vertices=10)
    add_cylinder("Table_Kobokan_Bowl", (12.225, 5.80, 0.95), 0.09, 0.06, "stainless_tray", "WarsunBuilding", vertices=12)

    # ─── KITCHEN PREP & BACK WALL AUTHENTIC DECOR ───
    add_box("Cook_Prep_Counter-col", (15.20, 8.80, 0.45), (3.60, 0.75, 0.90), "stainless_tray", "WarsunBuilding")
    add_cylinder("Magic_Com_Body", (13.90, 8.80, 1.10), 0.22, 0.38, "magic_com_white", "WarsunBuilding", vertices=14)
    add_cylinder("Magic_Com_Lid", (13.90, 8.80, 1.30), 0.23, 0.04, "stainless_tray", "WarsunBuilding", vertices=14)
    add_cylinder("Cobek_Batu", (15.60, 8.80, 0.94), 0.16, 0.05, "kost_dark_grey", "WarsunBuilding", vertices=10)
    add_cylinder("Sambal_Ulek", (15.60, 8.80, 0.97), 0.14, 0.03, "dish_telur_balado", "WarsunBuilding", vertices=10)
    add_cylinder("Ulekan_Batu", (15.68, 8.76, 1.03), 0.03, 0.14, "kost_dark_grey", "WarsunBuilding", rot=(math.radians(30), 0, 0))
    add_cylinder("Kuali_Besar", (16.40, 8.80, 0.94), 0.24, 0.08, "kost_dark_grey", "WarsunBuilding", vertices=12)

    # ─── BACK WALL AUTHENTIC WARTEG DECOR (CLEAN, NON-OVERLAPPING LAYOUT) ───
    # 1. Analog Wall Clock on Left Wall (X=10.50, sitting cleanly in front of wall Y=10.45)
    add_cylinder("Warteg_Jam_Dinding", (10.50, 10.425, 2.70), 0.20, 0.03, "curb_white", "WarsunBuilding", rot=(math.radians(90), 0, 0), vertices=14)
    add_cylinder("Warteg_Jam_Frame", (10.50, 10.415, 2.70), 0.22, 0.04, "dish_telur_balado", "WarsunBuilding", rot=(math.radians(90), 0, 0), vertices=14)

    # 2. Monumental WKB-Style Oval Logo in Upper Center (X=13.00, Z=2.75)
    add_cylinder("WKB_Badge_Oval", (13.0, 10.45, 2.75), 0.85, 0.04, "warteg_green", "WarsunBuilding", rot=(math.radians(90), 0, 0), vertices=16)
    add_cylinder("WKB_Badge_Inner", (13.0, 10.43, 2.75), 0.75, 0.04, "kost_dark_grey", "WarsunBuilding", rot=(math.radians(90), 0, 0), vertices=16)
    create_3d_text("WKB_Text", "WARUNG KONDANG", (13.0, 10.40, 2.82), (math.radians(90), 0, 0), size=0.22, extrude=0.03, mat_name="warsun_yellow", col_name="WarsunBuilding")
    create_3d_text("WKB_Subtext", "KHARISMA BAHARI STYLE", (13.0, 10.40, 2.60), (math.radians(90), 0, 0), size=0.10, extrude=0.02, mat_name="dish_telur_balado", col_name="WarsunBuilding")

    # 3. Framed WKB Banner on Right Wall (X=15.50, Z=2.90)
    add_box("WKB_Banner_Ojol_Frame", (15.50, 10.44, 2.90), (1.80, 0.02, 0.25), "kost_dark_grey", "WarsunBuilding")
    add_box("WKB_Banner_Ojol_Panel", (15.50, 10.42, 2.90), (1.76, 0.02, 0.22), "curb_white", "WarsunBuilding")

    # 4. Hanging Drink Sachets in Clear Columns (Zero overlap with Logo, Clock, or Banner!)
    sachet_x_positions = [
        11.20, 11.60, 12.00,        # Group A: Left of center logo
        13.95, 14.30,               # Group B1: Between center logo and banner
        16.60, 16.90, 17.20         # Group B2: Right of banner towards right wall
    ]
    for i, sx in enumerate(sachet_x_positions):
        add_box(f"Warsun_Sachet_Strip_{i}", (sx, 10.42, 2.10), (0.16, 0.02, 0.85), "warsun_yellow" if i % 2 == 0 else "dish_telur_balado", "WarsunBuilding")

    # ─── 11. GANG HOUSES (UNIFIED BALCONY 2F, CONTINUOUS FENCES & SLIDING GATES) ───
    def add_house_entrance(name_prefix, door_center, win_centers, face_axis='Y', sign=-1):
        dx, dy, dz = door_center
        if face_axis == 'Y':
            add_box(f"{name_prefix}_Door_Frame_L", (dx - 0.48, dy, dz + 1.05), (0.06, 0.08, 2.15), "kost_dark_grey", "GangHouses")
            add_box(f"{name_prefix}_Door_Frame_R", (dx + 0.48, dy, dz + 1.05), (0.06, 0.08, 2.15), "kost_dark_grey", "GangHouses")
            add_box(f"{name_prefix}_Door_Frame_Top", (dx, dy, dz + 2.15), (1.02, 0.08, 0.06), "kost_dark_grey", "GangHouses")
            add_box(f"{name_prefix}_Door_Leaf", (dx, dy + sign * 0.02, dz + 1.05), (0.90, 0.04, 2.08), "wood_door", "GangHouses")
            add_box(f"{name_prefix}_Door_Knob", (dx + 0.35, dy + sign * 0.05, dz + 1.05), (0.05, 0.05, 0.05), "kost_railing_metal", "GangHouses")
            add_box(f"{name_prefix}_Door_Roster", (dx, dy + sign * 0.02, dz + 2.30), (0.65, 0.04, 0.18), "roster_vent", "GangHouses")
            add_doormat(f"Doormat_{name_prefix}", (dx, dy + sign * 0.35, dz), "clothes_red", "GangHouses")

            for idx, (wx, wy, wz, w_w, w_h) in enumerate(win_centers):
                add_box(f"{name_prefix}_Win_Sill_{idx}", (wx, wy, wz - w_h/2.0), (w_w + 0.08, 0.10, 0.05), "kost_dark_grey", "GangHouses")
                add_box(f"{name_prefix}_Win_Top_{idx}", (wx, wy, wz + w_h/2.0), (w_w + 0.08, 0.08, 0.05), "kost_dark_grey", "GangHouses")
                add_box(f"{name_prefix}_Win_Jamb_L_{idx}", (wx - w_w/2.0, wy, wz), (0.05, 0.08, w_h), "kost_dark_grey", "GangHouses")
                add_box(f"{name_prefix}_Win_Jamb_R_{idx}", (wx + w_w/2.0, wy, wz), (0.05, 0.08, w_h), "kost_dark_grey", "GangHouses")
                add_box(f"{name_prefix}_Win_Mullion_{idx}", (wx, wy, wz), (0.04, 0.06, w_h), "kost_dark_grey", "GangHouses")
                add_box(f"{name_prefix}_Window_Glass_{idx}", (wx, wy + sign * 0.02, wz), (w_w - 0.08, 0.02, w_h - 0.08), "glass_frosted", "GangHouses")
                add_box(f"{name_prefix}_Win_Roster_{idx}", (wx, wy + sign * 0.02, wz + w_h/2.0 + 0.15), (w_w - 0.10, 0.04, 0.16), "roster_vent", "GangHouses")

    # ─── UNIQUE SLIDING GATE BUILDERS FOR EACH HOUSE STYLE ───
    def add_conwood_sliding_gate(name, pos, size=(1.16, 0.04, 1.0), col_name="GangHouses"):
        gx, gy, gz = pos
        gw, gd, gh = size
        parts = []
        # Modern black steel frame
        parts.append(add_box(f"{name}_Frame_Bot", (gx, gy, gz - gh/2.0 + 0.03), (gw, gd, 0.05), "iron_fence_black", col_name))
        parts.append(add_box(f"{name}_Frame_Top", (gx, gy, gz + gh/2.0 - 0.03), (gw, gd, 0.05), "iron_fence_black", col_name))
        parts.append(add_box(f"{name}_Stile_L", (gx - gw/2.0 + 0.03, gy, gz), (0.05, gd, gh), "iron_fence_black", col_name))
        parts.append(add_box(f"{name}_Stile_R", (gx + gw/2.0 - 0.03, gy, gz), (0.05, gd, gh), "iron_fence_black", col_name))
        # 5 Horizontal conwood teak slats
        slat_w = gw - 0.08
        for si, sz_off in enumerate([-0.32, -0.16, 0.0, 0.16, 0.32]):
            parts.append(add_box(f"{name}_WoodSlat_{si}", (gx, gy, gz + sz_off), (slat_w, gd * 0.8, 0.11), "fence_wood_slat", col_name))
        # Modern stainless bar handle
        parts.append(add_box(f"{name}_Handle", (gx + gw/2.0 - 0.08, gy + 0.04, gz), (0.02, 0.05, 0.35), "stainless_tray", col_name))
        # Rollers
        parts.append(add_cylinder(f"{name}_Wheel_L", (gx - gw/2.0 + 0.15, gy, gz - gh/2.0 - 0.02), 0.03, 0.03, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0)))
        parts.append(add_cylinder(f"{name}_Wheel_R", (gx + gw/2.0 - 0.15, gy, gz - gh/2.0 - 0.02), 0.03, 0.03, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0)))
        # Join moving gate parts
        valid_objs = [p for p in parts if p and p.name in bpy.data.objects]
        if valid_objs:
            bpy.ops.object.select_all(action='DESELECT')
            for vo in valid_objs:
                vo.select_set(True)
            bpy.context.view_layer.objects.active = valid_objs[0]
            bpy.ops.object.join()
            joined = bpy.context.view_layer.objects.active
            joined.name = name
        # Static floor track
        add_box(f"{name}_Track", (gx + gw * 0.45, gy, 0.01), (gw * 2.1, 0.04, 0.02), "kost_dark_grey", col_name)

    def add_picket_sliding_gate(name, pos, size=(1.16, 0.04, 1.0), col_name="GangHouses"):
        gx, gy, gz = pos
        gw, gd, gh = size
        parts = []
        # White timber frame
        parts.append(add_box(f"{name}_Rail_Bot", (gx, gy, gz - 0.30), (gw, gd, 0.06), "fence_white_wood", col_name))
        parts.append(add_box(f"{name}_Rail_Top", (gx, gy, gz + 0.25), (gw, gd, 0.06), "fence_white_wood", col_name))
        parts.append(add_box(f"{name}_Stile_L", (gx - gw/2.0 + 0.04, gy, gz), (0.06, gd, gh * 0.9), "fence_white_wood", col_name))
        parts.append(add_box(f"{name}_Stile_R", (gx + gw/2.0 - 0.04, gy, gz), (0.06, gd, gh * 0.9), "fence_white_wood", col_name))
        # 5 Pointed white pickets
        for pi in range(1, 6):
            px = (gx - gw/2.0) + pi * (gw / 6.0)
            parts.append(add_box(f"{name}_Picket_{pi}", (px, gy, gz), (0.08, gd * 0.9, gh * 0.88), "fence_white_wood", col_name))
            parts.append(add_box(f"{name}_Tip_{pi}", (px, gy, gz + gh * 0.44 + 0.03), (0.06, gd * 0.9, 0.06), "fence_white_wood", col_name, rot=(0, math.radians(45), 0)))
        # Brass latch
        parts.append(add_box(f"{name}_Handle", (gx + gw/2.0 - 0.09, gy + 0.04, gz + 0.05), (0.02, 0.05, 0.12), "fence_gold_accent", col_name))
        # Rollers
        parts.append(add_cylinder(f"{name}_Wheel_L", (gx - gw/2.0 + 0.15, gy, gz - gh/2.0 - 0.02), 0.03, 0.03, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0)))
        parts.append(add_cylinder(f"{name}_Wheel_R", (gx + gw/2.0 - 0.15, gy, gz - gh/2.0 - 0.02), 0.03, 0.03, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0)))
        # Join moving gate parts
        valid_objs = [p for p in parts if p and p.name in bpy.data.objects]
        if valid_objs:
            bpy.ops.object.select_all(action='DESELECT')
            for vo in valid_objs:
                vo.select_set(True)
            bpy.context.view_layer.objects.active = valid_objs[0]
            bpy.ops.object.join()
            joined = bpy.context.view_layer.objects.active
            joined.name = name
        # Static floor track
        add_box(f"{name}_Track", (gx + gw * 0.45, gy, 0.01), (gw * 2.1, 0.04, 0.02), "kost_dark_grey", col_name)

    def add_roster_sliding_gate(name, pos, size=(1.16, 0.04, 1.0), col_name="GangHouses"):
        gx, gy, gz = pos
        gw, gd, gh = size
        parts = []
        # Emerald green steel frame
        parts.append(add_box(f"{name}_Frame_Bot", (gx, gy, gz - gh/2.0 + 0.03), (gw, gd, 0.05), "fence_emerald_green", col_name))
        parts.append(add_box(f"{name}_Frame_Top", (gx, gy, gz + gh/2.0 - 0.03), (gw, gd, 0.05), "fence_emerald_green", col_name))
        parts.append(add_box(f"{name}_Stile_L", (gx - gw/2.0 + 0.03, gy, gz), (0.05, gd, gh), "fence_emerald_green", col_name))
        parts.append(add_box(f"{name}_Stile_R", (gx + gw/2.0 - 0.03, gy, gz), (0.05, gd, gh), "fence_emerald_green", col_name))
        parts.append(add_box(f"{name}_Mid_Rail", (gx, gy, gz), (gw, gd, 0.04), "fence_emerald_green", col_name))
        # Lower panel: terracotta roster blocks
        parts.append(add_box(f"{name}_Roster_Panel", (gx, gy, gz - 0.22), (gw - 0.08, gd * 0.8, 0.38), "fence_terracotta", col_name))
        for ri, rx_off in enumerate([-0.35, -0.12, 0.12, 0.35]):
            parts.append(add_box(f"{name}_Roster_Slot_{ri}", (gx + rx_off, gy, gz - 0.22), (0.10, gd, 0.20), "drain_trench", col_name))
        # Upper panel: 3 horizontal emerald bars
        for bi, bz in enumerate([0.15, 0.28, 0.41]):
            parts.append(add_box(f"{name}_Bar_{bi}", (gx, gy, gz + bz), (gw - 0.08, gd * 0.6, 0.03), "fence_emerald_green", col_name))
        # Silver handle
        parts.append(add_box(f"{name}_Handle", (gx + gw/2.0 - 0.08, gy + 0.04, gz + 0.05), (0.02, 0.06, 0.22), "stainless_tray", col_name))
        # Rollers
        parts.append(add_cylinder(f"{name}_Wheel_L", (gx - gw/2.0 + 0.15, gy, gz - gh/2.0 - 0.02), 0.03, 0.03, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0)))
        parts.append(add_cylinder(f"{name}_Wheel_R", (gx + gw/2.0 - 0.15, gy, gz - gh/2.0 - 0.02), 0.03, 0.03, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0)))
        # Join moving gate parts
        valid_objs = [p for p in parts if p and p.name in bpy.data.objects]
        if valid_objs:
            bpy.ops.object.select_all(action='DESELECT')
            for vo in valid_objs:
                vo.select_set(True)
            bpy.context.view_layer.objects.active = valid_objs[0]
            bpy.ops.object.join()
            joined = bpy.context.view_layer.objects.active
            joined.name = name
        # Static floor track
        add_box(f"{name}_Track", (gx + gw * 0.45, gy, 0.01), (gw * 2.1, 0.04, 0.02), "kost_dark_grey", col_name)

    def add_spearhead_sliding_gate(name, pos, size=(1.16, 0.04, 1.0), col_name="GangHouses"):
        gx, gy, gz = pos
        gw, gd, gh = size
        parts = []
        # Classic wrought iron frame
        parts.append(add_box(f"{name}_Frame_Bot", (gx, gy, gz - gh/2.0 + 0.03), (gw, gd, 0.05), "iron_fence_black", col_name))
        parts.append(add_box(f"{name}_Frame_Top", (gx, gy, gz + 0.35), (gw, gd, 0.04), "iron_fence_black", col_name))
        parts.append(add_box(f"{name}_Stile_L", (gx - gw/2.0 + 0.03, gy, gz), (0.05, gd, gh * 0.9), "iron_fence_black", col_name))
        parts.append(add_box(f"{name}_Stile_R", (gx + gw/2.0 - 0.03, gy, gz), (0.05, gd, gh * 0.9), "iron_fence_black", col_name))
        parts.append(add_box(f"{name}_Mid_Rail", (gx, gy, gz - 0.10), (gw, gd, 0.03), "iron_fence_black", col_name))
        # 5 Vertical pickets with golden spearhead finials
        for pi in range(1, 6):
            px = (gx - gw/2.0) + pi * (gw / 6.0)
            parts.append(add_box(f"{name}_Picket_{pi}", (px, gy, gz - 0.02), (0.025, gd * 0.7, 0.86), "iron_fence_black", col_name))
            parts.append(add_box(f"{name}_Spear_{pi}", (px, gy, gz + 0.45), (0.04, gd * 0.9, 0.08), "fence_gold_accent", col_name, rot=(0, math.radians(45), 0)))
        # Gold/brass pull handle
        parts.append(add_box(f"{name}_Handle", (gx + gw/2.0 - 0.08, gy + 0.04, gz), (0.02, 0.06, 0.18), "fence_gold_accent", col_name))
        # Rollers
        parts.append(add_cylinder(f"{name}_Wheel_L", (gx - gw/2.0 + 0.15, gy, gz - gh/2.0 - 0.02), 0.03, 0.03, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0)))
        parts.append(add_cylinder(f"{name}_Wheel_R", (gx + gw/2.0 - 0.15, gy, gz - gh/2.0 - 0.02), 0.03, 0.03, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0)))
        # Join moving gate parts
        valid_objs = [p for p in parts if p and p.name in bpy.data.objects]
        if valid_objs:
            bpy.ops.object.select_all(action='DESELECT')
            for vo in valid_objs:
                vo.select_set(True)
            bpy.context.view_layer.objects.active = valid_objs[0]
            bpy.ops.object.join()
            joined = bpy.context.view_layer.objects.active
            joined.name = name
        # Static floor track
        add_box(f"{name}_Track", (gx + gw * 0.45, gy, 0.01), (gw * 2.1, 0.04, 0.02), "kost_dark_grey", col_name)

    def add_bronze_sliding_gate(name, pos, size=(1.16, 0.04, 1.0), col_name="GangHouses"):
        gx, gy, gz = pos
        gw, gd, gh = size
        parts = []
        # Metallic bronze frame
        parts.append(add_box(f"{name}_Frame_Bot", (gx, gy, gz - gh/2.0 + 0.03), (gw, gd, 0.05), "fence_bronze", col_name))
        parts.append(add_box(f"{name}_Frame_Top", (gx, gy, gz + gh/2.0 - 0.03), (gw, gd, 0.05), "fence_bronze", col_name))
        parts.append(add_box(f"{name}_Stile_L", (gx - gw/2.0 + 0.03, gy, gz), (0.05, gd, gh), "fence_bronze", col_name))
        parts.append(add_box(f"{name}_Stile_R", (gx + gw/2.0 - 0.03, gy, gz), (0.05, gd, gh), "fence_bronze", col_name))
        # 8 Dense vertical bronze louvers
        for pi in range(1, 9):
            px = (gx - gw/2.0) + pi * (gw / 9.0)
            parts.append(add_box(f"{name}_Louver_{pi}", (px, gy, gz), (0.02, gd * 0.9, gh - 0.08), "fence_bronze", col_name))
        # Dark iron recessed handle
        parts.append(add_box(f"{name}_Handle", (gx + gw/2.0 - 0.08, gy + 0.04, gz), (0.02, 0.05, 0.30), "iron_fence_black", col_name))
        # Rollers
        parts.append(add_cylinder(f"{name}_Wheel_L", (gx - gw/2.0 + 0.15, gy, gz - gh/2.0 - 0.02), 0.03, 0.03, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0)))
        parts.append(add_cylinder(f"{name}_Wheel_R", (gx + gw/2.0 - 0.15, gy, gz - gh/2.0 - 0.02), 0.03, 0.03, "kost_dark_grey", col_name, rot=(math.radians(90), 0, 0)))
        # Join moving gate parts
        valid_objs = [p for p in parts if p and p.name in bpy.data.objects]
        if valid_objs:
            bpy.ops.object.select_all(action='DESELECT')
            for vo in valid_objs:
                vo.select_set(True)
            bpy.context.view_layer.objects.active = valid_objs[0]
            bpy.ops.object.join()
            joined = bpy.context.view_layer.objects.active
            joined.name = name
        # Static floor track
        add_box(f"{name}_Track", (gx + gw * 0.45, gy, 0.01), (gw * 2.1, 0.04, 0.02), "kost_dark_grey", col_name)

    # ──────── HOUSE 1 (2-Story Residence with Modern Conwood & Steel Fence) ────────
    add_box("House1_FrontLawn-col", (-1.5, -3.8, 0.02), (7.8, 3.0, 0.05), "grass_lawn", "GangHouses")
    for step_y in [-2.8, -3.5, -4.2, -4.9]:
        add_box(f"House1_Step_{step_y}", (0.8, step_y, 0.05), (0.7, 0.45, 0.03), "kost_concrete_grey", "GangHouses")

    # Front Fence: White concrete dwarf wall base with dark steel frame and horizontal warm conwood slats
    add_box("House1_Base_L-col", (-3.05, -2.25, 0.18), (6.1, 0.18, 0.36), "kost_wall_white", "GangHouses")
    add_box("House1_Base_Cap_L", (-3.05, -2.25, 0.38), (6.14, 0.22, 0.05), "kost_dark_grey", "GangHouses")
    add_box("House1_Steel_Frame_L-col", (-3.05, -2.25, 0.72), (6.1, 0.06, 0.64), "iron_fence_black", "GangHouses")
    for sz in [0.48, 0.62, 0.76, 0.90]:
        add_box(f"House1_Wood_Slat_L_{sz}", (-3.05, -2.25, sz), (6.0, 0.04, 0.10), "fence_wood_slat", "GangHouses")

    # Modern White Gate Pillars with Charcoal Cap
    add_box("House1_Gate_Post_L-col", (0.0, -2.25, 0.65), (0.28, 0.28, 1.30), "kost_wall_white", "GangHouses")
    add_box("House1_Gate_Post_L_Cap", (0.0, -2.25, 1.32), (0.32, 0.32, 0.06), "kost_dark_grey", "GangHouses")
    add_box("House1_Gate_Post_R-col", (1.2, -2.25, 0.65), (0.28, 0.28, 1.30), "kost_wall_white", "GangHouses")
    add_box("House1_Gate_Post_R_Cap", (1.2, -2.25, 1.32), (0.32, 0.32, 0.06), "kost_dark_grey", "GangHouses")

    # Sliding Gate: Conwood Wood Slat + Black Steel
    add_conwood_sliding_gate("SlidingGate_House1", (0.6, -2.22, 0.5), size=(1.16, 0.04, 1.0))

    # Right Section (X = 1.2 to 3.5)
    add_box("House1_Base_R-col", (2.35, -2.25, 0.18), (2.3, 0.18, 0.36), "kost_wall_white", "GangHouses")
    add_box("House1_Base_Cap_R", (2.35, -2.25, 0.38), (2.34, 0.22, 0.05), "kost_dark_grey", "GangHouses")
    add_box("House1_Steel_Frame_R-col", (2.35, -2.25, 0.72), (2.3, 0.06, 0.64), "iron_fence_black", "GangHouses")
    for sz in [0.48, 0.62, 0.76, 0.90]:
        add_box(f"House1_Wood_Slat_R_{sz}", (2.35, -2.25, sz), (2.2, 0.04, 0.10), "fence_wood_slat", "GangHouses")

    # House 1 Side Enclosure Wall (East Boundary connecting front fence to main building)
    add_box("House1_Side_Wall_E-col", (3.5, -3.625, 0.5), (0.18, 2.75, 1.0), "kost_wall_white", "GangHouses")
    add_box("House1_Side_Wall_E_Cap", (3.5, -3.625, 1.02), (0.22, 2.77, 0.05), "kost_dark_grey", "GangHouses")

    # House 1 Main Structure
    add_box("House1_Main_Building-col", (-1.5, -7.8, 2.6), (7.6, 5.6, 5.2), "kost_wall_white", "GangHouses")
    add_box("House1_Roof-col", (-1.5, -7.8, 5.3), (8.0, 6.0, 0.4), "tile_roof_brown", "GangHouses")
    add_box("House1_Roof_Ridge", (-1.5, -7.8, 5.52), (8.1, 0.25, 0.12), "roof_ridge_dark", "GangHouses")

    # Ground Floor Entrance
    add_house_entrance("House1_GF", (0.8, -4.96, 0.0), [(-2.6, -4.96, 1.35, 2.6, 1.3)], face_axis='Y', sign=1)
    add_kwh_meter("House1_KWH", (1.6, -4.96, 1.5), face_axis='Y', sign=1, col_name="GangHouses")
    add_ac_unit("House1_AC", (-4.2, -4.96, 2.3), face_axis='Y', sign=1, col_name="GangHouses")

    # House 1 2nd Floor Balcony
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

    # 2nd Floor Balcony Entrance (EXACT SAME DOOR & WINDOW ARCHITECTURE AS 1F!)
    add_house_entrance("House1_2F", (0.8, -4.96, 2.85), [(-2.6, -4.96, 4.20, 2.6, 1.3)], face_axis='Y', sign=1)

    # ──────── HOUSE 2 (Tosca House - TANPA PAGAR / OPEN FRONT TERRACE) ────────
    add_box("House2_Main_Building-col", (-10.5, -7.0, 1.8), (8.8, 6.8, 3.6), "wall_tosca", "GangHouses")
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

    # OPEN FRONT TERRACE (ZERO FENCE, ZERO GATES - Terbuka Ramah ke Gang)
    add_box("House2_Front_Terrace-col", (-10.5, -2.85, 0.04), (8.8, 1.25, 0.08), "kost_floor_paving", "GangHouses")
    add_cylinder("House2_Front_Pot_0", (-12.5, -2.4, 0.16), 0.18, 0.32, "brick_red", "GangHouses", vertices=8)
    add_bush_clump("House2_Front_Bush_0", (-12.5, -2.4, 0.34), 0.24, "GangHouses", flower_mat="flower_magenta")
    add_cylinder("House2_Front_Pot_1", (-7.2, -2.4, 0.16), 0.18, 0.32, "paint_bucket", "GangHouses", vertices=8)
    add_bush_clump("House2_Front_Bush_1", (-7.2, -2.4, 0.34), 0.24, "GangHouses", flower_mat="flower_yellow")

    # House 2 Side Boundary Walls (West with House 5 & East with House 1)
    add_box("House2_Side_Wall_W-col", (-15.0, -4.625, 0.5), (0.15, 4.75, 1.0), "kost_concrete_grey", "GangHouses")
    add_box("House2_Side_Wall_W_Cap", (-15.0, -4.625, 1.02), (0.19, 4.77, 0.05), "curb_concrete", "GangHouses")
    add_box("House2_Side_Wall_E-col", (-6.1, -3.625, 0.5), (0.15, 2.75, 1.0), "kost_concrete_grey", "GangHouses")
    add_box("House2_Side_Wall_E_Cap", (-6.1, -3.625, 1.02), (0.19, 2.77, 0.05), "curb_concrete", "GangHouses")

    # House 2 Jemuran - Relocated to west terrace of House 2, away from boundary wall (decoration only)
    add_box("House2_Jemuran_Frame_L", (-14.1, -3.1, 0.65), (0.03, 0.55, 1.3), "kost_railing_metal", "GangHouses")
    add_box("House2_Jemuran_Frame_R", (-12.7, -3.1, 0.65), (0.03, 0.55, 1.3), "kost_railing_metal", "GangHouses")
    add_box("House2_Jemuran_Baju_Red", (-13.7, -3.1, 0.75), (0.45, 0.03, 0.6), "clothes_red", "GangHouses")
    add_box("House2_Jemuran_Handuk_Blue", (-13.2, -3.1, 0.70), (0.45, 0.03, 0.7), "clothes_blue", "GangHouses")
    add_box("House2_Jemuran_Baju_Yellow", (-12.8, -3.1, 0.75), (0.35, 0.03, 0.55), "clothes_yellow", "GangHouses")

    # ──────── HOUSE 3 (Warm Yellow House with Classic White Picket Fence) ────────
    add_box("House3_Main_Building-col", (8.0, -7.0, 1.8), (9.0, 6.8, 3.6), "wall_yellow", "GangHouses")
    add_box("House3_Roof-col", (8.0, -7.0, 3.9), (9.4, 7.2, 0.8), "tin_roof", "GangHouses")
    add_box("House3_Roof_Ridge", (8.0, -7.0, 4.35), (9.5, 0.25, 0.12), "roof_ridge_dark", "GangHouses")
    add_tv_antenna("House3_Antenna", (10.0, -7.0, 4.3), height=2.0, col_name="GangHouses")
    add_kwh_meter("House3_KWH", (5.4, -3.56, 1.5), face_axis='Y', sign=1, col_name="GangHouses")

    add_house_entrance("House3", (6.5, -3.56, 0.0), [(4.8, -3.56, 1.4, 1.2, 1.1), (9.5, -3.56, 1.4, 1.2, 1.1)], face_axis='Y', sign=1)
    add_box("House3_Yard-col", (8.0, -3.5, 0.02), (8.8, 2.4, 0.05), "kost_floor_paving", "GangHouses")

    # Classic White Timber Gateposts
    add_box("House3_Gate_Post_L-col", (7.2, -2.25, 0.55), (0.18, 0.18, 1.10), "fence_white_wood", "GangHouses")
    add_box("House3_Gate_Post_L_Cap", (7.2, -2.25, 1.12), (0.22, 0.22, 0.06), "fence_white_wood", "GangHouses")
    add_box("House3_Gate_Post_R-col", (8.4, -2.25, 0.55), (0.18, 0.18, 1.10), "fence_white_wood", "GangHouses")
    add_box("House3_Gate_Post_R_Cap", (8.4, -2.25, 1.12), (0.22, 0.22, 0.06), "fence_white_wood", "GangHouses")

    # White Picket Fence Left Section (X = 3.5 to 7.2)
    add_box("House3_Fence_L-col", (5.35, -2.25, 0.5), (3.7, 0.08, 0.95), "fence_white_wood", "GangHouses")
    # Sliding Gate: White Pickets
    add_picket_sliding_gate("SlidingGate_House3", (7.8, -2.22, 0.5), size=(1.16, 0.04, 1.0))
    # White Picket Fence Right Section (X = 8.4 to 13.0)
    add_box("House3_Fence_R-col", (10.7, -2.25, 0.5), (4.6, 0.08, 0.95), "fence_white_wood", "GangHouses")

    # House 3 Side Enclosure Wall (East Boundary with House 6)
    add_box("House3_Side_Wall_E-col", (13.0, -4.625, 0.5), (0.15, 4.75, 1.0), "fence_white_wood", "GangHouses")
    add_box("House3_Side_Wall_E_Cap", (13.0, -4.625, 1.02), (0.19, 4.77, 0.05), "curb_concrete", "GangHouses")

    # Blue Trash Drum - placed neatly behind curb in front of House 3 fence post (no clipping with curb or wall)
    add_cylinder("House3_Trash_Drum", (7.0, -2.35, 0.38), 0.26, 0.76, "pvc_blue", "GangHouses", vertices=8)
    add_cylinder("House3_Trash_Lid", (7.0, -2.35, 0.78), 0.28, 0.06, "kost_dark_grey", "GangHouses", vertices=8)

    # ──────── HOUSE 4 (North Side House - TANPA PAGAR / OPEN FRONT TERRACE) ────────
    add_box("House4_North-col", (-20.0, 7.0, 1.8), (9.5, 8.5, 3.6), "wall_tosca", "GangHouses")
    add_box("House4_North_Roof-col", (-20.0, 7.0, 3.9), (9.8, 8.8, 0.8), "tile_roof_brown", "GangHouses")
    add_box("House4_Roof_Ridge", (-20.0, 7.0, 4.35), (9.9, 0.25, 0.12), "roof_ridge_dark", "GangHouses")
    add_house_entrance("House4", (-18.0, 2.71, 0.0), [(-21.5, 2.71, 1.4, 1.3, 1.1), (-16.0, 2.71, 1.4, 1.1, 1.1)], face_axis='Y', sign=-1)
    add_box("House4_Porch-col", (-18.0, 2.0, 0.06), (3.0, 1.4, 0.12), "kost_floor_paving", "GangHouses")
    add_box("House4_Awning", (-18.0, 2.0, 2.5), (3.2, 1.6, 0.06), "tin_roof", "GangHouses")

    # OPEN FRONT TERRACE FOR HOUSE 4 (ZERO FENCE, ZERO GATES - Terbuka Ramah ke Gang)
    add_box("House4_Front_Terrace-col", (-18.750, 2.4075, 0.040), (7.500, 0.565, 0.080), "kost_floor_paving", "GangHouses")
    add_cylinder("House4_Front_Pot_0", (-22.5, 2.4, 0.16), 0.18, 0.32, "paint_bucket", "GangHouses", vertices=8)
    add_bush_clump("House4_Front_Bush_0", (-22.5, 2.4, 0.34), 0.24, "GangHouses", flower_mat="flower_magenta")
    add_cylinder("House4_Front_Pot_1", (-15.5, 2.4, 0.16), 0.18, 0.32, "brick_red", "GangHouses", vertices=8)
    add_bush_clump("House4_Front_Bush_1", (-15.5, 2.4, 0.34), 0.24, "GangHouses", flower_mat="flower_yellow")

    # House 4 Side Enclosure Walls (West & East Boundaries)
    add_box("House4_Side_Wall_W-col", (-24.0, 4.625, 0.5), (0.15, 4.75, 1.0), "kost_concrete_grey", "GangHouses")
    add_box("House4_Side_Wall_W_Cap", (-24.0, 4.625, 1.02), (0.19, 4.77, 0.05), "curb_concrete", "GangHouses")
    add_box("House4_Side_Wall_E-col", (-14.0, 4.625, 0.5), (0.15, 4.75, 1.0), "kost_concrete_grey", "GangHouses")
    add_box("House4_Side_Wall_E_Cap", (-14.0, 4.625, 1.02), (0.19, 4.77, 0.05), "curb_concrete", "GangHouses")

    # ──────── HOUSE 5 (South House with Red Brick & Spearhead Wrought Iron) ────────
    add_box("House5_South-col", (-20.0, -7.0, 1.8), (9.5, 7.0, 3.6), "wall_cream", "GangHouses")
    add_box("House5_South_Roof-col", (-20.0, -7.0, 3.9), (9.8, 7.4, 0.8), "tile_roof_brown", "GangHouses")
    add_box("House5_Roof_Ridge", (-20.0, -7.0, 4.35), (9.9, 0.25, 0.12), "roof_ridge_dark", "GangHouses")
    add_house_entrance("House5", (-18.5, -3.46, 0.0), [(-21.5, -3.46, 1.4, 1.4, 1.1), (-16.2, -3.46, 1.4, 1.1, 1.1)], face_axis='Y', sign=1)
    add_box("House5_Terrace-col", (-18.5, -2.85, 0.05), (4.5, 1.2, 0.1), "kost_floor_paving", "GangHouses")

    # Exposed Red Brick Base with Wrought Iron Spearhead Railing (X = -24.0 to -15.0)
    add_box("House5_Brick_Base_L-col", (-21.6, -2.25, 0.18), (4.8, 0.22, 0.36), "brick_red", "GangHouses")
    add_box("House5_Brick_Cap_L", (-21.6, -2.25, 0.38), (4.84, 0.24, 0.05), "curb_concrete", "GangHouses")
    add_box("House5_Iron_L-col", (-21.6, -2.25, 0.72), (4.8, 0.06, 0.64), "iron_fence_black", "GangHouses")

    # Stately Red Brick Pillars
    add_box("House5_Gate_Post_L-col", (-19.2, -2.30, 0.65), (0.34, 0.34, 1.30), "brick_red", "GangHouses")
    add_box("House5_Gate_Post_L_Cap", (-19.2, -2.30, 1.32), (0.38, 0.38, 0.06), "curb_concrete", "GangHouses")
    add_box("House5_Gate_Post_R-col", (-18.0, -2.30, 0.65), (0.34, 0.34, 1.30), "brick_red", "GangHouses")
    add_box("House5_Gate_Post_R_Cap", (-18.0, -2.30, 1.32), (0.38, 0.38, 0.06), "curb_concrete", "GangHouses")

    add_spearhead_sliding_gate("SlidingGate_House5", (-18.6, -2.22, 0.5), size=(1.16, 0.04, 1.0))

    add_box("House5_Brick_Base_R-col", (-16.5, -2.25, 0.18), (3.0, 0.22, 0.36), "brick_red", "GangHouses")
    add_box("House5_Brick_Cap_R", (-16.5, -2.25, 0.38), (3.04, 0.24, 0.05), "curb_concrete", "GangHouses")
    add_box("House5_Iron_R-col", (-16.5, -2.25, 0.72), (3.0, 0.06, 0.64), "iron_fence_black", "GangHouses")

    # House 5 Side Enclosure Wall (West Boundary)
    add_box("House5_Side_Wall_W-col", (-24.0, -4.625, 0.5), (0.15, 4.75, 1.0), "kost_concrete_grey", "GangHouses")
    add_box("House5_Side_Wall_W_Cap", (-24.0, -4.625, 1.02), (0.19, 4.77, 0.05), "curb_concrete", "GangHouses")

    for i, px in enumerate([-17.2, -16.5, -15.8]):
        pot_mat = "paint_bucket" if i % 2 == 0 else "brick_red"
        add_cylinder(f"House5_Pot_{i}", (px, -2.8, 0.18), 0.14, 0.30, pot_mat, "GangHouses", vertices=8)
        flw_mat = "flower_magenta" if i == 0 else ("flower_yellow" if i == 1 else "flower_magenta")
        add_bush_clump(f"House5_Plant_{i}", (px, -2.8, 0.32), 0.22, "GangHouses", flower_mat=flw_mat)

    # ──────── HOUSE 6 (East House with Natural Stone & Metallic Bronze Louvers) ────────
    add_box("House6_East-col", (17.5, -7.0, 1.8), (8.5, 6.8, 3.6), "wall_cream", "GangHouses")
    add_box("House6_East_Roof-col", (17.5, -7.0, 3.9), (8.8, 7.2, 0.8), "tile_roof_brown", "GangHouses")
    add_box("House6_Roof_Ridge", (17.5, -7.0, 4.35), (8.9, 0.25, 0.12), "roof_ridge_dark", "GangHouses")
    add_house_entrance("House6", (15.5, -3.56, 0.0), [(18.5, -3.56, 1.4, 1.4, 1.1)], face_axis='Y', sign=1)

    # Natural Stone Foundation with Bronze Vertical Louver Fence (X = 13.0 to 22.0)
    add_box("House6_Stone_Base_L-col", (14.5, -2.25, 0.18), (3.0, 0.22, 0.36), "fence_stone_base", "GangHouses")
    add_box("House6_Stone_Cap_L", (14.5, -2.25, 0.38), (3.04, 0.24, 0.05), "curb_concrete", "GangHouses")
    add_box("House6_Bronze_L-col", (14.5, -2.25, 0.72), (3.0, 0.06, 0.64), "fence_bronze", "GangHouses")

    # Natural Stone Gateposts
    add_box("House6_Gate_Post_L-col", (16.0, -2.30, 0.65), (0.30, 0.30, 1.30), "fence_stone_base", "GangHouses")
    add_box("House6_Gate_Post_L_Cap", (16.0, -2.30, 1.32), (0.34, 0.34, 0.06), "curb_concrete", "GangHouses")
    add_box("House6_Gate_Post_R-col", (17.2, -2.30, 0.65), (0.30, 0.30, 1.30), "fence_stone_base", "GangHouses")
    add_box("House6_Gate_Post_R_Cap", (17.2, -2.30, 1.32), (0.34, 0.34, 0.06), "curb_concrete", "GangHouses")

    add_bronze_sliding_gate("SlidingGate_House6", (16.6, -2.22, 0.5), size=(1.16, 0.04, 1.0))

    add_box("House6_Stone_Base_R-col", (19.6, -2.25, 0.18), (4.8, 0.22, 0.36), "fence_stone_base", "GangHouses")
    add_box("House6_Stone_Cap_R", (19.6, -2.25, 0.38), (4.84, 0.24, 0.05), "curb_concrete", "GangHouses")
    add_box("House6_Bronze_R-col", (19.6, -2.25, 0.72), (4.8, 0.06, 0.64), "fence_bronze", "GangHouses")

    # House 6 Side Enclosure Wall (East Boundary near teleport portal)
    add_box("House6_Side_Wall_E-col", (22.0, -4.625, 0.5), (0.15, 4.75, 1.0), "kost_concrete_grey", "GangHouses")
    add_box("House6_Side_Wall_E_Cap", (22.0, -4.625, 1.02), (0.19, 4.77, 0.05), "curb_concrete", "GangHouses")

    add_cylinder("House6_Tire_Planter", (14.0, -2.45, 0.16), 0.30, 0.22, "clothes_red", "GangHouses", vertices=10)
    add_bush_clump("House6_Tire_Bush", (14.0, -2.45, 0.28), 0.25, "GangHouses", flower_mat="flower_yellow")
    # ─── 12. TREES & FLORA (ZERO BANANA TREES, BEAUTIFUL FACETED TREES & PALMS) ───
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
        ("Tree_Yard_H1", (-4.5, -2.65, 0.0), 3.4, 0.15, 0.75)
    ]
    for tname, pos, th, tr, cr in stylized_trees:
        add_stylized_tree(tname, pos, th, tr, cr, col_name="GangEnvironment")

    # Leaning Coconut Palms
    add_palm_tree("Palm_West", (-25.0, 7.0, 0.0), height=5.5, col_name="GangEnvironment")
    add_palm_tree("Palm_East", (22.0, -4.5, 0.0), height=5.2, col_name="GangEnvironment")

    # Bougainvillea Bush Clumps inside house lawns and gardens (zero fence clipping)
    flower_bushes = [
        ("Bush_F1", (-3.5, -3.2, 0.0), 0.45, "flower_magenta"), # House 1 front lawn
        ("Bush_F2", (-0.8, -3.3, 0.0), 0.40, "flower_yellow"),  # House 1 front lawn
        ("Bush_F3", (2.4, -3.2, 0.0), 0.42, "flower_magenta"),  # House 1 front lawn
        ("Bush_F4", (11.2, -3.2, 0.0), 0.45, "flower_yellow"),  # House 3 front yard
        ("Bush_F5", (-14.2, 3.2, 0.0), 0.42, "flower_magenta"), # House 4 east yard
        ("Bush_F6", (7.4, 3.2, 0.0), 0.35, "flower_yellow")    # Kost east garden (cleared of Kost outer wall)
    ]
    for bname, bpos, br, bmat in flower_bushes:
        add_bush_clump(bname, bpos, br, col_name="GangEnvironment", flower_mat=bmat)

    # ─── 13. STREET LIGHT POLES, OVERHEAD WIRES & TELEPORT GATE ───
    for px, py, tag in [(-12.0, 2.2, "-12.0"), (8.30, 1.80, "8.5")]:
        add_cylinder(f"Tiang_Listrik_{tag}", (px, py, 3.5), 0.10, 7.0, "kost_concrete_grey", "GangInfrastructure", vertices=8)
        add_box(f"Trafo_Box_{tag}", (px, py, 5.5), (0.4, 0.4, 0.6), "kost_dark_grey", "GangInfrastructure")
        add_box(f"Lampu_Arm_{tag}", (px, py - 0.4, 5.8), (0.05, 0.8, 0.05), "kost_railing_metal", "GangInfrastructure")
        add_cylinder(f"Lampu_Cap_{tag}", (px, py - 0.75, 5.75), 0.15, 0.08, "kost_dark_grey", "GangInfrastructure", vertices=8)
        add_box(f"Lampu_Bulb_{tag}", (px, py - 0.75, 5.68), (0.1, 0.1, 0.1), "lamp_bulb", "GangInfrastructure")
        add_cylinder(f"Cable_Coil_{tag}", (px, py + 0.12, 4.2), 0.25, 0.06, "kost_dark_grey", "GangInfrastructure", rot=(math.radians(90), 0, 0), vertices=10)

    add_angled_bar("Kabel_Listrik_1", (-12.0, 2.1, 6.6), (8.30, 1.75, 6.6), 0.02, 0.02, "kost_dark_grey", "GangInfrastructure")
    add_angled_bar("Kabel_Listrik_2", (-12.0, 2.2, 6.4), (8.30, 1.85, 6.4), 0.02, 0.02, "kost_dark_grey", "GangInfrastructure")

    # Campus Teleport Gate
    add_box("Teleport_Pole_L-col", (20.0, 2.0, 1.8), (0.2, 0.2, 3.6), "kost_concrete_grey", "TeleportArea")
    add_box("Teleport_Pole_R-col", (20.0, -2.0, 1.8), (0.2, 0.2, 3.6), "kost_concrete_grey", "TeleportArea")
    add_box("Teleport_Beam-col", (20.0, 0.0, 3.5), (0.25, 4.2, 0.3), "kost_concrete_grey", "TeleportArea")
    add_box("Teleport_Portal_Visual", (20.0, 0.0, 1.7), (0.06, 3.6, 3.2), "teleport_cyan", "TeleportArea")
    add_box("Teleport_Sign_Board", (20.0, 0.0, 3.9), (0.08, 3.2, 0.5), "pvc_blue", "TeleportArea")
    add_angled_bar("Teleport_Chain", (20.0, -1.8, 0.6), (20.0, 1.8, 0.6), 0.04, 0.04, "kost_railing_metal", "TeleportArea")

    # ─── 14. SAVE AND EXPORT GLB ───
    blend_path = "/home/haelahpx/Documents/GitHub/gameproject01/game/new-game-project/assets/models/kampung_kos_scene.blend"
    blend_path2 = "/home/haelahpx/Documents/GitHub/gameproject01/game/new-game-project/assets/models/kampung_kos_gang.blend"
    glb_path = "/home/haelahpx/Documents/GitHub/gameproject01/game/new-game-project/assets/models/kampung_kos_gang.glb"

    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path2)
    print(f"Saved Blend files to: {blend_path} and {blend_path2}")

    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    print(f"Exported GLB to: {glb_path}")

if __name__ == "__main__":
    build_all()
