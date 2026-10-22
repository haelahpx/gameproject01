"""
Script to fix:
1. Junction connections:
   - Eliminate all unwanted sidewalk openings / gaps where roads don't branch
     ("ada yg harusnya tertutup tapi dia tidak ada"):
     * Main Boulevard at X=-75.0, Y=0.0: South sidewalk is 100% continuous and closed.
     * Middle Ring at X=-75.0, Y=38.0: North sidewalk is 100% continuous and closed.
     * Pos Ronda at X=-32.0, Y=0.0: North sidewalk is 100% continuous and closed.
     * East Connector at X=25.0, Y=0.0: North sidewalk is 100% continuous and closed.
     * West Avenue at X=-115.0, Y=38.0: West sidewalk is 100% continuous and closed.
     * Loop-84 at X=-84.0, Y=0.0: North sidewalk is 100% continuous and closed.
     * South Boulevard at Y=-60.0: South sidewalk is 100% continuous and closed.
     * Y=-22.0 road at X=-84.0: South sidewalk is 100% continuous and closed.
   - Eliminate any sidewalk / curb barriers across road entrances
     ("ada yg harusnya tidak ada penghalang tapi ada"):
     * Clear entrance into West Avenue North at X=-115.0, Y=38.0.
     * Clear entrance at X=-10.0, Y=38.0.
     * Clear entrance at X=25.0, Y=0.0.
2. Fix broken turn at X=-32.0, Y=-22.0 (Tambal Ban / Poor Kost belokan):
   - Replace jagged square corner, floating broken stripes, and missing curbs
     with a dedicated, smooth 90-degree curved corner unit:
     * 12-segment smooth curved asphalt road surface filling the bend
     * Smooth inner and outer curved sidewalks with concrete slabs
     * Alternating black-and-white curb blocks along inner and outer radiuses
     * Smooth curved dashed white center markings connecting the straight roads
3. Also provide smooth 90-degree curved corner units for all other elbow turns:
   - Corner at X=-10.0, Y=38.0 (East turn of Middle Ring)
   - Corner at X=-10.0, Y=55.0 (East turn of Upper Ring)
   - Corner at X=-115.0, Y=55.0 (West turn of Upper Ring)
   - Corner at X=-115.0, Y=-60.0 (South-West loop corner)
"""

import bpy  # pyrefly: ignore[missing-import] # type: ignore
import bmesh  # pyrefly: ignore[missing-import] # type: ignore
import math
from mathutils import Vector  # pyrefly: ignore[missing-import] # type: ignore

