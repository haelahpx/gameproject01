class_name MobileControls
extends Control

@export var look_sensitivity: float = 1.0
@export var auto_detect_mobile: bool = true

@onready var controls_layer: Control = $ControlsLayer
@onready var touch_look_zone: Control = $ControlsLayer/TouchLookZone
@onready var joystick: TouchJoystick = $ControlsLayer/VirtualJoystick
@onready var btn_interact: Button = $ControlsLayer/ActionButtons/BtnInteract
@onready var btn_jump: Button = $ControlsLayer/ActionButtons/BtnJump
@onready var btn_sprint: Button = $ControlsLayer/ActionButtons/BtnSprint
@onready var btn_toggle_ui: Button = $BtnToggleUI

var _look_touch_index: int = -1
var _player: CharacterBody3D = null

func _ready() -> void:
	# Find player reference
	_player = get_tree().get_first_node_in_group("player") as CharacterBody3D
	if not _player:
		# Fallback: check parent or ancestors
		var current = get_parent()
		while current:
			if current is CharacterBody3D:
				_player = current
				break
			current = current.get_parent()

	# Connect buttons
	if btn_interact:
		btn_interact.pressed.connect(_on_interact_pressed)
	if btn_jump:
		btn_jump.pressed.connect(_on_jump_pressed)
	if btn_sprint:
		btn_sprint.pressed.connect(_on_sprint_pressed)
	if btn_toggle_ui:
		btn_toggle_ui.pressed.connect(_on_toggle_ui_pressed)

	if touch_look_zone:
		touch_look_zone.gui_input.connect(_on_look_zone_gui_input)

	# Listen to InputRouter toggle
	InputRouter.touch_controls_toggled.connect(_on_touch_controls_toggled)

	# Initial state
	if auto_detect_mobile and InputRouter.is_mobile():
		InputRouter.set_touch_controls_active(true)
	else:
		_apply_ui_visibility(InputRouter.touch_controls_active)

func _process(_delta: float) -> void:
	if not controls_layer.visible:
		return

	# Highlight sprint button if active
	if btn_sprint:
		var sprinting = InputRouter.is_sprinting()
		if sprinting:
			btn_sprint.modulate = Color(1.0, 0.85, 0.3, 1.0) # Golden/amber active glow
		else:
			btn_sprint.modulate = Color(1.0, 1.0, 1.0, 0.85)

	# Highlight interact button when facing interactable
	if btn_interact:
		var can_interact = false
		if _player and _player.has_method("is_facing_interactable"):
			can_interact = _player.is_facing_interactable()
		
		if can_interact:
			btn_interact.modulate = Color(0.3, 1.0, 0.6, 1.0) # Bright emerald ready glow
		else:
			btn_interact.modulate = Color(0.85, 0.9, 1.0, 0.8)

func _on_touch_controls_toggled(active: bool) -> void:
	_apply_ui_visibility(active)

func _apply_ui_visibility(active: bool) -> void:
	if controls_layer:
		controls_layer.visible = active
	if btn_toggle_ui:
		if active:
			btn_toggle_ui.text = "📱 Mode HP: ON"
			btn_toggle_ui.modulate = Color(0.4, 0.9, 0.5, 0.9)
		else:
			btn_toggle_ui.text = "📱 Mode HP: OFF"
			btn_toggle_ui.modulate = Color(1.0, 1.0, 1.0, 0.6)

func _on_interact_pressed() -> void:
	InputRouter.trigger_virtual_interact()

func _on_jump_pressed() -> void:
	InputRouter.trigger_virtual_jump()

func _on_sprint_pressed() -> void:
	InputRouter.toggle_virtual_sprint()

func _on_toggle_ui_pressed() -> void:
	InputRouter.set_touch_controls_active(not InputRouter.touch_controls_active)

func _on_look_zone_gui_input(event: InputEvent) -> void:
	# Touch screen events
	if event is InputEventScreenTouch:
		if event.pressed and _look_touch_index == -1:
			_look_touch_index = event.index
			accept_event()
		elif not event.pressed and event.index == _look_touch_index:
			_look_touch_index = -1
			accept_event()

	elif event is InputEventScreenDrag:
		if event.index == _look_touch_index:
			InputRouter.add_virtual_look(event.relative * look_sensitivity)
			accept_event()

	# Mouse emulation / desktop preview events
	elif event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed and _look_touch_index == -1:
				_look_touch_index = -99
				accept_event()
			elif not event.pressed and _look_touch_index == -99:
				_look_touch_index = -1
				accept_event()

	elif event is InputEventMouseMotion:
		if _look_touch_index == -99:
			InputRouter.add_virtual_look(event.relative * look_sensitivity)
			accept_event()
