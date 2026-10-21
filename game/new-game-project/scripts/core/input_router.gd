extends Node

var look_delta: Vector2 = Vector2.ZERO
var mouse_captured: bool = true

func _ready() -> void:
	capture_mouse(true)

func _unhandled_input(event: InputEvent) -> void:
	# Toggle mouse capture on Escape / ui_cancel
	if event.is_action_pressed("ui_cancel"):
		toggle_mouse_capture()
		get_viewport().set_input_as_handled()
		return
	
	# Recapture mouse when clicking inside the window
	if event is InputEventMouseButton and event.pressed and not mouse_captured:
		capture_mouse(true)
		get_viewport().set_input_as_handled()
		return

	# Only track mouse look when mouse is captured
	if mouse_captured and event is InputEventMouseMotion:
		look_delta += event.relative

func get_move_vector() -> Vector2:
	return Input.get_vector("move_left", "move_right", "move_forward", "move_back")

func consume_look_delta() -> Vector2:
	var delta: Vector2 = look_delta
	look_delta = Vector2.ZERO
	return delta

func is_sprinting() -> bool:
	return Input.is_action_pressed("sprint")

func is_interact_just_pressed() -> bool:
	return Input.is_action_just_pressed("interact")

func is_jump_just_pressed() -> bool:
	return Input.is_action_just_pressed("jump")

func capture_mouse(captured: bool) -> void:
	mouse_captured = captured
	if captured:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	else:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func toggle_mouse_capture() -> void:
	capture_mouse(not mouse_captured)

func is_mouse_captured() -> bool:
	return mouse_captured
