class_name SceneTeleportTrigger
extends Area3D

@export_file("*.tscn") var target_scene_path: String = ""
@export var fade_duration: float = 0.8

var _is_transitioning: bool = false

func _ready() -> void:
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node3D) -> void:
	if _is_transitioning:
		return
	if body.is_in_group("player") or body.name.to_lower().contains("player"):
		trigger_teleport()

func trigger_teleport() -> void:
	if target_scene_path.is_empty():
		print("[SceneTeleportTrigger] Target scene path not configured yet.")
		return
	_is_transitioning = true
	# Fade out logic (using ColorRect canvas layer or direct scene change)
	var tween := create_tween()
	var fade_overlay := ColorRect.new()
	fade_overlay.color = Color(0, 0, 0, 0)
	fade_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	
	var canvas := CanvasLayer.new()
	canvas.layer = 100
	canvas.add_child(fade_overlay)
	get_tree().root.add_child(canvas)
	
	tween.tween_property(fade_overlay, "color:a", 1.0, fade_duration)
	tween.finished.connect(func():
		get_tree().change_scene_to_file(target_scene_path)
		canvas.queue_free()
	)
