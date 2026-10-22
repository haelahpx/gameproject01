extends CharacterBody3D

@export var walk_speed: float = 4.0
@export var sprint_speed: float = 7.0
@export var mouse_sensitivity: float = 0.002
@export var arrow_look_speed: float = 2.4
@export var head_bob_enabled: bool = true
@export var head_bob_frequency: float = 2.4
@export var head_bob_amplitude: float = 0.05
@export var gravity: float = 9.8
@export var jump_velocity: float = 4.5

@onready var camera: Camera3D = $Camera3D
@onready var raycast: RayCast3D = $Camera3D/RayCast3D
@onready var prompt_container: Control = get_node_or_null("HUD/PromptContainer")
@onready var prompt_label: Label = get_node_or_null("HUD/PromptContainer/PromptLabel")
@onready var notice_container: Control = get_node_or_null("HUD/NoticeContainer")
@onready var notice_label: Label = get_node_or_null("HUD/NoticeContainer/NoticeLabel")

var head_bob_time: float = 0.0
var default_cam_y: float = 1.5
var _notice_timer: float = 0.0

func _ready() -> void:
	add_to_group("player")
	InputRouter.capture_mouse(true)
	if not InputRouter.touch_controls_active:
		InputRouter.capture_mouse(true)
	floor_max_angle = deg_to_rad(50.0)
	floor_snap_length = 0.45
	floor_constant_speed = true
	if camera:
		default_cam_y = camera.position.y
	_hide_prompt()
	_hide_notice()

func _process(delta: float) -> void:
	if _notice_timer > 0.0:
		_notice_timer -= delta
		if _notice_timer <= 0.0:
			_hide_notice()

func _physics_process(delta: float) -> void:
	_handle_rotation(delta)
	_handle_movement(delta)
	_handle_interaction()

func _handle_rotation(delta: float) -> void:
	var delta_mouse = InputRouter.consume_look_delta()
	var arrow_look = InputRouter.get_arrow_look_vector()
	
	# Horizontal yaw rotation (mouse delta + arrow keys):
	# Mouse: -delta_mouse.x * mouse_sensitivity
	# Arrow: Left (-1) rotates +Y (turn left), Right (+1) rotates -Y (turn right)
	var yaw_change = -delta_mouse.x * mouse_sensitivity - arrow_look.x * arrow_look_speed * delta
	rotate_y(yaw_change)
	
	if camera:
		# Vertical pitch rotation (mouse delta + arrow keys):
		# Mouse: -delta_mouse.y * mouse_sensitivity
		# Arrow: Up (+1) pitches camera up (+X rotation), Down (-1) pitches camera down (-X rotation)
		var pitch_change = -delta_mouse.y * mouse_sensitivity + arrow_look.y * arrow_look_speed * delta
		camera.rotate_x(pitch_change)
		camera.rotation.x = clamp(camera.rotation.x, deg_to_rad(-89), deg_to_rad(89))

func is_facing_interactable() -> bool:
	if not raycast or not raycast.is_colliding():
		return false
	return _find_interactable(raycast.get_collider()) != null

func _handle_movement(delta: float) -> void:
	var move_vec = InputRouter.get_move_vector()
	var direction = (transform.basis * Vector3(move_vec.x, 0, move_vec.y)).normalized()
	var is_sprinting = InputRouter.is_sprinting()
	var current_speed = sprint_speed if is_sprinting else walk_speed

	if direction:
		velocity.x = direction.x * current_speed
		velocity.z = direction.z * current_speed
	else:
		velocity.x = move_toward(velocity.x, 0, current_speed)
		velocity.z = move_toward(velocity.z, 0, current_speed)

	if is_on_floor() and InputRouter.is_jump_just_pressed():
		velocity.y = jump_velocity

	if not is_on_floor():
		velocity.y -= gravity * delta

	move_and_slide()
	_handle_head_bob(delta, direction.length() > 0 and is_on_floor())

func _handle_head_bob(delta: float, is_moving: bool) -> void:
	if not camera:
		return
	if not head_bob_enabled:
		camera.position.y = move_toward(camera.position.y, default_cam_y, delta * 4.0)
		return

	if is_moving:
		head_bob_time += delta * velocity.length() * head_bob_frequency
		camera.position.y = default_cam_y + sin(head_bob_time) * head_bob_amplitude
	else:
		head_bob_time = 0.0
		camera.position.y = move_toward(camera.position.y, default_cam_y, delta * 2.0)

func set_head_bob_enabled(enabled: bool) -> void:
	head_bob_enabled = enabled
	if not enabled and camera:
		camera.position.y = default_cam_y

func _find_interactable(collider: Object) -> Object:
	if not collider:
		return null
	if collider is Interactable or collider.has_method("interact"):
		return collider
	for child in collider.get_children():
		if child is Interactable or child.has_method("interact"):
			return child
	var parent = collider.get_parent()
	if parent and (parent is Interactable or parent.has_method("interact")):
		return parent
	return null

func _get_prompt_string(target: Object) -> String:
	if target.has_method("get_prompt"):
		return target.get_prompt()
	elif "prompt_message" in target:
		return str(target.prompt_message)
	return "Interaksi"

func _handle_interaction() -> void:
	if not raycast:
		return
	if raycast.is_colliding():
		var collider = raycast.get_collider()
		var target = _find_interactable(collider)
		if target:
			var prompt_text = _get_prompt_string(target)
			_show_prompt("[E] " + prompt_text)
			if InputRouter.is_interact_just_pressed():
				target.interact(self)
				_show_prompt("[E] " + _get_prompt_string(target))
				if "inspection_text" in target and str(target.inspection_text) != "":
					show_notice(str(target.inspection_text))
			return
	_hide_prompt()

func _show_prompt(text: String) -> void:
	if prompt_label:
		prompt_label.text = text
	if prompt_container:
		prompt_container.visible = true
	elif prompt_label:
		prompt_label.visible = true

func _hide_prompt() -> void:
	if prompt_container:
		prompt_container.visible = false
	elif prompt_label:
		prompt_label.visible = false

func show_notice(text: String, duration: float = 3.5) -> void:
	if notice_label:
		notice_label.text = text
	if notice_container:
		notice_container.visible = true
	_notice_timer = duration

func _hide_notice() -> void:
	if notice_container:
		notice_container.visible = false
