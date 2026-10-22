class_name InteractiveTeleport
extends Interactable

@export_file("*.tscn") var target_scene_path: String = "res://scenes/levels/campus_area.tscn"
@export var fade_duration: float = 0.6
@export var travel_message: String = "Berangkat menuju area kampus..."

var _is_transitioning: bool = false

func interact(actor: Node = null) -> void:
	if not is_interactable or _is_transitioning or target_scene_path.is_empty():
		return
	_is_transitioning = true
	
	if actor and actor.has_method("show_notice"):
		actor.show_notice(travel_message, 2.0)
	
	SceneTransition.transition_to_scene(target_scene_path, travel_message, fade_duration)
