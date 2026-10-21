class_name BusHaltePortal
extends Area3D

@export_file("*.tscn") var target_scene_path: String = "res://main.tscn"
@export var prompt_text: String = "[F] Naik Bus Pulang ke Kampung Kos"
@export var travel_message: String = "Menaiki bus dan kembali pulang ke Kampung Kos..."
@export var fade_duration: float = 0.6

var _player: CharacterBody3D = null
var _is_player_inside: bool = false
var _is_transitioning: bool = false

func _ready() -> void:
	collision_mask = 0xFFFFFFFF
	collision_layer = 0
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node3D) -> void:
	if _is_transitioning:
		return
	if body.is_in_group("player") or body is CharacterBody3D or body.name.to_lower().contains("player"):
		_player = body as CharacterBody3D
		_is_player_inside = true
		if _player and _player.has_method("_show_prompt"):
			_player._show_prompt(prompt_text)

func _on_body_exited(body: Node3D) -> void:
	if body == _player:
		if _player and _player.has_method("_hide_prompt"):
			_player._hide_prompt()
		_is_player_inside = false
		_player = null

func _process(_delta: float) -> void:
	if _is_player_inside and _player and not _is_transitioning:
		if _player.has_method("_show_prompt"):
			_player._show_prompt(prompt_text)
		
		# Allow F key (or E)
		if Input.is_physical_key_pressed(KEY_F) or Input.is_action_just_pressed("interact_f") or Input.is_action_just_pressed("interact"):
			_trigger_portal()

func _unhandled_input(event: InputEvent) -> void:
	if _is_player_inside and not _is_transitioning:
		if event is InputEventKey and event.pressed:
			if event.physical_keycode == KEY_F or event.keycode == KEY_F:
				_trigger_portal()
				get_viewport().set_input_as_handled()
		elif event.is_action_pressed("interact_f") or event.is_action_pressed("interact"):
			_trigger_portal()
			get_viewport().set_input_as_handled()

func _trigger_portal() -> void:
	if _is_transitioning:
		return
	_is_transitioning = true
	print("[BusHaltePortal] Player pressed F! Transitioning to: ", target_scene_path)
	
	if _player and _player.has_method("show_notice"):
		_player.show_notice(travel_message, 2.5)
	if _player and _player.has_method("_hide_prompt"):
		_player._hide_prompt()
		
	SceneTransition.transition_to_scene(target_scene_path, travel_message, fade_duration)