def run():
    print("=== Starting fix_junction_openings_and_lturn.py ===")

    # Materials
    mat_asphalt = bpy.data.materials.get("road_asphalt")
    mat_marking_white = bpy.data.materials.get("road_marking_white")
    mat_curb_concrete = bpy.data.materials.get("curb_concrete") or bpy.data.materials.get("Mat_ConcreteCurb.001")
    mat_curb_black = bpy.data.materials.get("curb_black")
    mat_curb_white = bpy.data.materials.get("curb_white")

    col_perumahan = bpy.data.collections.get("PerumahanRoads")
    if not col_perumahan:
        col_perumahan = bpy.data.collections.new("PerumahanRoads")
        bpy.context.scene.collection.children.link(col_perumahan)

    # -------------------------------------------------------------------------
    # 1. CLEAN UP ALL PREVIOUS PERUM ROADS, CURBS, AND STRIPES
    # -------------------------------------------------------------------------
    print("1. Cleaning up previous Perumahan road meshes and duplicate curb returns...")
    to_remove = []
    for o in bpy.data.objects:
        if o.name.startswith("Perum_") or o.name.startswith("CurbReturn_") or o.name.startswith("Corner_"):
            # Keep Campus intersection corners if any
            if not o.name.startswith("Perempatan_") and not o.name.startswith("WestJunc_"):
                to_remove.append(o)

    for o in to_remove:
        mesh = o.data if o.type == 'MESH' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)

    print(f"Removed {len(to_remove)} previous road/curb objects.")

    # -------------------------------------------------------------------------
    # 2. ROAD SEGMENT GENERATOR WITH INDEPENDENT LEFT/RIGHT SIDEWALK TRIMS
    # -------------------------------------------------------------------------
    def build_road_segment(name, p_start, p_end, road_width=4.2, sidewalk_width=0.70,
                           trim_left_start=0.0, trim_left_end=0.0,
                           trim_right_start=0.0, trim_right_end=0.0,
                           has_left_sw=True, has_right_sw=True, has_centerline=True,
                           col_target=col_perumahan):
        x1, y1 = p_start[0], p_start[1]
        x2, y2 = p_end[0], p_end[1]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length <= 0.1:
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
        if has_centerline and length > 2.5:
            mesh_lines = bpy.data.meshes.new(f"{name}_Stripes_Mesh")
            obj_lines = bpy.data.objects.new(f"{name}_Stripes", mesh_lines)
            bm_l = bmesh.new()

            stripe_len = 1.5
            gap_len = 1.5
            cycle = stripe_len + gap_len
            line_w = 0.12
            z_stripe = 0.003

            max_trim_start = max(trim_left_start, trim_right_start)
            max_trim_end = max(trim_left_end, trim_right_end)

            start_x = -hl + max_trim_start + 0.3
            end_x = hl - max_trim_end - 0.3
            usable_len = end_x - start_x
            if usable_len > 1.2:
                n_stripes = int(math.floor(usable_len / cycle))
                for si in range(max(1, n_stripes)):
                    sx = start_x + si * cycle
                    ex = min(sx + stripe_len, end_x)
                    if ex - sx > 0.4:
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

        # C. Sidewalks and Alternating Black/White Curbs (Independent Trims)
        curb_w = 0.14
        curb_h = 0.12
        sw_h = 0.11

        def build_side(is_left=True):
            sign = 1.0 if is_left else -1.0
            sw_name = f"{name}_SW_{'L' if is_left else 'R'}"
            t_start = trim_left_start if is_left else trim_right_start
            t_end = trim_left_end if is_left else trim_right_end

            sw_start = -hl + t_start
            sw_end = hl - t_end
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
    # 3. DEDICATED 90-DEGREE CURVED CORNER GENERATOR (SMOOTH ROAD BEND)
    # -------------------------------------------------------------------------
    def build_curved_corner_90(name, center_pt, r_center=4.0, road_width=4.0, sidewalk_width=0.70,
                               start_deg=270.0, end_deg=360.0, steps=12,
                               has_centerline=True, col_target=col_perumahan):
        cx, cy = center_pt
        t_start = math.radians(start_deg)
        t_end = math.radians(end_deg)

        hw = road_width / 2.0
        r_in = r_center - hw
        r_out = r_center + hw
        r_sw_in = r_in - sidewalk_width
        r_sw_out = r_out + sidewalk_width

        curb_w = 0.14
        curb_h = 0.12
        sw_h = 0.11

        # A. Corner Asphalt Road Pavement Mesh
        mesh_asphalt = bpy.data.meshes.new(f"{name}_Asphalt_Mesh")
        obj_asphalt = bpy.data.objects.new(f"{name}_Road-col", mesh_asphalt)
        bm_a = bmesh.new()

        verts_top_in, verts_top_out = [], []
        verts_bot_in, verts_bot_out = [], []

        for s in range(steps + 1):
            th = t_start + (s / steps) * (t_end - t_start)
            c, sn = math.cos(th), math.sin(th)
            v_ti = bm_a.verts.new((cx + r_in * c, cy + r_in * sn, 0.00))
            v_to = bm_a.verts.new((cx + r_out * c, cy + r_out * sn, 0.00))
            v_bi = bm_a.verts.new((cx + r_in * c, cy + r_in * sn, -0.08))
            v_bo = bm_a.verts.new((cx + r_out * c, cy + r_out * sn, -0.08))

            verts_top_in.append(v_ti)
            verts_top_out.append(v_to)
            verts_bot_in.append(v_bi)
            verts_bot_out.append(v_bo)

        for s in range(steps):
            # Top road surface
            bm_a.faces.new([verts_top_in[s], verts_top_out[s], verts_top_out[s + 1], verts_top_in[s + 1]])
            # Bottom surface
            bm_a.faces.new([verts_bot_in[s], verts_bot_in[s + 1], verts_bot_out[s + 1], verts_bot_out[s]])
            # Inner and outer vertical sides
            bm_a.faces.new([verts_bot_in[s], verts_top_in[s], verts_top_in[s + 1], verts_bot_in[s + 1]])
            bm_a.faces.new([verts_bot_out[s], verts_bot_out[s + 1], verts_top_out[s + 1], verts_top_out[s]])

        bm_a.to_mesh(mesh_asphalt)
        bm_a.free()
        mesh_asphalt.materials.append(mat_asphalt)
        col_target.objects.link(obj_asphalt)

        # B. Curved Center Dashed Line Markings
        if has_centerline:
            mesh_stripe = bpy.data.meshes.new(f"{name}_Stripes_Mesh")
            obj_stripe = bpy.data.objects.new(f"{name}_Stripes", mesh_stripe)
            bm_s = bmesh.new()

            line_w = 0.12
            r_c_in = r_center - line_w / 2.0
            r_c_out = r_center + line_w / 2.0

            # 2 dashes along the 90 degree arc: [15%..40%] and [60%..85%]
            dash_ranges = [(0.15, 0.40), (0.60, 0.85)]
            for d_start, d_end in dash_ranges:
                n_sub = 4
                dv_in, dv_out = [], []
                for si in range(n_sub + 1):
                    f_step = d_start + (si / n_sub) * (d_end - d_start)
                    th = t_start + f_step * (t_end - t_start)
                    c, sn = math.cos(th), math.sin(th)
                    vi = bm_s.verts.new((cx + r_c_in * c, cy + r_c_in * sn, 0.003))
                    vo = bm_s.verts.new((cx + r_c_out * c, cy + r_c_out * sn, 0.003))
                    dv_in.append(vi)
                    dv_out.append(vo)
                for si in range(n_sub):
                    bm_s.faces.new([dv_in[si], dv_out[si], dv_out[si + 1], dv_in[si + 1]])

            bm_s.to_mesh(mesh_stripe)
            bm_s.free()
            mesh_stripe.materials.append(mat_marking_white)
            col_target.objects.link(obj_stripe)

        # C. Inner Sidewalk and Curbs (Radius: r_in)
        mesh_inner_sw = bpy.data.meshes.new(f"{name}_Inner_SW_Mesh")
        obj_inner_sw = bpy.data.objects.new(f"{name}_Inner_SW-col", mesh_inner_sw)
        bm_isw = bmesh.new()

        mesh_inner_curb = bpy.data.meshes.new(f"{name}_Inner_Curb_Mesh")
        obj_inner_curb = bpy.data.objects.new(f"{name}_Inner_Curb", mesh_inner_curb)
        bm_ic = bmesh.new()

        r_ci = r_in - curb_w

        iv_in_sw, iv_mid, iv_out_sw = [], [], []
        cv_in_bot, cv_in_top, cv_out_bot, cv_out_top = [], [], [], []

        for s in range(steps + 1):
            th = t_start + (s / steps) * (t_end - t_start)
            c, sn = math.cos(th), math.sin(th)

            # Curb vertices (from r_in at road surface to r_ci at curb top)
            cv1 = bm_ic.verts.new((cx + r_in * c, cy + r_in * sn, 0.00))
            cv2 = bm_ic.verts.new((cx + r_in * c, cy + r_in * sn, curb_h))
            cv3 = bm_ic.verts.new((cx + r_ci * c, cy + r_ci * sn, curb_h))
            cv4 = bm_ic.verts.new((cx + r_ci * c, cy + r_ci * sn, 0.00))
            cv_out_bot.append(cv1)
            cv_out_top.append(cv2)
            cv_in_top.append(cv3)
            cv_in_bot.append(cv4)

            # Sidewalk slab vertices (from r_ci to r_sw_in)
            sv1 = bm_isw.verts.new((cx + r_sw_in * c, cy + r_sw_in * sn, -0.05))
            sv2 = bm_isw.verts.new((cx + r_sw_in * c, cy + r_sw_in * sn, sw_h))
            sv3 = bm_isw.verts.new((cx + r_ci * c, cy + r_ci * sn, sw_h))
            sv4 = bm_isw.verts.new((cx + r_ci * c, cy + r_ci * sn, -0.05))
            iv_in_sw.append(sv1)
            iv_out_sw.append(sv2)
            iv_mid.append(sv3)

        for s in range(steps):
            # Inner curb faces (alternating black/white)
            c_slot = 0 if (s % 2 == 0) else 1
            f_top = bm_ic.faces.new([cv_in_top[s], cv_out_top[s], cv_out_top[s + 1], cv_in_top[s + 1]])
            f_face = bm_ic.faces.new([cv_out_bot[s], cv_out_top[s], cv_out_top[s + 1], cv_out_bot[s + 1]])
            f_top.material_index = c_slot
            f_face.material_index = c_slot

            # Inner sidewalk top face
            bm_isw.faces.new([iv_out_sw[s], iv_mid[s], iv_mid[s + 1], iv_out_sw[s + 1]])

        bm_ic.to_mesh(mesh_inner_curb)
        bm_ic.free()
        mesh_inner_curb.materials.append(mat_curb_white)
        mesh_inner_curb.materials.append(mat_curb_black)
        col_target.objects.link(obj_inner_curb)

        bm_isw.to_mesh(mesh_inner_sw)
        bm_isw.free()
        mesh_inner_sw.materials.append(mat_curb_concrete)
        col_target.objects.link(obj_inner_sw)

        # D. Outer Sidewalk and Curbs (Radius: r_out)
        mesh_outer_sw = bpy.data.meshes.new(f"{name}_Outer_SW_Mesh")
        obj_outer_sw = bpy.data.objects.new(f"{name}_Outer_SW-col", mesh_outer_sw)
        bm_osw = bmesh.new()

        mesh_outer_curb = bpy.data.meshes.new(f"{name}_Outer_Curb_Mesh")
        obj_outer_curb = bpy.data.objects.new(f"{name}_Outer_Curb", mesh_outer_curb)
        bm_oc = bmesh.new()

        r_co = r_out + curb_w

        ov_in_top, ov_in_bot, ov_out_top, ov_out_bot = [], [], [], []
        ov_sw_top_in, ov_sw_top_out = [], []

        for s in range(steps + 1):
            th = t_start + (s / steps) * (t_end - t_start)
            c, sn = math.cos(th), math.sin(th)

            # Curb vertices (from r_out at road surface to r_co at curb top)
            cv1 = bm_oc.verts.new((cx + r_out * c, cy + r_out * sn, 0.00))
            cv2 = bm_oc.verts.new((cx + r_out * c, cy + r_out * sn, curb_h))
            cv3 = bm_oc.verts.new((cx + r_co * c, cy + r_co * sn, curb_h))
            cv4 = bm_oc.verts.new((cx + r_co * c, cy + r_co * sn, 0.00))
            ov_in_bot.append(cv1)
            ov_in_top.append(cv2)
            ov_out_top.append(cv3)
            ov_out_bot.append(cv4)

            # Outer sidewalk slab vertices (from r_co to r_sw_out)
            sv1 = bm_osw.verts.new((cx + r_co * c, cy + r_co * sn, sw_h))
            sv2 = bm_osw.verts.new((cx + r_sw_out * c, cy + r_sw_out * sn, sw_h))
            ov_sw_top_in.append(sv1)
            ov_sw_top_out.append(sv2)

        for s in range(steps):
            c_slot = 0 if (s % 2 == 0) else 1
            f_top = bm_oc.faces.new([ov_in_top[s], ov_out_top[s], ov_out_top[s + 1], ov_in_top[s + 1]])
            f_face = bm_oc.faces.new([ov_in_bot[s], ov_in_top[s], ov_in_top[s + 1], ov_in_bot[s + 1]])
            f_top.material_index = c_slot
            f_face.material_index = c_slot

            # Outer sidewalk top face
            bm_osw.faces.new([ov_sw_top_in[s], ov_sw_top_out[s], ov_sw_top_out[s + 1], ov_sw_top_in[s + 1]])

        bm_oc.to_mesh(mesh_outer_curb)
        bm_oc.free()
        mesh_outer_curb.materials.append(mat_curb_white)
        mesh_outer_curb.materials.append(mat_curb_black)
        col_target.objects.link(obj_outer_curb)

        bm_osw.to_mesh(mesh_outer_sw)
        bm_osw.free()
        mesh_outer_sw.materials.append(mat_curb_concrete)
        col_target.objects.link(obj_outer_sw)

        return obj_asphalt

    # -------------------------------------------------------------------------
    # 4. T-JUNCTION CORNER CURB RETURN (WITH SIDEWALK WEDGE)
    # -------------------------------------------------------------------------
    def build_corner_curb_return(name, center_pt, r=1.8, start_deg=0.0, end_deg=90.0, steps=8):
        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bm = bmesh.new()

        cx, cy = center_pt
        t_start = math.radians(start_deg)
        t_end = math.radians(end_deg)

        r_inner = r
        r_outer = r + 0.14
        r_sw = r + 0.14 + 0.70

        verts_in = []
        verts_curb_top = []
        verts_sw = []

        for s in range(steps + 1):
            th = t_start + (s / steps) * (t_end - t_start)
            cos_t, sin_t = math.cos(th), math.sin(th)
            vi = bm.verts.new((cx + r_inner * cos_t, cy + r_inner * sin_t, 0.00))
            vc = bm.verts.new((cx + r_outer * cos_t, cy + r_outer * sin_t, 0.12))
            vsw = bm.verts.new((cx + r_sw * cos_t, cy + r_sw * sin_t, 0.11))
            verts_in.append(vi)
            verts_curb_top.append(vc)
            verts_sw.append(vsw)

        for s in range(steps):
            c_slot = 0 if (s % 2 == 0) else 1
            f_curb = bm.faces.new([verts_in[s], verts_in[s + 1], verts_curb_top[s + 1], verts_curb_top[s]])
            f_curb.material_index = c_slot
            f_sw = bm.faces.new([verts_curb_top[s], verts_curb_top[s + 1], verts_sw[s + 1], verts_sw[s]])
            f_sw.material_index = 2

        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_curb_white)
        mesh.materials.append(mat_curb_black)
        mesh.materials.append(mat_curb_concrete)
        col_perumahan.objects.link(obj)
        return obj

    # =========================================================================
    # 5. BUILD THE 5 DEDICATED SMOOTH 90-DEGREE CORNERS
    # =========================================================================
    print("5. Building smooth 90-degree corner boulevards...")

    # A. Corner at X=-32.0, Y=-22.0 (Tambal Ban & Poor Kost Belokan)
    # Connects Perum_Kampung_EW_22 (ends at X=-36.0, Y=-22.0)
    # with Perum_Kampung_NS_32 (starts at X=-32.0, Y=-18.0)
    # Center: (-36.0, -18.0), R=4.0m, arc 270 deg -> 360 deg
    build_curved_corner_90("Corner_TambalBan_X32_Y22", (-36.0, -18.0),
                           r_center=4.0, road_width=4.0, sidewalk_width=0.70,
                           start_deg=270.0, end_deg=360.0, steps=12)

    # B. Corner at X=-10.0, Y=38.0 (East turn of Middle Ring)
    # Connects Perum_North_EW_38_East (ends at X=-14.0, Y=38.0)
    # with Perum_North_NS_10 (starts at X=-10.0, Y=42.0)
    # Center: (-14.0, 42.0), R=4.0m, arc 270 deg -> 360 deg
    build_curved_corner_90("Corner_MiddleRing_X10_Y38", (-14.0, 42.0),
                           r_center=4.0, road_width=4.0, sidewalk_width=0.65,
                           start_deg=270.0, end_deg=360.0, steps=12)

    # C. Corner at X=-10.0, Y=55.0 (East turn of Upper Ring)
    # Connects Perum_North_NS_10 (ends at X=-10.0, Y=51.0)
    # with Perum_North_EW_55 (starts at X=-14.0, Y=55.0)
    # Center: (-14.0, 51.0), R=4.0m, arc 0 deg -> 90 deg
    build_curved_corner_90("Corner_UpperRing_X10_Y55", (-14.0, 51.0),
                           r_center=4.0, road_width=4.0, sidewalk_width=0.65,
                           start_deg=0.0, end_deg=90.0, steps=12)

    # D. Corner at X=-115.0, Y=55.0 (West turn of Upper Ring)
    # Connects Perum_North_EW_55 (ends at X=-110.6, Y=55.0)
    # with Perum_West_Avenue_North (ends at X=-115.0, Y=50.6)
    # Center: (-110.6, 50.6), R=4.4m, arc 90 deg -> 180 deg
    build_curved_corner_90("Corner_UpperRing_West_X115_Y55", (-110.6, 50.6),
                           r_center=4.4, road_width=4.4, sidewalk_width=0.70,
                           start_deg=90.0, end_deg=180.0, steps=12)

    # E. Corner at X=-115.0, Y=-60.0 (South-West loop corner)
    # Connects Perum_West_Avenue_South2 (ends at X=-115.0, Y=-55.6)
    # with Perum_South_EW_60_West (starts at X=-110.6, Y=-60.0)
    # Center: (-110.6, -55.6), R=4.4m, arc 180 deg -> 270 deg
    build_curved_corner_90("Corner_SouthLoop_X115_Y60", (-110.6, -55.6),
                           r_center=4.4, road_width=4.4, sidewalk_width=0.70,
                           start_deg=180.0, end_deg=270.0, steps=12)

    # =========================================================================
    # 6. BUILD MAIN BOULEVARD ALONG Y=0.0 (FROM WEST AVE TO EAST AVE)
    # =========================================================================
    print("6. Building Main Boulevard with 100% closed continuous opposite sidewalks...")

    # Segment 1: West Avenue junction to Ave-115 (X in [-143.39, -115.0])
    # Start: West Ave (both sides trim 1.2). End: X=-115 4-way (both sides trim 2.4)
    build_road_segment("Perum_Main_Bvd_1", (-143.39, 0.0), (-115.0, 0.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=1.2, trim_left_end=2.4,
                       trim_right_start=1.2, trim_right_end=2.4)

    # Segment 2: Ave-115 to Loop-84 (X in [-115.0, -84.0])
    # Start: X=-115 (both trim 2.4)
    # End: X=-84 T-junction (Branch goes South! North/Left is 0.0 closed, South/Right trims 2.2)
    build_road_segment("Perum_Main_Bvd_2", (-115.0, 0.0), (-84.0, 0.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=2.4, trim_left_end=0.0,  # North is CLOSED!
                       trim_right_start=2.4, trim_right_end=2.2)

    # Segment 3: Loop-84 to Pertigaan NS-75 (X in [-84.0, -75.0])
    # Start: X=-84 T-junction (North/Left is 0.0 closed, South/Right trims 2.2)
    # End: X=-75 T-junction (Branch goes North! North/Left trims 2.3, South/Right is 0.0 CLOSED!)
    build_road_segment("Perum_Main_Bvd_3", (-84.0, 0.0), (-75.0, 0.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=0.0, trim_left_end=2.3,
                       trim_right_start=2.2, trim_right_end=0.0) # South is CLOSED!

    # Segment 4: Pertigaan NS-75 to Pos Ronda Pertigaan X=-32.0 (X in [-75.0, -32.0])
    # Start: X=-75 (North/Left trims 2.3, South/Right is 0.0 CLOSED!)
    # End: X=-32 (Branch goes South! North/Left is 0.0 CLOSED!, South/Right trims 2.2)
    build_road_segment("Perum_Main_Bvd_4", (-75.0, 0.0), (-32.0, 0.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=2.3, trim_left_end=0.0,   # North is CLOSED!
                       trim_right_start=0.0, trim_right_end=2.2) # South is CLOSED at X=-75!

    # Segment 5: Pos Ronda Pertigaan X=-32.0 to East Connector X=+25.0 (X in [-32.0, 25.0])
    # Start: X=-32 (North/Left is 0.0 CLOSED!, South/Right trims 2.2)
    # End: X=25 (Branch goes South! North/Left is 0.0 CLOSED!, South/Right trims 2.2)
    build_road_segment("Perum_Main_Bvd_5", (-32.0, 0.0), (25.0, 0.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=0.0, trim_left_end=0.0,   # North is 100% CLOSED!
                       trim_right_start=2.2, trim_right_end=2.2)

    # Segment 6: East Connector X=+25.0 to East Avenue X=56.61 (X in [25.0, 56.61])
    # Start: X=25 (North/Left is 0.0 CLOSED!, South/Right trims 2.2)
    # End: East Ave (both trim 1.2)
    build_road_segment("Perum_Main_Bvd_6", (25.0, 0.0), (56.61, 0.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=0.0, trim_left_end=1.2,   # North is CLOSED at X=25!
                       trim_right_start=2.2, trim_right_end=1.2)

    # =========================================================================
    # 7. BUILD KAMPUNG CENTRAL & SOUTH BRANCHES
    # =========================================================================
    print("7. Building Kampung branches connecting to the smooth corner...")

    # Vertical Branch at X=-32.0: runs from corner at Y=-18.0 up to Y=0.0
    # Start at Y=-18.0: seamlessly connects to Corner_TambalBan_X32_Y22 (trims 0.0)
    # End at Y=0.0: meets Main Boulevard (both sides trim 2.3 for curb returns into Bvd)
    build_road_segment("Perum_Kampung_NS_32", (-32.0, -18.0), (-32.0, 0.0),
                       road_width=4.0, sidewalk_width=0.70,
                       trim_left_start=0.0, trim_left_end=2.3,
                       trim_right_start=0.0, trim_right_end=2.3)

    # Horizontal Belokan between X=-58.0 and X=-36.0 at Y=-22.0
    # Start at X=-58.0: meets Perum_South_EW_22_Mid seamlessly (trims 0.0)
    # End at X=-36.0: connects seamlessly to Corner_TambalBan_X32_Y22 (trims 0.0)
    build_road_segment("Perum_Kampung_EW_22", (-58.0, -22.0), (-36.0, -22.0),
                       road_width=4.0, sidewalk_width=0.70,
                       trim_left_start=0.0, trim_left_end=0.0,
                       trim_right_start=0.0, trim_right_end=0.0)

    # =========================================================================
    # 8. BUILD NORTH RESIDENTIAL HOUSING ESTATE (BLOK UTARA)
    # =========================================================================
    print("8. Building Blok Utara roads...")

    # Collector North-South Road at X=-75.0 (from Y=0.0 to Y=38.0)
    # Start at Y=0: meets Boulevard (both trim 2.3 for curb returns)
    # End at Y=38: meets Middle Ring (both trim 2.3 for curb returns)
    build_road_segment("Perum_North_NS_75", (-75.0, 0.0), (-75.0, 38.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=2.3, trim_left_end=2.3,
                       trim_right_start=2.3, trim_right_end=2.3)

    # Middle East-West Ring along Y=38.0
    # West segment: from X=-112.6 (Avenue East roadway edge) to X=-75.0
    # Start at X=-112.6: clears West Avenue (both trim 0.2 for curb returns)
    # End at X=-75.0: T-junction (Branch arrives from South! North/Left is 0.0 CLOSED, South/Right trims 2.3)
    build_road_segment("Perum_North_EW_38_West", (-112.6, 38.0), (-75.0, 38.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=0.2, trim_left_end=0.0,   # North is CLOSED at X=-75!
                       trim_right_start=0.2, trim_right_end=2.3)

    # East segment: from X=-75.0 to X=-14.0 (corner unit)
    # Start at X=-75.0: North/Left is 0.0 CLOSED, South/Right trims 2.3
    # End at X=-14.0: connects seamlessly to Corner_MiddleRing_X10_Y38 (trims 0.0)
    build_road_segment("Perum_North_EW_38_East", (-75.0, 38.0), (-14.0, 38.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=0.0, trim_left_end=0.0,   # North is CLOSED at X=-75!
                       trim_right_start=2.3, trim_right_end=0.0)

    # Upper Ring along Y=55.0 (from X=-110.6 to X=-14.0)
    # Connects seamlessly between Corner_UpperRing_West and Corner_UpperRing_East
    build_road_segment("Perum_North_EW_55", (-110.6, 55.0), (-14.0, 55.0),
                       road_width=4.0, sidewalk_width=0.65,
                       trim_left_start=0.0, trim_left_end=0.0,
                       trim_right_start=0.0, trim_right_end=0.0)

    # East Vertical Connector of Upper Ring (at X=-10.0, from Y=42.0 to Y=51.0)
    # Connects seamlessly between Corner_MiddleRing (at Y=42) and Corner_UpperRing (at Y=51)
    build_road_segment("Perum_North_NS_10", (-10.0, 42.0), (-10.0, 51.0),
                       road_width=4.0, sidewalk_width=0.65,
                       trim_left_start=0.0, trim_left_end=0.0,
                       trim_right_start=0.0, trim_right_end=0.0)

    # West Primary Residential Avenue at X=-115.0
    # North segment: from Y=38.0 to Y=50.6 (corner unit)
    # Start at Y=38.0: West/Left is 0.0 CLOSED! East/Right trims 2.3 (opens into EW_38_West)
    # End at Y=50.6: connects seamlessly to Corner_UpperRing_West (trims 0.0)
    build_road_segment("Perum_West_Avenue_North", (-115.0, 38.0), (-115.0, 50.6),
                       road_width=4.8, sidewalk_width=0.75,
                       trim_left_start=0.0, trim_left_end=0.0,   # West is 100% CLOSED!
                       trim_right_start=2.3, trim_right_end=0.0)

    # Mid segment: from Y=0.0 to Y=38.0
    # Start at Y=0.0: 4-way intersection (both trim 2.3)
    # End at Y=38.0: West/Left is 0.0 CLOSED! East/Right trims 2.3 (opens into EW_38_West)
    build_road_segment("Perum_West_Avenue_Mid", (-115.0, 0.0), (-115.0, 38.0),
                       road_width=4.8, sidewalk_width=0.75,
                       trim_left_start=2.3, trim_left_end=0.0,   # West is 100% CLOSED!
                       trim_right_start=2.3, trim_right_end=2.3)

    # South1 segment: from Y=-22.0 to Y=0.0
    # Start at Y=-22.0: West/Left is 0.0 CLOSED! East/Right trims 2.3 (opens into EW_22_West)
    # End at Y=0.0: 4-way intersection (both trim 2.3)
    build_road_segment("Perum_West_Avenue_South1", (-115.0, -22.0), (-115.0, 0.0),
                       road_width=4.8, sidewalk_width=0.75,
                       trim_left_start=0.0, trim_left_end=2.3,   # West is 100% CLOSED!
                       trim_right_start=2.3, trim_right_end=2.3)

    # South2 segment: from Y=-55.6 (corner unit) to Y=-22.0
    # Start at Y=-55.6: connects seamlessly to Corner_SouthLoop (trims 0.0)
    # End at Y=-22.0: West/Left is 0.0 CLOSED! East/Right trims 2.3 (opens into EW_22_West)
    build_road_segment("Perum_West_Avenue_South2", (-115.0, -55.6), (-115.0, -22.0),
                       road_width=4.8, sidewalk_width=0.75,
                       trim_left_start=0.0, trim_left_end=0.0,   # West is 100% CLOSED!
                       trim_right_start=0.0, trim_right_end=2.3)

    # =========================================================================
    # 9. BUILD SOUTH RESIDENTIAL BLOCK (BLOK SELATAN)
    # =========================================================================
    print("9. Building Blok Selatan roads...")

    # West Loop at X=-84.0 (from Y=-22.0 to Y=0.0)
    # Start at Y=-22.0: meets EW_22 (both trim 2.2)
    # End at Y=0.0: meets Main Boulevard (both trim 2.3)
    build_road_segment("Perum_West_Loop_NS_84", (-84.0, -22.0), (-84.0, 0.0),
                       road_width=4.0, sidewalk_width=0.70,
                       trim_left_start=2.2, trim_left_end=2.3,
                       trim_right_start=2.2, trim_right_end=2.3)

    # EW_22_Mid: from X=-84.0 to X=-58.0
    # Start at X=-84.0: T-junction (Branch from North! North/Left trims 2.2, South/Right is 0.0 CLOSED!)
    # End at X=-58.0: straight joint with Perum_Kampung_EW_22 (both trim 0.0)
    build_road_segment("Perum_South_EW_22_Mid", (-84.0, -22.0), (-58.0, -22.0),
                       road_width=4.0, sidewalk_width=0.70,
                       trim_left_start=2.2, trim_left_end=0.0,
                       trim_right_start=0.0, trim_right_end=0.0) # South is 100% CLOSED!

    # EW_22_West: from X=-112.6 (Avenue East roadway edge) to X=-84.0
    # Start at X=-112.6: clears West Avenue (both trim 0.2)
    # End at X=-84.0: North/Left trims 2.2, South/Right is 0.0 CLOSED!
    build_road_segment("Perum_South_EW_22_West", (-112.6, -22.0), (-84.0, -22.0),
                       road_width=4.0, sidewalk_width=0.70,
                       trim_left_start=0.2, trim_left_end=2.2,
                       trim_right_start=0.2, trim_right_end=0.0) # South is 100% CLOSED!

    # South_NS_75: from Y=-60.0 to Y=-22.0
    # Start at Y=-60.0: meets South Boulevard (both trim 2.3)
    # End at Y=-22.0: dead end / connector (both trim 0.0)
    build_road_segment("Perum_South_NS_75", (-75.0, -60.0), (-75.0, -22.0),
                       road_width=4.0, sidewalk_width=0.70,
                       trim_left_start=2.3, trim_left_end=0.0,
                       trim_right_start=2.3, trim_right_end=0.0)

    # South Boulevard along Y=-60.0:
    # West segment: from X=-110.6 (Corner_SouthLoop) to X=-75.0
    # Start at X=-110.6: connects to Corner_SouthLoop (trims 0.0)
    # End at X=-75.0: T-junction (Branch from North! North/Left trims 2.2, South/Right is 0.0 CLOSED!)
    build_road_segment("Perum_South_EW_60_West", (-110.6, -60.0), (-75.0, -60.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=0.0, trim_left_end=2.2,
                       trim_right_start=0.0, trim_right_end=0.0) # South is 100% CLOSED!

    # Mid segment: from X=-75.0 to X=25.0
    # Start at X=-75.0: North/Left trims 2.2, South/Right is 0.0 CLOSED!
    # End at X=25.0: North/Left trims 2.2, South/Right is 0.0 CLOSED!
    build_road_segment("Perum_South_EW_60_Mid", (-75.0, -60.0), (25.0, -60.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=2.2, trim_left_end=2.2,
                       trim_right_start=0.0, trim_right_end=0.0) # South is 100% CLOSED!

    # East Conn segment: from X=25.0 to X=56.61
    # Start at X=25.0: North/Left trims 2.2, South/Right is 0.0 CLOSED!
    # End at X=56.61: meets East Avenue (both trim 1.2)
    build_road_segment("Perum_South_EW_60_East_Conn", (25.0, -60.0), (56.61, -60.0),
                       road_width=4.2, sidewalk_width=0.70,
                       trim_left_start=2.2, trim_left_end=1.2,
                       trim_right_start=0.0, trim_right_end=1.2) # South is CLOSED at X=25!

    # East_NS_25: from Y=-60.0 to Y=0.0
    # Start at Y=-60.0: meets South Boulevard (both trim 2.3)
    # End at Y=0.0: meets Main Boulevard (both trim 2.3)
    build_road_segment("Perum_East_NS_25", (25.0, -60.0), (25.0, 0.0),
                       road_width=4.0, sidewalk_width=0.70,
                       trim_left_start=2.3, trim_left_end=2.3,
                       trim_right_start=2.3, trim_right_end=2.3)

    # =========================================================================
    # 10. CORNER CURB RETURNS AT ALL T-JUNCTIONS AND AVENUE ENDS
    # =========================================================================
    print("10. Placing corner curb returns with solid sidewalk wedges...")

    # Main Boulevard East Avenue ends (X=56.61, Y=0.0)
    build_corner_curb_return("CurbReturn_East_Ave_NW", (54.2, 2.3), r=2.0, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_East_Ave_SW", (54.2, -2.3), r=2.0, start_deg=0, end_deg=90)

    # Main Boulevard West Avenue terminus (X=-143.39, Y=0.0)
    build_corner_curb_return("CurbReturn_West_Ave_NE", (-141.2, 2.3), r=2.0, start_deg=180, end_deg=270)
    build_corner_curb_return("CurbReturn_West_Ave_SE", (-141.2, -2.3), r=2.0, start_deg=90, end_deg=180)

    # South Boulevard East Avenue ends (X=56.61, Y=-60.0)
    build_corner_curb_return("CurbReturn_East_Ave_S_NW", (54.2, -57.7), r=2.0, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_East_Ave_S_SW", (54.2, -62.3), r=2.0, start_deg=0, end_deg=90)

    # Ave-115 & Y=0 Perempatan (4-Way Intersection)
    build_corner_curb_return("CurbReturn_X115_Y0_NW", (-117.4, 2.3), r=2.0, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X115_Y0_NE", (-112.6, 2.3), r=2.0, start_deg=180, end_deg=270)
    build_corner_curb_return("CurbReturn_X115_Y0_SW", (-117.4, -2.3), r=2.0, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X115_Y0_SE", (-112.6, -2.3), r=2.0, start_deg=90, end_deg=180)

    # Ave-115 & Y=38 T-Junction (Branch to East only)
    build_corner_curb_return("CurbReturn_X115_Y38_NE", (-112.6, 40.3), r=2.0, start_deg=180, end_deg=270)
    build_corner_curb_return("CurbReturn_X115_Y38_SE", (-112.6, 35.7), r=2.0, start_deg=90, end_deg=180)

    # Ave-115 & Y=-22 T-Junction (Branch to East only)
    build_corner_curb_return("CurbReturn_X115_Y22_NE", (-112.6, -19.8), r=2.0, start_deg=180, end_deg=270)
    build_corner_curb_return("CurbReturn_X115_Y22_SE", (-112.6, -24.2), r=2.0, start_deg=90, end_deg=180)

    # Pertigaan X=-75 & Y=0 (Branch to North only)
    build_corner_curb_return("CurbReturn_X75_Y0_NW", (-77.2, 2.3), r=1.8, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X75_Y0_NE", (-72.8, 2.3), r=1.8, start_deg=180, end_deg=270)

    # Pertigaan X=-75 & Y=38 (Branch arrives from South only)
    build_corner_curb_return("CurbReturn_X75_Y38_SW", (-77.2, 35.7), r=1.8, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X75_Y38_SE", (-72.8, 35.7), r=1.8, start_deg=90, end_deg=180)

    # Pertigaan X=-84 & Y=0 (Branch to South only)
    build_corner_curb_return("CurbReturn_X84_Y0_SW", (-86.1, -2.3), r=1.8, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X84_Y0_SE", (-81.9, -2.3), r=1.8, start_deg=90, end_deg=180)

    # Pertigaan X=-84 & Y=-22 (Branch arrives from North only)
    build_corner_curb_return("CurbReturn_X84_Y22_NW", (-86.1, -19.8), r=1.8, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X84_Y22_NE", (-81.9, -19.8), r=1.8, start_deg=180, end_deg=270)

    # Pos Ronda Pertigaan at X=-32 & Y=0 (Branch to South only)
    build_corner_curb_return("CurbReturn_X32_Y0_SW", (-34.1, -2.3), r=1.8, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X32_Y0_SE", (-29.9, -2.3), r=1.8, start_deg=90, end_deg=180)

    # East Connector at X=25 & Y=0 (Branch to South only)
    build_corner_curb_return("CurbReturn_X25_Y0_SW", (22.9, -2.3), r=1.8, start_deg=0, end_deg=90)
    build_corner_curb_return("CurbReturn_X25_Y0_SE", (27.1, -2.3), r=1.8, start_deg=90, end_deg=180)

    # South Boulevard Pertigaan at X=-75 & Y=-60 (Branch arrives from North only)
    build_corner_curb_return("CurbReturn_X75_Y60_NW", (-77.2, -57.7), r=1.8, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X75_Y60_NE", (-72.8, -57.7), r=1.8, start_deg=180, end_deg=270)

    # South Boulevard Pertigaan at X=25 & Y=-60 (Branch arrives from North only)
    build_corner_curb_return("CurbReturn_X25_Y60_NW", (22.9, -57.7), r=1.8, start_deg=270, end_deg=360)
    build_corner_curb_return("CurbReturn_X25_Y60_NE", (27.1, -57.7), r=1.8, start_deg=180, end_deg=270)

    # Save the blend file immediately
    bpy.ops.wm.save_mainfile()
    print("=== Successfully saved kampung_kos_gang.blend ===")

if __name__ == "__main__":
    run()
