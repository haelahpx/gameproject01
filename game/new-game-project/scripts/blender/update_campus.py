import bpy
import bmesh
import mathutils
import math
import os

def run_update():
    print("Starting Campus Area Comprehensive Overhaul...")
    
    # -------------------------------------------------------------------------
    # 1. HELPER FUNCTIONS & MATERIALS
    # -------------------------------------------------------------------------
    def get_or_create_material(name, color, roughness=0.5, metallic=0.0, alpha=1.0, is_glass=False):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
        if not bsdf:
            bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        
        bsdf.inputs['Base Color'].default_value = (color[0], color[1], color[2], alpha)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if 'Alpha' in bsdf.inputs:
            bsdf.inputs['Alpha'].default_value = alpha
            
        if is_glass:
            if 'Transmission Weight' in bsdf.inputs:
                bsdf.inputs['Transmission Weight'].default_value = 0.85
            elif 'Transmission' in bsdf.inputs:
                bsdf.inputs['Transmission'].default_value = 0.85
            if hasattr(mat, "blend_method"):
                mat.blend_method = 'BLEND'
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = 'BLENDED'
            if hasattr(mat, "show_transparent_back"):
                mat.show_transparent_back = False
                
        return mat

    # Retrieve existing or create materials
    m_wall_orange = get_or_create_material("Mat_SchoolWall_Orange", (0.88, 0.46, 0.20), roughness=0.55)
    m_white_trim  = get_or_create_material("Mat_WhiteTrim", (0.96, 0.96, 0.97), roughness=0.35)
    m_roof_slate  = get_or_create_material("Mat_RoofSlate", (0.29, 0.31, 0.34), roughness=0.85)
    m_glass       = get_or_create_material("Mat_WindowGlass", (0.32, 0.58, 0.80), roughness=0.05, alpha=0.35, is_glass=True)
    m_courtyard   = get_or_create_material("Mat_CourtyardBlue", (0.23, 0.36, 0.49), roughness=0.75)
    m_perim_wall  = get_or_create_material("Mat_PerimeterWall", (0.89, 0.90, 0.84), roughness=0.6)
    m_road        = get_or_create_material("Mat_RoadAsphalt", (0.16, 0.17, 0.18), roughness=0.85)
    m_sidewalk    = get_or_create_material("Mat_Sidewalk", (0.84, 0.85, 0.86), roughness=0.55)
    m_bus_yellow  = get_or_create_material("Mat_SchoolBusYellow", (0.96, 0.70, 0.12), roughness=0.3)
    m_solar_blue  = get_or_create_material("Mat_SolarPanelBlue", (0.10, 0.22, 0.48), roughness=0.15, metallic=0.7)
    m_metal_gray  = get_or_create_material("Mat_MetalGray", (0.58, 0.62, 0.65), roughness=0.35, metallic=0.7)
    m_grass       = get_or_create_material("Mat_GrassGreen", (0.34, 0.58, 0.24), roughness=0.8)
    m_car_red     = get_or_create_material("Mat_CarRed", (0.80, 0.16, 0.14), roughness=0.25)
    m_car_orange  = get_or_create_material("Mat_CarOrange", (0.90, 0.45, 0.12), roughness=0.3)
    m_car_silver  = get_or_create_material("Mat_CarSilver", (0.74, 0.76, 0.78), roughness=0.3, metallic=0.6)
    m_car_blue    = get_or_create_material("Mat_CarBlue", (0.12, 0.35, 0.78), roughness=0.3)
    m_door_wood   = get_or_create_material("Mat_DoorWood", (0.38, 0.22, 0.12), roughness=0.5)
    m_interior    = get_or_create_material("Mat_InteriorFloor", (0.84, 0.82, 0.78), roughness=0.45)
    m_black_tire  = get_or_create_material("Mat_BlackTire", (0.08, 0.08, 0.08), roughness=0.9)
    m_clock_white = get_or_create_material("Mat_ClockFace", (0.98, 0.98, 0.98), roughness=0.2)
    m_dark_metal  = get_or_create_material("Mat_DarkMetal", (0.15, 0.15, 0.16), roughness=0.4, metallic=0.5)
    m_paving      = get_or_create_material("Mat_PavingBlock", (0.76, 0.73, 0.70), roughness=0.65)
    m_paver_edge  = get_or_create_material("Mat_PaverBorder", (0.60, 0.58, 0.55), roughness=0.7)
    m_curb        = get_or_create_material("Mat_ConcreteCurb", (0.82, 0.83, 0.85), roughness=0.6)
    m_flag_red    = get_or_create_material("Mat_FlagRed", (0.88, 0.08, 0.08), roughness=0.4)
    m_flag_white  = get_or_create_material("Mat_FlagWhite", (0.98, 0.98, 0.98), roughness=0.4)
    m_gold        = get_or_create_material("Mat_GoldFinial", (0.95, 0.80, 0.20), roughness=0.2, metallic=0.85)
    m_bin_green   = get_or_create_material("Mat_BinGreen", (0.15, 0.65, 0.22), roughness=0.4)
    m_bin_yellow  = get_or_create_material("Mat_BinYellow", (0.92, 0.78, 0.10), roughness=0.4)
    m_bin_red     = get_or_create_material("Mat_BinRed", (0.85, 0.15, 0.12), roughness=0.4)
    m_canopy_blue = get_or_create_material("Mat_CanopyBlue", (0.18, 0.42, 0.68), roughness=0.35)
    m_motor_teal  = get_or_create_material("Mat_MotorTeal", (0.10, 0.55, 0.58), roughness=0.3)
    m_motor_black = get_or_create_material("motor_body_black", (0.12, 0.12, 0.14), roughness=0.3)
    m_motor_red   = get_or_create_material("motor_body_red", (0.78, 0.12, 0.12), roughness=0.3)
    m_motor_white = get_or_create_material("motor_body_white", (0.92, 0.92, 0.92), roughness=0.3)

    # -------------------------------------------------------------------------
    # 2. PRIMITIVE BUILDERS
    # -------------------------------------------------------------------------
    def remove_objects_by_prefix(prefixes):
        to_del = []
        for obj in bpy.context.scene.objects:
            for p in prefixes:
                if obj.name.startswith(p):
                    to_del.append(obj)
                    break
        for obj in to_del:
            bpy.data.objects.remove(obj, do_unlink=True)

    def add_box(name, center, size, material=None, col=True):
        col_suffix = "-col" if col else ""
        obj_name = f"{name}{col_suffix}"
        if obj_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
        obj = bpy.context.active_object
        obj.name = obj_name
        obj.scale = (size[0], size[1], size[2])
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if material:
            obj.data.materials.append(material)
        return obj

    def add_box_rot(name, center, size, material=None, rotation_z=0.0, col=True):
        col_suffix = "-col" if col else ""
        obj_name = f"{name}{col_suffix}"
        if obj_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
        obj = bpy.context.active_object
        obj.name = obj_name
        obj.scale = (size[0], size[1], size[2])
        obj.rotation_euler = (0, 0, rotation_z)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        if material:
            obj.data.materials.append(material)
        return obj

    def add_cylinder(name, center, radius, height, material=None, col=True, vertices=16):
        col_suffix = "-col" if col else ""
        obj_name = f"{name}{col_suffix}"
        if obj_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=vertices,
            radius=radius,
            depth=height,
            location=center
        )
        obj = bpy.context.active_object
        obj.name = obj_name
        if material:
            obj.data.materials.append(material)
        return obj

    # -------------------------------------------------------------------------
    # 3. FIX PERIMETER WALLS & DRIVEWAY GATES (REQUIREMENT 2)
    # -------------------------------------------------------------------------
    print("Updating Perimeter Walls & Driveway Gates...")
    # Remove old continuous south walls and caps
    remove_objects_by_prefix([
        "Perim_Wall_South", "Perim_Cap_South",
        "Street_Curb_7", "Street_Curb_8", "Street_Curb_9", "Street_Curb_10", "Street_Curb_11", "Street_Curb_12", # Left driveway opening (-19 to -13)
        "Street_Curb_29", "Street_Curb_30", "Street_Curb_31", "Street_Curb_32", "Street_Curb_33", # Right driveway opening (+13.5 to +18.5)
        "Parking_Pad_L", "Parking_Pad_R", "Stall_Line_", "Planter_Left_", "Planter_Right_",
        "Path_Parking_W", "Path_Parking_E", "Walkway_", "Promenade_", "Plaza_Curb_"
    ])

    wall_h = 1.5
    wall_z = 0.75
    cap_z = 1.55

    # Perimeter South wall segments with dedicated gate openings:
    # Segment 1: Far West [-27.5 to -19.5] -> center -23.5, len 8.0
    add_box("Perim_Wall_South_FarW", (-23.5, -34.5, wall_z), (8.0, 0.6, wall_h), m_perim_wall)
    add_box("Perim_Cap_South_FarW",  (-23.5, -34.5, cap_z),  (8.2, 0.8, 0.1),    m_white_trim)

    # --- LEFT VEHICLE GATE (CAR & BUS ENTRANCE: X = -19.5 to -12.5) ---
    # Left Gate Pillars
    add_box("GatePillar_Car_L", (-19.3, -34.5, 1.2), (0.9, 0.9, 2.4), m_white_trim)
    add_box("GatePillar_Car_L_Cap", (-19.3, -34.5, 2.45), (1.1, 1.1, 0.15), m_wall_orange)
    add_box("GatePillar_Car_R", (-12.7, -34.5, 1.2), (0.9, 0.9, 2.4), m_white_trim)
    add_box("GatePillar_Car_R_Cap", (-12.7, -34.5, 2.45), (1.1, 1.1, 0.15), m_wall_orange)
    # Open iron swinging gate leaves folded back
    add_box_rot("GateLeaf_Car_L", (-19.0, -33.5, 1.0), (0.1, 2.8, 1.8), m_dark_metal, rotation_z=math.radians(15))
    add_box_rot("GateLeaf_Car_R", (-13.0, -33.5, 1.0), (0.1, 2.8, 1.8), m_dark_metal, rotation_z=math.radians(-15))
    # Gate Signboard
    add_box("GateSign_Car", (-16.0, -34.5, 2.5), (3.6, 0.15, 0.45), m_sidewalk)

    # Segment 2: Mid West [-12.5 to -3.0] -> center -7.75, len 9.5
    add_box("Perim_Wall_South_MidW", (-7.75, -34.5, wall_z), (9.5, 0.6, wall_h), m_perim_wall)
    add_box("Perim_Cap_South_MidW",  (-7.75, -34.5, cap_z),  (9.7, 0.8, 0.1),    m_white_trim)

    # --- CENTER MAIN PEDESTRIAN GATE (X = -3.0 to +3.0) ---
    add_box("GatePillar_Main_L", (-3.0, -34.5, 1.5), (1.0, 1.0, 3.0), m_white_trim)
    add_box("GatePillar_Main_L_Cap", (-3.0, -34.5, 3.08), (1.2, 1.2, 0.2), m_wall_orange)
    add_box("GatePillar_Main_R", (3.0, -34.5, 1.5), (1.0, 1.0, 3.0), m_white_trim)
    add_box("GatePillar_Main_R_Cap", (3.0, -34.5, 3.08), (1.2, 1.2, 0.2), m_wall_orange)
    # Grand Overhead Arch with School Name
    add_box("GateArch_Main_Beam", (0.0, -34.5, 3.5), (6.8, 0.8, 0.65), m_wall_orange)
    add_box("GateArch_Main_Cornice", (0.0, -34.5, 3.88), (7.0, 1.0, 0.15), m_white_trim)

    # Segment 3: Mid East [+3.0 to +13.5] -> center 8.25, len 10.5
    add_box("Perim_Wall_South_MidE", (8.25, -34.5, wall_z), (10.5, 0.6, wall_h), m_perim_wall)
    add_box("Perim_Cap_South_MidE",  (8.25, -34.5, cap_z),  (10.7, 0.8, 0.1),    m_white_trim)

    # --- RIGHT VEHICLE GATE (MOTORCYCLE & BICYCLE ENTRANCE: X = +13.5 to +18.5) ---
    add_box("GatePillar_Motor_L", (13.3, -34.5, 1.2), (0.8, 0.8, 2.4), m_white_trim)
    add_box("GatePillar_Motor_L_Cap", (13.3, -34.5, 2.45), (1.0, 1.0, 0.15), m_wall_orange)
    add_box("GatePillar_Motor_R", (18.7, -34.5, 1.2), (0.8, 0.8, 2.4), m_white_trim)
    add_box("GatePillar_Motor_R_Cap", (18.7, -34.5, 2.45), (1.0, 1.0, 0.15), m_wall_orange)
    # Open iron gate leaves
    add_box_rot("GateLeaf_Motor_L", (13.6, -33.5, 1.0), (0.1, 2.0, 1.8), m_dark_metal, rotation_z=math.radians(15))
    add_box_rot("GateLeaf_Motor_R", (18.4, -33.5, 1.0), (0.1, 2.0, 1.8), m_dark_metal, rotation_z=math.radians(-15))
    add_box("GateSign_Motor", (16.0, -34.5, 2.5), (3.4, 0.15, 0.45), m_sidewalk)

    # Segment 4: Far East [+18.5 to +27.5] -> center 23.0, len 9.0
    add_box("Perim_Wall_South_FarE", (23.0, -34.5, wall_z), (9.0, 0.6, wall_h), m_perim_wall)
    add_box("Perim_Cap_South_FarE",  (23.0, -34.5, cap_z),  (9.2, 0.8, 0.1),    m_white_trim)

    # -------------------------------------------------------------------------
    # 4. ASPHALT DRIVEWAYS CONNECTING ROAD TO PARKING LOTS (REQUIREMENT 2)
    # -------------------------------------------------------------------------
    print("Building clear asphalt driveways...")
    # Left Driveway: Runs continuously from road (Y = -38.5) through gate (Y = -34.5) to parking lot (Y = -30.0)
    add_box("Driveway_Car_RoadCut", (-16.0, -36.5, -0.04), (5.8, 4.0, 0.04), m_road, col=False)
    add_box("Driveway_Car_GateEntry", (-16.0, -32.5, 0.01), (5.8, 4.2, 0.04), m_road, col=False)

    # Right Driveway: Runs from road through motor gate to parking lot
    add_box("Driveway_Motor_RoadCut", (16.0, -36.5, -0.04), (4.6, 4.0, 0.04), m_road, col=False)
    add_box("Driveway_Motor_GateEntry", (16.0, -32.5, 0.01), (4.6, 4.2, 0.04), m_road, col=False)

    # -------------------------------------------------------------------------
    # 5. LEFT PARKING LOT: DEDICATED CARS & BUS (REQUIREMENT 2)
    # -------------------------------------------------------------------------
    print("Building Left Parking Lot (Cars & Bus)...")
    # Extended continuous parking asphalt pad
    add_box("Parking_Pad_Cars", (-16.5, -27.5, 0.01), (15.5, 12.0, 0.03), m_road)

    # Yellow School Bus Parking Bay (Stall marked for Bus)
    add_box("Bus_Stall_Line_L", (-22.5, -27.0, 0.03), (0.2, 9.0, 0.01), m_bus_yellow, col=False)
    add_box("Bus_Stall_Line_R", (-19.0, -27.0, 0.03), (0.2, 9.0, 0.01), m_bus_yellow, col=False)
    add_box("Bus_Stall_Line_T", (-20.75, -22.5, 0.03), (3.7, 0.2, 0.01), m_bus_yellow, col=False)

    # Move Parked School Bus into its bay
    bus_parts = [o for o in bpy.data.objects if o.name.startswith("Parked_SchoolBus")]
    for p in bus_parts:
        # Bus center at X = -20.75, Y = -27.0
        p.location.x = -20.75 + (p.location.x - (-17.0))
        p.location.y = -27.0 + (p.location.y - (-28.0))

    # Car Parking Stalls (4 stalls for cars)
    car_x_positions = [-17.2, -14.4, -11.6, -8.8]
    for cx in [-18.6, -15.8, -13.0, -10.2, -7.4]:
        add_box(f"Car_Stall_Line_{cx:.1f}", (cx, -26.5, 0.03), (0.14, 5.5, 0.01), m_white_trim, col=False)
    for cx in car_x_positions:
        add_box(f"Car_Stall_Top_{cx:.1f}", (cx, -23.75, 0.03), (2.8, 0.14, 0.01), m_white_trim, col=False)
        add_box(f"Car_Wheel_Stop_{cx:.1f}", (cx, -24.2, 0.08), (1.8, 0.25, 0.15), m_curb)

    # Place Cars in Left Parking Stalls
    car_orange = [o for o in bpy.data.objects if o.name.startswith("Car_Orange")]
    for p in car_orange:
        p.location.x = -17.2 + (p.location.x - (-13.0))
        p.location.y = -26.5 + (p.location.y - (-28.0))

    # Move Red and Silver cars from the right side over to the left parking lot!
    car_red = [o for o in bpy.data.objects if o.name.startswith("Car_Red")]
    for p in car_red:
        p.location.x = -14.4 + (p.location.x - (12.5))
        p.location.y = -26.5 + (p.location.y - (-28.0))

    car_silver = [o for o in bpy.data.objects if o.name.startswith("Car_Silver")]
    for p in car_silver:
        p.location.x = -11.6 + (p.location.x - (15.5))
        p.location.y = -26.5 + (p.location.y - (-28.0))

    # -------------------------------------------------------------------------
    # 6. RIGHT PARKING LOT: DEDICATED MOTORCYCLES & BICYCLES (REQUIREMENT 2)
    # -------------------------------------------------------------------------
    print("Building Right Parking Lot (Motorcycles & Bicycles)...")
    # Continuous asphalt pad for motor & bike
    add_box("Parking_Pad_MotorBikes", (16.0, -27.5, 0.01), (15.0, 12.0, 0.03), m_road)

    # Covered Motorcycle Shelter Structure (Kanopi Parkir Motor)
    # 6 steel columns holding arched corrugated canopy
    canopy_posts = [(11.0, -28.5), (15.5, -28.5), (20.0, -28.5),
                    (11.0, -24.5), (15.5, -24.5), (20.0, -24.5)]
    for idx, (px, py) in enumerate(canopy_posts):
        add_cylinder(f"CanopyPost_Motor_{idx}", (px, py, 1.3), 0.06, 2.6, m_metal_gray)
    # Canopy roof beam frame
    add_box("Canopy_Motor_Beam_S", (15.5, -28.5, 2.6), (9.5, 0.12, 0.12), m_metal_gray)
    add_box("Canopy_Motor_Beam_N", (15.5, -24.5, 2.6), (9.5, 0.12, 0.12), m_metal_gray)
    # Arched canopy roof
    add_box("Canopy_Motor_Roof", (15.5, -26.5, 2.75), (9.8, 4.6, 0.08), m_canopy_blue)

    # Motorcycle Parking Stalls (8 marked bays)
    motor_bays_x = [11.2, 12.4, 13.6, 14.8, 16.0, 17.2, 18.4, 19.6]
    for bx in [10.6] + [bx + 0.6 for bx in motor_bays_x]:
        add_box(f"Motor_Line_{bx:.1f}", (bx, -26.5, 0.03), (0.08, 2.5, 0.01), m_white_trim, col=False)
    add_box("Motor_Stall_Header", (15.4, -25.2, 0.03), (9.6, 0.15, 0.01), m_bin_green, col=False)

    # Builder for low-poly parked motorcycle
    def add_parked_motorcycle(name, center, mat_body, rotation_z=0.0):
        # Frame & chassis
        add_box_rot(f"{name}_Chassis", (center[0], center[1], center[2] + 0.45), (0.35, 1.3, 0.45), mat_body, rotation_z)
        # Black seat
        add_box_rot(f"{name}_Seat", (center[0], center[1] + 0.1, center[2] + 0.68), (0.28, 0.65, 0.12), m_dark_metal, rotation_z)
        # Handlebars & fork
        add_box_rot(f"{name}_Handlebars", (center[0], center[1] - 0.45, center[2] + 0.85), (0.7, 0.08, 0.08), m_metal_gray, rotation_z)
        # Headlight
        add_box_rot(f"{name}_Headlight", (center[0], center[1] - 0.65, center[2] + 0.75), (0.2, 0.08, 0.15), m_white_trim, rotation_z, col=False)
        # Front Wheel
        w_f = add_cylinder(f"{name}_Wheel_F", (center[0], center[1] - 0.55, center[2] + 0.3), 0.3, 0.1, m_black_tire, vertices=12)
        w_f.rotation_euler = (0, math.radians(90), rotation_z)
        # Rear Wheel
        w_r = add_cylinder(f"{name}_Wheel_R", (center[0], center[1] + 0.55, center[2] + 0.3), 0.3, 0.1, m_black_tire, vertices=12)
        w_r.rotation_euler = (0, math.radians(90), rotation_z)
        # Exhaust pipe
        add_cylinder(f"{name}_Exhaust", (center[0] + 0.22, center[1] + 0.2, center[2] + 0.25), 0.04, 0.8, m_metal_gray)

    # Park 6 distinct motorcycles in stalls
    add_parked_motorcycle("Motor_Parked_1", (11.8, -26.5, 0.0), m_motor_teal)
    add_parked_motorcycle("Motor_Parked_2", (13.0, -26.5, 0.0), m_motor_black)
    add_parked_motorcycle("Motor_Parked_3", (14.2, -26.5, 0.0), m_motor_red)
    add_parked_motorcycle("Motor_Parked_4", (16.6, -26.5, 0.0), m_motor_white)
    add_parked_motorcycle("Motor_Parked_5", (17.8, -26.5, 0.0), m_car_blue)
    add_parked_motorcycle("Motor_Parked_6", (19.0, -26.5, 0.0), m_motor_black)

    # Bicycle Racks & Bicycles Area
    for i in range(5):
        rx = 10.5 + i * 1.2
        add_box(f"Bike_Rack_Post_L_{i}", (rx, -22.5, 0.45), (0.05, 0.05, 0.9), m_metal_gray)
        add_box(f"Bike_Rack_Post_R_{i}", (rx, -21.5, 0.45), (0.05, 0.05, 0.9), m_metal_gray)
        add_box(f"Bike_Rack_Bar_{i}", (rx, -22.0, 0.88), (0.05, 1.05, 0.05), m_metal_gray)

    # Low poly bicycles
    def add_parked_bicycle(name, center, mat_color):
        # Frame diamond
        add_box(f"{name}_Frame", (center[0], center[1], center[2] + 0.5), (0.04, 1.0, 0.4), mat_color, col=False)
        # Wheels
        for wy in [-0.55, 0.55]:
            w = add_cylinder(f"{name}_W_{wy}", (center[0], center[1] + wy, center[2] + 0.35), 0.35, 0.04, m_black_tire, vertices=12, col=False)
            w.rotation_euler = (0, math.radians(90), 0)
        # Handlebars & Seat
        add_box(f"{name}_Handlebars", (center[0], center[1] - 0.4, center[2] + 0.85), (0.5, 0.05, 0.05), m_metal_gray, col=False)
        add_box(f"{name}_Seat", (center[0], center[1] + 0.2, center[2] + 0.75), (0.15, 0.22, 0.05), m_dark_metal, col=False)

    add_parked_bicycle("Bicycle_1", (11.7, -22.0, 0.0), m_car_red)
    add_parked_bicycle("Bicycle_2", (12.9, -22.0, 0.0), m_solar_blue)
    add_parked_bicycle("Bicycle_3", (14.1, -22.0, 0.0), m_white_trim)

    # -------------------------------------------------------------------------
    # 7. CONTINUOUS, DETAILED PEDESTRIAN PATHWAYS (REQUIREMENT 3)
    # -------------------------------------------------------------------------
    print("Building detailed, continuous pedestrian path network...")
    # Main Central Promenade: From street gate (Y = -34.5) to monument (Y = -17.5) and front stairs (Y = -5.0)
    # Width = 4.4m (X = -2.2 to +2.2), fully paved with Mat_PavingBlock
    add_box("Promenade_Main_South", (0.0, -26.0, 0.02), (4.4, 17.0, 0.02), m_paving, col=False)
    add_box("Promenade_Main_North", (0.0, -11.0, 0.02), (4.4, 12.0, 0.02), m_paving, col=False)

    # Side decorative borders along promenade (strictly parallel along edges, NO curbs across path!)
    add_box("Promenade_Border_W1", (-2.25, -26.0, 0.03), (0.15, 17.0, 0.03), m_curb, col=False)
    add_box("Promenade_Border_E1", (2.25, -26.0, 0.03), (0.15, 17.0, 0.03), m_curb, col=False)
    add_box("Promenade_Border_W2", (-2.25, -11.0, 0.03), (0.15, 12.0, 0.03), m_curb, col=False)
    add_box("Promenade_Border_E2", (2.25, -11.0, 0.03), (0.15, 12.0, 0.03), m_curb, col=False)

    # Central Monument Plaza (around "SCHOOL" sign, Y = -17.5)
    add_box("Plaza_Monument_Floor", (0.0, -17.5, 0.02), (9.0, 7.0, 0.02), m_paving, col=False)

    # Central Flag Plaza (around Flagpole, Y = -11.0)
    add_box("Plaza_Flag_Floor", (0.0, -11.0, 0.025), (7.0, 5.0, 0.02), m_paver_edge, col=False)

    # Left Cross-Walkway: Promenade to Car Parking & West Wing
    # Connects X = -2.2 cleanly across to X = -8.8 (seamless flat paving, no curb obstacles)
    add_box("Path_Cross_Left", (-5.5, -21.0, 0.02), (6.6, 2.4, 0.02), m_paving, col=False)
    # Side curbs along North and South edges of the cross path
    add_box("Path_Cross_Left_BorderN", (-5.5, -19.75, 0.03), (6.6, 0.12, 0.03), m_curb, col=False)
    add_box("Path_Cross_Left_BorderS", (-5.5, -22.25, 0.03), (6.6, 0.12, 0.03), m_curb, col=False)

    # Right Cross-Walkway: Promenade to Motorcycle Parking & Bus Halte
    add_box("Path_Cross_Right", (5.5, -21.0, 0.02), (6.6, 2.4, 0.02), m_paving, col=False)
    add_box("Path_Cross_Right_BorderN", (5.5, -19.75, 0.03), (6.6, 0.12, 0.03), m_curb, col=False)
    add_box("Path_Cross_Right_BorderS", (5.5, -22.25, 0.03), (6.6, 0.12, 0.03), m_curb, col=False)

    # Walkway to Bus Halte along front sidewalk
    add_box("Path_To_Halte", (3.0, -34.8, 0.02), (2.4, 3.4, 0.02), m_paving, col=False)

    # Building Facade Apron Walkways (running in front of West and East wings)
    # West Wing Front Walkway: X = [-2.2 to -21.0], Y = -5.0 to -7.0
    add_box("Walkway_Facade_West", (-11.5, -5.8, 0.02), (18.6, 2.0, 0.02), m_paving, col=False)
    # East Wing Front Walkway: X = [2.2 to 21.0], Y = -5.0 to -7.0
    add_box("Walkway_Facade_East", (11.5, -5.8, 0.02), (18.6, 2.0, 0.02), m_paving, col=False)

    # -------------------------------------------------------------------------
    # 8. RICH PROPS & DETAILS (REQUIREMENT 4)
    # -------------------------------------------------------------------------
    print("Adding rich props (Pos Satpam, Flagpole, 3-Color Bins, Signs)...")
    remove_objects_by_prefix([
        "PosSatpam_", "Flagpole_", "Flag_MerahPutih", "TrashBin_", "DirSign_", "GardenBench_"
    ])

    # --- POS SATPAM (SECURITY GUARD HOUSE) ---
    # Located near the main gate at X = -5.5, Y = -32.0
    satpam_x, satpam_y = -5.5, -31.8
    # Concrete plinth
    add_box("PosSatpam_Floor", (satpam_x, satpam_y, 0.1), (3.0, 2.4, 0.2), m_sidewalk)
    # Walls (Light cream/orange walls)
    add_box("PosSatpam_Wall_Back", (satpam_x, satpam_y + 1.1, 1.4), (2.8, 0.15, 2.4), m_white_trim)
    add_box("PosSatpam_Wall_Left", (satpam_x - 1.35, satpam_y, 1.4), (0.15, 2.2, 2.4), m_white_trim)
    add_box("PosSatpam_Wall_Right", (satpam_x + 1.35, satpam_y, 1.4), (0.15, 2.2, 2.4), m_white_trim)
    # Front Wall with service window
    add_box("PosSatpam_Wall_Front_L", (satpam_x - 0.9, satpam_y - 1.1, 1.4), (0.8, 0.15, 2.4), m_white_trim)
    add_box("PosSatpam_Wall_Front_R", (satpam_x + 0.9, satpam_y - 1.1, 1.4), (0.8, 0.15, 2.4), m_white_trim)
    add_box("PosSatpam_Wall_Front_Low", (satpam_x, satpam_y - 1.1, 0.5), (1.0, 0.15, 0.8), m_white_trim)
    add_box("PosSatpam_Wall_Front_High", (satpam_x, satpam_y - 1.1, 2.3), (1.0, 0.15, 0.6), m_white_trim)
    # Window glass
    add_box("PosSatpam_Glass", (satpam_x, satpam_y - 1.1, 1.4), (0.95, 0.04, 1.0), m_glass, col=False)
    # Overhanging roof canopy
    add_box("PosSatpam_Roof", (satpam_x, satpam_y, 2.7), (3.4, 2.8, 0.2), m_canopy_blue)
    # Sign "POS SATPAM"
    add_box("PosSatpam_SignBoard", (satpam_x, satpam_y - 1.45, 2.7), (1.8, 0.08, 0.35), m_sidewalk)

    # --- TIANG BENDERA MERAH PUTIH (FLAGPOLE & INDONESIAN FLAG) ---
    # Located in central plaza at X = 0.0, Y = -11.0
    flag_x, flag_y = 0.0, -11.0
    # Tiered circular base (white stone)
    add_cylinder("Flagpole_Plinth_Low", (flag_x, flag_y, 0.12), 1.4, 0.24, m_white_trim)
    add_cylinder("Flagpole_Plinth_Mid", (flag_x, flag_y, 0.28), 1.0, 0.18, m_white_trim)
    add_cylinder("Flagpole_Plinth_Top", (flag_x, flag_y, 0.42), 0.6, 0.18, m_white_trim)
    # Mast pole (white steel)
    add_cylinder("Flagpole_Mast", (flag_x, flag_y, 4.5), 0.06, 8.2, m_white_trim)
    # Gold finial on top
    add_cylinder("Flagpole_Finial", (flag_x, flag_y, 8.65), 0.12, 0.15, m_gold, col=False)
    # Indonesian Flag (Merah Putih: top red, bottom white)
    # Red Top Half
    add_box_rot("Flag_MerahPutih_Red", (flag_x + 0.9, flag_y, 8.1), (1.8, 0.02, 0.6), m_flag_red, rotation_z=math.radians(10), col=False)
    # White Bottom Half
    add_box_rot("Flag_MerahPutih_White", (flag_x + 0.9, flag_y, 7.5), (1.8, 0.02, 0.6), m_flag_white, rotation_z=math.radians(10), col=False)

    # --- 3-COLOR SEPARATED TRASH BINS (TEMPAT SAMPAH 3 WARNA) ---
    def add_trash_bin_set(prefix, center, rotation_z=0.0):
        # Steel stand frame
        add_box_rot(f"{prefix}_Stand", (center[0], center[1], center[2] + 0.15), (1.3, 0.35, 0.3), m_dark_metal, rotation_z, col=False)
        # Green (Organik)
        add_cylinder(f"{prefix}_Green", (center[0] - 0.42, center[1], center[2] + 0.5), 0.16, 0.6, m_bin_green)
        # Yellow (Anorganik)
        add_cylinder(f"{prefix}_Yellow", (center[0], center[1], center[2] + 0.5), 0.16, 0.6, m_bin_yellow)
        # Red (B3/Residu)
        add_cylinder(f"{prefix}_Red", (center[0] + 0.42, center[1], center[2] + 0.5), 0.16, 0.6, m_bin_red)

    add_trash_bin_set("TrashBin_Gate", (-3.5, -31.5, 0.0))
    add_trash_bin_set("TrashBin_Plaza", (-3.0, -17.5, 0.0))
    add_trash_bin_set("TrashBin_Porch", (4.5, -4.5, 0.0))

    # --- DIRECTIONAL SIGNPOSTS (PETUNJUK ARAH) ---
    def add_direction_signpost(name, center):
        # Post
        add_cylinder(f"{name}_Post", (center[0], center[1], center[2] + 1.25), 0.05, 2.5, m_dark_metal)
        # Left arrow sign (Parkir Mobil)
        add_box_rot(f"{name}_SignL", (center[0] - 0.45, center[1], center[2] + 2.2), (0.8, 0.04, 0.22), m_canopy_blue, rotation_z=0.0, col=False)
        # Right arrow sign (Parkir Motor)
        add_box_rot(f"{name}_SignR", (center[0] + 0.45, center[1], center[2] + 1.9), (0.8, 0.04, 0.22), m_canopy_blue, rotation_z=0.0, col=False)
        # Forward sign (Gedung Utama)
        add_box_rot(f"{name}_SignF", (center[0], center[1] - 0.45, center[2] + 1.6), (0.04, 0.8, 0.22), m_canopy_blue, rotation_z=0.0, col=False)

    add_direction_signpost("DirSign_Plaza", (2.8, -17.5, 0.0))
    add_direction_signpost("DirSign_Entrance", (-2.6, -31.0, 0.0))

    # --- GARDEN BENCHES ---
    def add_bench(name, center, rotation_z=0.0):
        # Legs
        add_box_rot(f"{name}_LegL", (center[0] - 0.7, center[1], center[2] + 0.22), (0.1, 0.45, 0.44), m_dark_metal, rotation_z)
        add_box_rot(f"{name}_LegR", (center[0] + 0.7, center[1], center[2] + 0.22), (0.1, 0.45, 0.44), m_dark_metal, rotation_z)
        # Wood seat slats
        add_box_rot(f"{name}_Seat", (center[0], center[1], center[2] + 0.45), (1.6, 0.5, 0.06), m_door_wood, rotation_z)
        # Backrest
        add_box_rot(f"{name}_Back", (center[0], center[1] + 0.2, center[2] + 0.75), (1.6, 0.06, 0.4), m_door_wood, rotation_z)

    add_bench("Bench_Plaza_W", (-3.6, -15.5, 0.0), rotation_z=math.radians(90))
    add_bench("Bench_Plaza_E", (3.6, -15.5, 0.0), rotation_z=math.radians(-90))
    add_bench("Bench_Promenade_W", (-2.9, -23.0, 0.0), rotation_z=math.radians(90))
    add_bench("Bench_Promenade_E", (2.9, -23.0, 0.0), rotation_z=math.radians(-90))

    # -------------------------------------------------------------------------
    # 9. INTERIOR 2ND FLOOR (LANTAI 2), STAIRS & ELEVATOR (REQUIREMENT 5)
    # -------------------------------------------------------------------------
    print("Building Interior Lantai 2, Stairs & Elevator...")
    remove_objects_by_prefix([
        "Floor2_", "Railing2_", "Stairs_Interior_", "Elevator_"
    ])

    # Ceiling of Floor 1 = Bottom of Floor 2 = Z 4.15m.
    # Floor 2 Top Walking Surface = Z 4.40m.
    # Thickness = 0.25m.
    f2_z = 4.275
    f2_th = 0.25

    # --- LANTAI 2 FLOOR SLABS ---
    # Left Wing Floor 2
    add_box("Floor2_LeftWing", (-13.5, 8.0, f2_z), (15.0, 10.0, f2_th), m_interior)
    add_box("Floor2_LeftWingFwd", (-17.0, -2.0, f2_z), (8.0, 10.0, f2_th), m_interior)

    # Right Wing Floor 2
    add_box("Floor2_RightWing", (13.5, 8.0, f2_z), (15.0, 10.0, f2_th), m_interior)
    add_box("Floor2_RightWingFwd", (17.0, -2.0, f2_z), (8.0, 10.0, f2_th), m_interior)

    # Center Hall Floor 2 - MEZZANINE WITH CENTRAL ATRIUM OPENING
    # North bridge connecting left and right wings (Y = 9.0 to 13.0)
    add_box("Floor2_Center_North", (0.0, 11.0, f2_z), (12.0, 4.0, f2_th), m_interior)
    # South bridge overlooking entrance (Y = -1.0 to 2.5)
    add_box("Floor2_Center_South", (0.0, 0.75, f2_z), (12.0, 3.5, f2_th), m_interior)
    # West top landing at head of stairs (X = -6.0 to -3.2, Y = 9.0 to 13.0)
    # Note: Stairwell is open from Y = 2.5 to 9.0 so player has full headroom!
    add_box("Floor2_Center_WestLanding", (-4.6, 11.0, f2_z), (2.8, 4.0, f2_th), m_interior)
    # East corridor walkway (X = 3.2 to 6.0, Y = 2.5 to 9.0)
    add_box("Floor2_Center_East", (4.6, 5.75, f2_z), (2.8, 6.5, f2_th), m_interior)
    # Center Atrium Void is open from X = -3.2 to +3.2, Y = 2.5 to 9.0!

    # --- LANTAI 2 ATRIUM SAFETY RAILINGS (Height 1.0m, Z = 4.40 to 5.40) ---
    # South edge of atrium (along Y = 2.5)
    add_box("Railing2_Atrium_South", (0.0, 2.5, 4.9), (6.4, 0.08, 1.0), m_metal_gray)
    add_box("Railing2_Atrium_South_Glass", (0.0, 2.5, 4.85), (6.3, 0.04, 0.8), m_glass, col=False)
    # North edge of atrium (along Y = 9.0)
    add_box("Railing2_Atrium_North", (0.0, 9.0, 4.9), (6.4, 0.08, 1.0), m_metal_gray)
    add_box("Railing2_Atrium_North_Glass", (0.0, 9.0, 4.85), (6.3, 0.04, 0.8), m_glass, col=False)
    # West edge of atrium (along X = -3.2, leaving opening for stairs landing at Y = 8.5 to 9.0)
    add_box("Railing2_Atrium_West", (-3.2, 5.5, 4.9), (0.08, 6.0, 1.0), m_metal_gray)
    add_box("Railing2_Atrium_West_Glass", (-3.2, 5.5, 4.85), (0.04, 5.9, 0.8), m_glass, col=False)
    # East edge of atrium (along X = 3.2, leaving opening for elevator entrance at Y = 7.0 to 8.5)
    add_box("Railing2_Atrium_East_S", (3.2, 4.5, 4.9), (0.08, 4.0, 1.0), m_metal_gray)

    # --- LANTAI 2 INTERIOR ROOM PARTITIONS ---
    # Classroom partition walls on Lantai 2 Left Wing
    add_box("Floor2_Wall_Class_L1", (-13.5, 8.0, 6.6), (0.2, 10.0, 4.4), m_white_trim)
    add_box("Floor2_Wall_Class_R1", (13.5, 8.0, 6.6), (0.2, 10.0, 4.4), m_white_trim)

    # --- INTERIOR STAIRCASE TO LANTAI 2 ---
    # Runs along the west wall of the center atrium:
    # From Lantai 1 (Y = 3.0, Z = 0.40) up to Lantai 2 (Y = 8.8, Z = 4.40).
    # Width = 1.6m (X = -4.9 to -3.3, center X = -4.1).
    stair_w = 1.6
    stair_cx = -4.1
    num_steps = 16
    run_len = 5.8
    rise_total = 4.0  # from 0.40 to 4.40
    step_run = run_len / num_steps
    step_rise = rise_total / num_steps

    for s in range(num_steps):
        sy = 3.0 + s * step_run + step_run / 2.0
        # Step top height
        sz_top = 0.40 + (s + 1) * step_rise
        # Build step block
        step_h = sz_top - 0.40
        add_box(f"Stairs_Interior_Step_{s}", (stair_cx, sy, 0.40 + step_h / 2.0), (stair_w, step_run, step_h), m_white_trim, col=False)

    # Sturdy handrails on both sides of stairs
    add_box_rot("Stairs_Interior_Rail_L", (stair_cx - stair_w/2, 5.9, 3.35), (0.06, 6.6, 0.08), m_metal_gray, rotation_z=0.0, col=False)
    add_box_rot("Stairs_Interior_Rail_R", (stair_cx + stair_w/2, 5.9, 3.35), (0.06, 6.6, 0.08), m_metal_gray, rotation_z=0.0, col=False)

    # --- ELEVATOR (LIFT) SHAFT & CABIN ---
    # Placed on East side of atrium: X = [3.6, 5.6], Y = [6.8, 8.8]
    elev_cx, elev_cy = 4.6, 7.8
    # 4 Vertical Steel Corner Shaft Columns from Floor 1 (Z = 0.40) to Ceiling (Z = 8.80)
    for px in [3.6, 5.6]:
        for py in [6.8, 8.8]:
            add_box(f"Elevator_Shaft_Col_{px}_{py}", (px, py, 4.6), (0.12, 0.12, 8.4), m_metal_gray)

    # Shaft top beam enclosure & machine room cover at Z = 8.8
    add_box("Elevator_Shaft_TopCover", (elev_cx, elev_cy, 8.75), (2.2, 2.2, 0.3), m_dark_metal)

    # Glass walls enclosing the back and outer sides of the shaft
    # North side (Y = 8.8)
    add_box("Elevator_Shaft_Glass_N", (elev_cx, 8.8, 4.6), (1.9, 0.04, 8.0), m_glass, col=False)
    # East side (X = 5.6)
    add_box("Elevator_Shaft_Glass_E", (5.6, elev_cy, 4.6), (0.04, 1.9, 8.0), m_glass, col=False)

    # Elevator Cabin Structure (At Floor 1 position: Z = 0.40)
    # Floor platform
    add_box("Elevator_Cabin_Floor", (elev_cx, elev_cy, 0.48), (1.8, 1.8, 0.15), m_sidewalk)
    # Safety walls on East, North, South inside cabin
    add_box("Elevator_Cabin_Wall_N", (elev_cx, elev_cy + 0.85, 1.6), (1.7, 0.06, 2.1), m_metal_gray)
    add_box("Elevator_Cabin_Wall_E", (elev_cx + 0.85, elev_cy, 1.6), (0.06, 1.7, 2.1), m_metal_gray)
    add_box("Elevator_Cabin_Wall_S", (elev_cx, elev_cy - 0.85, 1.6), (1.7, 0.06, 2.1), m_metal_gray)
    # Cabin ceiling & lamp
    add_box("Elevator_Cabin_Ceiling", (elev_cx, elev_cy, 2.65), (1.8, 1.8, 0.1), m_dark_metal)
    add_box("Elevator_Cabin_Lamp", (elev_cx, elev_cy, 2.58), (0.5, 0.5, 0.04), m_white_trim, col=False)
    # Control Panel inside cabin
    add_box("Elevator_Cabin_Panel", (elev_cx + 0.8, elev_cy - 0.3, 1.4), (0.06, 0.25, 0.5), m_dark_metal, col=False)

    # Call button pillars outside on Lantai 1 and Lantai 2
    add_box("Elevator_CallPillar_F1", (3.35, 7.0, 1.2), (0.1, 0.18, 0.3), m_dark_metal, col=False)
    add_box("Elevator_CallPillar_F2", (3.35, 7.0, 5.2), (0.1, 0.18, 0.3), m_dark_metal, col=False)

    # -------------------------------------------------------------------------
    # 10. FRONT ENTRANCE STAIRS VERIFICATION (REQUIREMENT 1)
    # -------------------------------------------------------------------------
    # Ensure visual steps have NO collision suffix
    for s_name in ["Stairs_Step_1", "Stairs_Step_2", "Stairs_Step_3", "Step_0", "Step_1", "Step_2", "Step_Landing", "Porch_Platform"]:
        obj = bpy.data.objects.get(s_name)
        if obj and obj.name.endswith("-col"):
            obj.name = obj.name[:-4]

    # Clean up orphan data blocks
    bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

    # -------------------------------------------------------------------------
    # 11. SAVE BLEND & EXPORT GLB
    # -------------------------------------------------------------------------
    models_dir = "/home/clemoryn/Documents/GitHub/gameproject01/game/new-game-project/assets/models"
    blend_out = os.path.join(models_dir, "campus_area.blend")
    glb_out = os.path.join(models_dir, "campus_area.glb")

    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"Saved blend file to: {blend_out}")

    bpy.ops.export_scene.gltf(
        filepath=glb_out,
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    print(f"Exported GLB successfully to: {glb_out}")

run_update()
