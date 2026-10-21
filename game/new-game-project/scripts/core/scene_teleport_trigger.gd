class_name SceneTeleportTrigger
extends Area3D

@export_file("*.tscn") var target_scene_path: String = ""
@export var fade_duration: float = 0.5
@export var transition_label: String = "Menuju Kampus..."

var _is_transitioning: bool = false

func _ready() -> void:
	collision_mask = 0xFFFFFFFF
	collision_layer = 0
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node3D) -> void:
	if _is_transitioning:
		return
	if body.is_in_group("player") or body.name.to_lower().contains("player") or body is CharacterBody3D:
		trigger_teleport()

func trigger_teleport() -> void:
	if target_scene_path.is_empty():
		push_warning("[SceneTeleportTrigger] Target scene path not configured.")
		return
	_is_transitioning = true
	print("[SceneTeleportTrigger] Starting teleport to: ", target_scene_path)
	SceneTransition.transition_to_scene(target_scene_path, transition_label, fade_duration)
