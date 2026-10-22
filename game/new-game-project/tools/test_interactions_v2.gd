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
	assert(signboard.prompt_message.contains("Kondang"), "Signboard prompt does not say Kondang!")
	assert(signboard.inspection_text.contains("KOST KONDANG"), "Signboard text does not say KOST KONDANG!")
	print("✔ Interact_Signboard verified: prompt='", signboard.prompt_message, "', text='", signboard.inspection_text, "'")

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

	# Check Interactive Sliding Gates (House 2 and House 4 have NO fence/gate)
	assert(root.get_node_or_null("SlidingGate_House2") == null, "SlidingGate_House2 should be deleted!")
	assert(root.get_node_or_null("SlidingGate_House4") == null, "SlidingGate_House4 should be deleted!")
	print("✔ House 2 & House 4 confirmed to have NO fence/gate (open front terraces)")

	# Check Jemuran interaction removed (now purely decorative prop)
	assert(root.get_node_or_null("Interact_Jemuran") == null, "Interact_Jemuran should be deleted!")
	print("✔ Jemuran confirmed to have NO interaction prompt (purely neighborhood decorative prop)")

	for gi in [1, 3, 5, 6]:
		var gate_name = "SlidingGate_House%d" % gi
		var gate = root.get_node_or_null(gate_name)
		assert(gate != null, "Missing sliding gate: " + gate_name)
		assert(gate.open_prompt == "Buka Pagar", "Gate open_prompt incorrect: " + gate_name)
		assert(gate.close_prompt == "Tutup Pagar", "Gate close_prompt incorrect: " + gate_name)
		print("✔ ", gate_name, " verified: prompt='", gate.get_prompt(), "', slide_offset=", gate.slide_offset)

	print("--- ALL 23 LEVEL CHECKS PASSED PERFECTLY! ---")
