"""
Script to fix:
1. Shift all sliding gates and fence tracks (SlidingGate_House1, 3, 5, 6) back by -1.2m
   so they align with their gate posts and sit neatly behind the sidewalk.
2. Shift Warkop street stall back by -1.2m.
3. Remove old conflicting Got_Slab, Got_Slot, Gang_Drain, and Polisi_Stripe fragments.
4. Redesign the 4-way perempatan intersection and West T-junction:
   - Completely remove the ugly protruding fan wedges (CurbReturn_Perempatan_* and CurbReturn_WestJunc_*).
   - Build 4 crisp, non-overlapping corner sidewalk blocks with black-and-white curb blocks.
   - Build 4 clean, painted zebra crosswalks and stop lines on the approach roads.
   - Center intersection square is a single, clean, flat asphalt plane (0 Z-fighting).
5. Save blend file and export GLBs.
"""

import bpy  # pyrefly: ignore[missing-import] # type: ignore
import bmesh  # pyrefly: ignore[missing-import] # type: ignore
import math
from mathutils import Vector  # pyrefly: ignore[missing-import] # type: ignore

def run():
    print("=== Starting fix_fences_and_clean_intersection.py ===")

    # Materials
    mat_asphalt = bpy.data.materials.get("road_asphalt")
    mat_marking_white = bpy.data.materials.get("road_marking_white")
    mat_curb_concrete = bpy.data.materials.get("curb_concrete") or bpy.data.materials.get("Mat_ConcreteCurb.001")
    mat_curb_black = bpy.data.materials.get("curb_black")
    mat_curb_white = bpy.data.materials.get("curb_white")

    col_campus = bpy.data.collections.get("CampusArea") or bpy.context.scene.collection
    col_perumahan = bpy.data.collections.get("PerumahanRoads") or bpy.context.scene.collection

    # -------------------------------------------------------------------------
    # 1. SHIFT SLIDING GATES, TRACKS, AND WARKOP BACK
    # -------------------------------------------------------------------------
    print("1. Moving sliding gates and fence tracks back...")
    gates_to_shift = [
        "SlidingGate_House1", "SlidingGate_House1_Track",
        "SlidingGate_House3", "SlidingGate_House3_Track",
        "SlidingGate_House5", "SlidingGate_House5_Track",
        "SlidingGate_House6", "SlidingGate_House6_Track",
    ]
    for gname in gates_to_shift:
        obj = bpy.data.objects.get(gname)
        if obj:
            # If not yet shifted (still around -2.22), shift by -1.2m to -3.42m
            if obj.location.y > -2.5:
                obj.location.y -= 1.2
                print(f"Shifted {gname} to Y={obj.location.y:.2f}")

    # Shift Warkop street stall objects
    warkop_objs = [o for o in bpy.data.objects if "Warkop" in o.name]
    for wo in warkop_objs:
        if wo.location.y > -3.2:
            wo.location.y -= 1.2
            print(f"Shifted {wo.name} to Y={wo.location.y:.2f}")

    # -------------------------------------------------------------------------
    # 2. REMOVE OLD CONFLICTING GUTTER SLABS AND SPEED BUMPS
    # -------------------------------------------------------------------------
    print("2. Removing old gutter slabs and speed bumps...")
    old_fragments = [
        o.name for o in bpy.data.objects
        if (o.name.startswith("Got_Slab_") or o.name.startswith("Got_Slot_") or
            o.name.startswith("Gang_Drain_") or o.name.startswith("Polisi_Stripe_"))
    ]
    for fname in old_fragments:
        o = bpy.data.objects.get(fname)
        if o:
            mesh = o.data if o.type == 'MESH' else None
            bpy.data.objects.remove(o, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)

    print(f"Removed {len(old_fragments)} old conflicting fragments.")

    # -------------------------------------------------------------------------
    # 3. REMOVE UGLY PROTRUDING FAN WEDGES AT INTERSECTIONS
    # -------------------------------------------------------------------------
    print("3. Removing protruding fan wedges...")
    wedge_names = [
        "CurbReturn_Perempatan_NW", "CurbReturn_Perempatan_NE",
        "CurbReturn_Perempatan_SW", "CurbReturn_Perempatan_SE",
        "CurbReturn_WestJunc_NW", "CurbReturn_WestJunc_SW",
        "Perempatan_Intersection_Center-col", "Perempatan_NW_Corner-col",
        "Perempatan_NE_Corner-col", "Perempatan_SW_Corner-col", "Perempatan_SE_Corner-col",
        "WestJunc_NW_Corner-col", "WestJunc_SW_Corner-col"
    ]
    # Also catch any with .001 suffix
    for o in list(bpy.data.objects):
        if any(o.name.startswith(p) for p in [
            "CurbReturn_Perempatan_", "CurbReturn_WestJunc_",
            "Perempatan_", "WestJunc_", "Zebra_Perempatan_", "StopLine_Perempatan_"
        ]):
            wedge_names.append(o.name)

    for wname in set(wedge_names):
        o = bpy.data.objects.get(wname)
        if o:
            mesh = o.data if o.type == 'MESH' else None
            bpy.data.objects.remove(o, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)

    # -------------------------------------------------------------------------
    # 4. REDESIGN 4-WAY PEREMPATAN INTERSECTION (CLEAN, SQUARE, CRISP)
    # Coordinates: Center is at X = 61.11, Y = -165.24
    # Roadway width: 9.0m
    # N-S Roadway: X in [56.61, 65.61]
    # E-W Roadway: Y in [-169.74, -160.74]
    # Center box: X in [56.61, 65.61], Y in [-169.74, -160.74]
    # -------------------------------------------------------------------------
    print("4. Building crisp perempatan intersection and sidewalk corners...")

    # A. Central Intersection Asphalt Box (Single flat surface at Z=0.00)
    mesh_center = bpy.data.meshes.new("Perempatan_Center_Mesh")
    obj_center = bpy.data.objects.new("Perempatan_Intersection_Center-col", mesh_center)
    bm_cnt = bmesh.new()
    
    x_min, x_max = 56.61, 65.61
    y_min, y_max = -169.74, -160.74
    
    v1 = bm_cnt.verts.new((x_min, y_min, -0.08))
    v2 = bm_cnt.verts.new((x_max, y_min, -0.08))
    v3 = bm_cnt.verts.new((x_max, y_max, -0.08))
    v4 = bm_cnt.verts.new((x_min, y_max, -0.08))
    v5 = bm_cnt.verts.new((x_min, y_min,  0.00))
    v6 = bm_cnt.verts.new((x_max, y_min,  0.00))
    v7 = bm_cnt.verts.new((x_max, y_max,  0.00))
    v8 = bm_cnt.verts.new((x_min, y_max,  0.00))
    
    bm_cnt.faces.new([v5, v6, v7, v8]) # top
    bm_cnt.faces.new([v4, v3, v2, v1]) # bottom
    bm_cnt.faces.new([v1, v2, v6, v5])
    bm_cnt.faces.new([v2, v3, v7, v6])
    bm_cnt.faces.new([v3, v4, v8, v7])
    bm_cnt.faces.new([v4, v1, v5, v8])
    
    bm_cnt.to_mesh(mesh_center)
    bm_cnt.free()
    mesh_center.materials.append(mat_asphalt)
    col_campus.objects.link(obj_center)

    # B. The 4 Corner Sidewalk Blocks (Neat 3m x 3m sidewalk squares with black/white curbs)
    # They stay STRICTLY on the sidewalk corners:
    # NW: X in [53.61, 56.61], Y in [-160.74, -157.74]
    # NE: X in [65.61, 68.61], Y in [-160.74, -157.74]
    # SW: X in [53.61, 56.61], Y in [-172.74, -169.74]
    # SE: X in [65.61, 68.61], Y in [-172.74, -169.74]

    def build_corner_sidewalk_block(name, x_range, y_range, curb_face_x, curb_face_y):
        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        obj = bpy.data.objects.new(f"{name}-col", mesh)
        bm = bmesh.new()

        xa, xb = x_range
        ya, yb = y_range
        z_top = 0.18
        z_bot = -0.05
        curb_w = 0.15

        # 1. Main Sidewalk Slab
        v1 = bm.verts.new((xa, ya, z_bot))
        v2 = bm.verts.new((xb, ya, z_bot))
        v3 = bm.verts.new((xb, yb, z_bot))
        v4 = bm.verts.new((xa, yb, z_bot))
        v5 = bm.verts.new((xa, ya, z_top))
        v6 = bm.verts.new((xb, ya, z_top))
        v7 = bm.verts.new((xb, yb, z_top))
        v8 = bm.verts.new((xa, yb, z_top))

        f_top = bm.faces.new([v5, v6, v7, v8])
        f_top.material_index = 0 # mat_curb_concrete
        for fvs in [[v4, v3, v2, v1], [v1, v2, v6, v5], [v2, v3, v7, v6], [v3, v4, v8, v7], [v4, v1, v5, v8]]:
            f = bm.faces.new(fvs)
            f.material_index = 0

        # 2. Black & White Curb Blocks facing the E-W street (along Y edge)
        curb_y = curb_face_y
        sign_y = -1.0 if curb_y == ya else 1.0
        x_len = abs(xb - xa)
        n_blocks_x = max(1, int(round(x_len / 1.0)))
        blen_x = x_len / n_blocks_x
        
        for bi in range(n_blocks_x):
            cx0 = xa + bi * blen_x
            cx1 = cx0 + blen_x
            cmat_idx = 1 if (bi % 2 == 0) else 2 # 1: white, 2: black
            
            c_ya = curb_y
            c_yb = curb_y + sign_y * curb_w
            c_ymin, c_ymax = min(c_ya, c_yb), max(c_ya, c_yb)

            cv1 = bm.verts.new((cx0, c_ymin, 0.00))
            cv2 = bm.verts.new((cx1, c_ymin, 0.00))
            cv3 = bm.verts.new((cx1, c_ymax, 0.00))
            cv4 = bm.verts.new((cx0, c_ymax, 0.00))
            cv5 = bm.verts.new((cx0, c_ymin, z_top))
            cv6 = bm.verts.new((cx1, c_ymin, z_top))
            cv7 = bm.verts.new((cx1, c_ymax, z_top))
            cv8 = bm.verts.new((cx0, c_ymax, z_top))

            for fvs in [[cv5, cv6, cv7, cv8], [cv1, cv2, cv6, cv5], [cv2, cv3, cv7, cv6], [cv3, cv4, cv8, cv7], [cv4, cv1, cv5, cv8]]:
                f = bm.faces.new(fvs)
                f.material_index = cmat_idx

        # 3. Black & White Curb Blocks facing the N-S street (along X edge)
        curb_x = curb_face_x
        sign_x = -1.0 if curb_x == xa else 1.0
        y_len = abs(yb - ya)
        n_blocks_y = max(1, int(round(y_len / 1.0)))
        blen_y = y_len / n_blocks_y

        for bi in range(n_blocks_y):
            cy0 = ya + bi * blen_y
            cy1 = cy0 + blen_y
            cmat_idx = 2 if (bi % 2 == 0) else 1 # alternate
            
            c_xa = curb_x
            c_xb = curb_x + sign_x * curb_w
            c_xmin, c_xmax = min(c_xa, c_xb), max(c_xa, c_xb)

            cv1 = bm.verts.new((c_xmin, cy0, 0.00))
            cv2 = bm.verts.new((c_xmax, cy0, 0.00))
            cv3 = bm.verts.new((c_xmax, cy1, 0.00))
            cv4 = bm.verts.new((c_xmin, cy1, 0.00))
            cv5 = bm.verts.new((c_xmin, cy0, z_top))
            cv6 = bm.verts.new((c_xmax, cy0, z_top))
            cv7 = bm.verts.new((c_xmax, cy1, z_top))
            cv8 = bm.verts.new((c_xmin, cy1, z_top))

            for fvs in [[cv5, cv6, cv7, cv8], [cv1, cv2, cv6, cv5], [cv2, cv3, cv7, cv6], [cv3, cv4, cv8, cv7], [cv4, cv1, cv5, cv8]]:
                f = bm.faces.new(fvs)
                f.material_index = cmat_idx

        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_curb_concrete)
        mesh.materials.append(mat_curb_white)
        mesh.materials.append(mat_curb_black)
        col_campus.objects.link(obj)
        return obj

    # NW Corner (Faces south to Y=-160.74, faces east to X=56.61)
    build_corner_sidewalk_block("Perempatan_NW_Corner", (53.61, 56.61), (-160.74, -157.74), 56.61, -160.74)
    # NE Corner (Faces south to Y=-160.74, faces west to X=65.61)
    build_corner_sidewalk_block("Perempatan_NE_Corner", (65.61, 68.61), (-160.74, -157.74), 65.61, -160.74)
    # SW Corner (Faces north to Y=-169.74, faces east to X=56.61)
    build_corner_sidewalk_block("Perempatan_SW_Corner", (53.61, 56.61), (-172.74, -169.74), 56.61, -169.74)
    # SE Corner (Faces north to Y=-169.74, faces west to X=65.61)
    build_corner_sidewalk_block("Perempatan_SE_Corner", (65.61, 68.61), (-172.74, -169.74), 65.61, -169.74)

    # C. West T-Junction Sidewalk Corners (at West Avenue X=-147.89, E-W road ends at X=-143.39)
    # NW: X in [-146.39, -143.39], Y in [-160.74, -157.74]
    # SW: X in [-146.39, -143.39], Y in [-172.74, -169.74]
    build_corner_sidewalk_block("WestJunc_NW_Corner", (-146.39, -143.39), (-160.74, -157.74), -143.39, -160.74)
    build_corner_sidewalk_block("WestJunc_SW_Corner", (-146.39, -143.39), (-172.74, -169.74), -143.39, -169.74)

    # -------------------------------------------------------------------------
    # D. PAINTED ZEBRA CROSSWALKS & STOP LINES (CRISP & OUTSIDE INTERSECTION)
    # -------------------------------------------------------------------------
    def build_crosswalk_stripes(name, center_pos, length_across, depth_along, is_ns_crossing=True):
        """
        Builds a crisp, standard painted zebra crosswalk:
        - White bars 0.50m wide with 0.50m gap
        - Painted flat on asphalt at Z = 0.003
        """
        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bm = bmesh.new()

        cx, cy = center_pos
        stripe_w = 0.50
        gap_w = 0.50
        cycle = stripe_w + gap_w
        z = 0.003

        n_stripes = int(math.floor(length_across / cycle))
        start_off = -length_across/2.0 + (length_across - (n_stripes * cycle - gap_w)) / 2.0

        for si in range(n_stripes):
            off0 = start_off + si * cycle
            off1 = off0 + stripe_w

            if is_ns_crossing:
                # Stripes are oriented along Y, spaced across X
                px0 = cx + off0
                px1 = cx + off1
                py0 = cy - depth_along / 2.0
                py1 = cy + depth_along / 2.0
            else:
                # Stripes are oriented along X, spaced across Y
                px0 = cx - depth_along / 2.0
                px1 = cx + depth_along / 2.0
                py0 = cy + off0
                py1 = cy + off1

            v1 = bm.verts.new((px0, py0, z))
            v2 = bm.verts.new((px1, py0, z))
            v3 = bm.verts.new((px1, py1, z))
            v4 = bm.verts.new((px0, py1, z))
            bm.faces.new([v1, v2, v3, v4])

        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_marking_white)
        col_campus.objects.link(obj)
        return obj

    def build_stop_line(name, center_pos, length_across, is_ns_road=True):
        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bm = bmesh.new()
        
        cx, cy = center_pos
        line_thick = 0.35
        z = 0.003
        
        if is_ns_road:
            x0 = cx - length_across / 2.0
            x1 = cx + length_across / 2.0
            y0 = cy - line_thick / 2.0
            y1 = cy + line_thick / 2.0
        else:
            x0 = cx - line_thick / 2.0
            x1 = cx + line_thick / 2.0
            y0 = cy - length_across / 2.0
            y1 = cy + length_across / 2.0

        v1 = bm.verts.new((x0, y0, z))
        v2 = bm.verts.new((x1, y0, z))
        v3 = bm.verts.new((x1, y1, z))
        v4 = bm.verts.new((x0, y1, z))
        bm.faces.new([v1, v2, v3, v4])
        
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_marking_white)
        col_campus.objects.link(obj)
        return obj

    # 1. North Approach Crosswalk (on N-S avenue at Y=-158.5)
    build_crosswalk_stripes("Zebra_Perempatan_North", (61.11, -158.5), length_across=8.0, depth_along=2.6, is_ns_crossing=True)
    build_stop_line("StopLine_Perempatan_North", (61.11, -157.0), length_across=8.0, is_ns_road=True)

    # 2. South Approach Crosswalk (on N-S avenue at Y=-172.0)
    build_crosswalk_stripes("Zebra_Perempatan_South", (61.11, -172.0), length_across=8.0, depth_along=2.6, is_ns_crossing=True)
    build_stop_line("StopLine_Perempatan_South", (61.11, -173.5), length_across=8.0, is_ns_road=True)

    # 3. West Approach Crosswalk (on E-W avenue at X=54.5)
    build_crosswalk_stripes("Zebra_Perempatan_West", (54.5, -165.24), length_across=8.0, depth_along=2.6, is_ns_crossing=False)
    build_stop_line("StopLine_Perempatan_West", (53.0, -165.24), length_across=8.0, is_ns_road=False)

    # 4. East Approach Crosswalk (on E-W avenue at X=67.7)
    build_crosswalk_stripes("Zebra_Perempatan_East", (67.7, -165.24), length_across=8.0, depth_along=2.6, is_ns_crossing=False)
    build_stop_line("StopLine_Perempatan_East", (69.2, -165.24), length_across=8.0, is_ns_road=False)

    # 5. West T-Junction Crosswalk (at X=-141.5)
    build_crosswalk_stripes("Zebra_WestJunc", (-141.5, -165.24), length_across=8.0, depth_along=2.6, is_ns_crossing=False)
    build_stop_line("StopLine_WestJunc", (-140.0, -165.24), length_across=8.0, is_ns_road=False)

    print("Created clean, non-overlapping zebra crosswalks and stop lines.")

    # -------------------------------------------------------------------------
    # E. UPDATE TRAFFIC LIGHT POLE POSITIONS ON CORNER SIDEWALKS
    # -------------------------------------------------------------------------
    tl_positions = {
        "TrafficLight_NW": (54.8, -158.8),
        "TrafficLight_NE": (67.4, -158.8),
        "TrafficLight_SW": (54.8, -171.7),
        "TrafficLight_SE": (67.4, -171.7),
    }
    for base_name, (npx, npy) in tl_positions.items():
        pole = bpy.data.objects.get(f"{base_name}_Pole-col")
        if pole:
            cur_px, cur_py = pole.location.x, pole.location.y
            shift_x = npx - cur_px
            shift_y = npy - cur_py
            # Shift all related parts of this traffic light
            for part in bpy.data.objects:
                if part.name.startswith(base_name):
                    part.location.x += shift_x
                    part.location.y += shift_y

    # Save the blend file immediately
    bpy.ops.wm.save_mainfile()
    print("=== Successfully fixed fences and redesigned intersection! ===")

if __name__ == "__main__":
    run()
