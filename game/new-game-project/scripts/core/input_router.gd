extends Node

var look_delta: Vector2 = Vector2.ZERO
var virtual_look_delta: Vector2 = Vector2.ZERO
var virtual_move_vector: Vector2 = Vector2.ZERO
var virtual_sprint: bool = false
var virtual_interact: bool = false
var virtual_jump: bool = false

var mouse_captured: bool = true
var touch_controls_active: bool = false

signal touch_controls_toggled(active: bool)

func _ready() -> void:
	if is_mobile():
		touch_controls_active = true
		capture_mouse(false)
	else:
		capture_mouse(true)

func is_mobile() -> bool:
	return OS.has_feature("mobile") or OS.has_feature("android") or OS.has_feature("ios") or OS.has_feature("web_android") or OS.has_feature("web_ios")

func _unhandled_input(event: InputEvent) -> void:
	# Toggle mouse capture on Escape / ui_cancel
	if event.is_action_pressed("ui_cancel"):
		toggle_mouse_capture()
		get_viewport().set_input_as_handled()
		return
	
	# Recapture mouse when clicking inside the window (only if touch controls not active on desktop)
	if event is InputEventMouseButton and event.pressed and not mouse_captured and not touch_controls_active:
		capture_mouse(true)
		get_viewport().set_input_as_handled()
		return

	# Only track mouse look when mouse is captured
	if mouse_captured and event is InputEventMouseMotion:
		look_delta += event.relative

func get_move_vector() -> Vector2:
	# If virtual joystick is active, use its vector
	if virtual_move_vector.length_squared() > 0.001:
		return virtual_move_vector
	return Input.get_vector("move_left", "move_right", "move_forward", "move_back")

func get_arrow_look_vector() -> Vector2:
	var arrow_vec = Vector2.ZERO
	# Arrow keys look:
	# Left Arrow: -1.0 (turn left)
	# Right Arrow: +1.0 (turn right)
	# Up Arrow: +1.0 (look up)
	# Down Arrow: -1.0 (look down)
	if Input.is_key_pressed(KEY_LEFT) or Input.is_action_pressed("ui_left"):
		arrow_vec.x -= 1.0
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_action_pressed("ui_right"):
		arrow_vec.x += 1.0
	if Input.is_key_pressed(KEY_UP) or Input.is_action_pressed("ui_up"):
		arrow_vec.y += 1.0
	if Input.is_key_pressed(KEY_DOWN) or Input.is_action_pressed("ui_down"):
		arrow_vec.y -= 1.0
	return arrow_vec

func consume_look_delta() -> Vector2:
	var delta: Vector2 = look_delta + virtual_look_delta
	look_delta = Vector2.ZERO
	virtual_look_delta = Vector2.ZERO
	return delta

func set_virtual_move(vec: Vector2) -> void:
	virtual_move_vector = vec

func add_virtual_look(delta: Vector2) -> void:
	virtual_look_delta += delta

func set_virtual_sprint(sprint: bool) -> void:
	virtual_sprint = sprint

func toggle_virtual_sprint() -> void:
	virtual_sprint = not virtual_sprint

func trigger_virtual_interact() -> void:
	virtual_interact = true

func trigger_virtual_jump() -> void:
	virtual_jump = true

func is_sprinting() -> bool:
	return Input.is_action_pressed("sprint") or virtual_sprint

func is_interact_just_pressed() -> bool:
	var pressed = Input.is_action_just_pressed("interact") or virtual_interact
	virtual_interact = false
	return pressed

func is_interact_f_just_pressed() -> bool:
	return Input.is_action_just_pressed("interact_f")

func is_jump_just_pressed() -> bool:
	var pressed = Input.is_action_just_pressed("jump") or virtual_jump
	virtual_jump = false
	return pressed

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

func set_touch_controls_active(active: bool) -> void:
	touch_controls_active = active
	if active:
		capture_mouse(false)
	else:
		capture_mouse(true)
	touch_controls_toggled.emit(active)
