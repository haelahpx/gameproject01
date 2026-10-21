extends SceneTree

func _init():
	print("--- TESTING LEVEL INTERACTIONS & STAIRS SETUP ---")
	var level_scene = load("res://scenes/levels/kampung_kos_level.tscn")
	if not level_scene:
		printerr("FAILED to load kampung_kos_level.tscn")
		quit(1)
		return

	var root = level_scene.instantiate()
	root_node_check(root)
	quit()

func root_node_check(root: Node):
	# Check stairs collider
	var stairs = root.get_node_or_null("StairsRampCollider")
	assert(stairs != null, "StairsRampCollider missing!")
	print("✔ StairsRampCollider found at transform: ", stairs.transform.origin, " rotation basis: ", stairs.transform.basis)

	# Check signboard
	var signboard = root.get_node_or_null("Interact_Signboard")
	assert(signboard != null, "Interact_Signboard missing!")
	print("✔ Interact_Signboard found: prompt='", signboard.prompt_message, "', text='", signboard.inspection_text, "'")

	# Check locked doors
	for i in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
		var door_name = "Interact_Door_Room%02d" % i
		var door = root.get_node_or_null(door_name)
		assert(door != null, "Missing door: " + door_name)
		assert(door.inspection_text.contains("tidak memiliki akses"), "Door inspection text does not mention access: " + door_name)
		print("✔ ", door_name, " verified: prompt='", door.prompt_message, "', notice='", door.inspection_text, "'")

	# Check WC door, Bak Mandi, Kloset
	var wc_door = root.get_node_or_null("DoorHingeWC/WCDoor")
	assert(wc_door != null, "WCDoor missing!")
	print("✔ WCDoor found: open_prompt='", wc_door.open_prompt, "', close_prompt='", wc_door.close_prompt, "'")

	var bak = root.get_node_or_null("Interact_BakMandi")
	assert(bak != null, "Interact_BakMandi missing!")
	print("✔ Interact_BakMandi found: prompt='", bak.prompt_message, "'")

	var kloset = root.get_node_or_null("Interact_Kloset")
	assert(kloset != null, "Interact_Kloset missing!")
	print("✔ Interact_Kloset found: prompt='", kloset.prompt_message, "'")

	# Check Player door
	var player_door = root.get_node_or_null("DoorHingePlayer/PlayerDoor")
	assert(player_door != null, "PlayerDoor missing!")
	print("✔ PlayerDoor found: open_prompt='", player_door.open_prompt, "'")

	print("--- ALL 16 LEVEL CHECKS PASSED PERFECTLY! ---")
