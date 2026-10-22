extends SceneTree

func _init():
	print("Converting GLB to Godot PackedScene with Trimesh Collisions and Glass Transparency...")
	var gltf = GLTFDocument.new()
	var state = GLTFState.new()
	var err = gltf.append_from_file("res://assets/models/kampung_kos_gang.glb", state)
	if err != OK:
		printerr("Error loading GLB: ", err)
		quit(1)
		return
	
	var root = gltf.generate_scene(state)
	print("Scene generated with ", root.get_child_count(), " objects.")

	# Setup glass materials (Crystal Clear Glass!)
	var window_glass_mat = StandardMaterial3D.new()
	window_glass_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	window_glass_mat.albedo_color = Color(0.88, 0.95, 1.0, 0.12)
	window_glass_mat.roughness = 0.02
	window_glass_mat.metallic = 0.05
	window_glass_mat.cull_mode = BaseMaterial3D.CULL_DISABLED

	var showcase_glass_mat = StandardMaterial3D.new()
	showcase_glass_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	showcase_glass_mat.albedo_color = Color(0.90, 0.96, 1.0, 0.10)
	showcase_glass_mat.roughness = 0.02
	showcase_glass_mat.metallic = 0.05
	showcase_glass_mat.cull_mode = BaseMaterial3D.CULL_DISABLED

	var water_mat = StandardMaterial3D.new()
	water_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	water_mat.albedo_color = Color(0.15, 0.65, 0.90, 0.78)
	water_mat.roughness = 0.05
	water_mat.metallic = 0.15
	water_mat.cull_mode = BaseMaterial3D.CULL_DISABLED

	var frosted_glass_mat = StandardMaterial3D.new()
	frosted_glass_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	frosted_glass_mat.albedo_color = Color(0.82, 0.88, 0.94, 0.45)
	frosted_glass_mat.roughness = 0.65
	frosted_glass_mat.metallic = 0.05
	frosted_glass_mat.cull_mode = BaseMaterial3D.CULL_DISABLED

	var col_count = 0
	var glass_count = 0

	for child in root.get_children():
		if child is MeshInstance3D:
			var node_name = child.name
			if node_name.ends_with("-col"):
				child.create_trimesh_collision()
				col_count += 1
			
			# Apply glass material override for transparent elements
			if "Glass" in node_name or "Shelf" in node_name or "Window" in node_name or ("Toples" in node_name and not "Lid" in node_name and not "Fill" in node_name):
				if "Showcase" in node_name or "Warteg" in node_name or "Kerupuk" in node_name or "Gelas" in node_name:
					child.material_override = showcase_glass_mat
				elif "Player_Window" in node_name or "WinStreet" in node_name or "Win_F1" in node_name or "Win_F2" in node_name:
					child.material_override = window_glass_mat
				else:
					child.material_override = frosted_glass_mat
				glass_count += 1
			elif "Water" in node_name or "Air_Teh" in node_name:
				child.material_override = water_mat
				glass_count += 1

	print("Added trimesh collision to ", col_count, " meshes.")
	print("Applied transparency material to ", glass_count, " glass meshes.")
	_set_owner_recursive(root, root)

	var packed = PackedScene.new()
	var pack_err = packed.pack(root)
	if pack_err != OK:
		printerr("Pack error: ", pack_err)
		quit(1)
		return

	var save_err = ResourceSaver.save(packed, "res://assets/models/kampung_kos_gang_model.tscn")
	print("Saved to kampung_kos_gang_model.tscn! Result: ", save_err)
	quit()

func _set_owner_recursive(node: Node, root_node: Node):
	for child in node.get_children():
		child.owner = root_node
		_set_owner_recursive(child, root_node)
