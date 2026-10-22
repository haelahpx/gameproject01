class_name TouchJoystick
extends Control

@export var max_radius: float = 65.0
@export var handle_radius: float = 28.0
@export var deadzone: float = 8.0

# Styling colors
@export var base_color: Color = Color(0.08, 0.10, 0.16, 0.55)
@export var border_color: Color = Color(0.35, 0.55, 0.85, 0.70)
@export var handle_color: Color = Color(0.25, 0.60, 0.95, 0.85)
@export var handle_border_color: Color = Color(1.0, 1.0, 1.0, 0.90)

var _center: Vector2 = Vector2.ZERO
var _handle_pos: Vector2 = Vector2.ZERO
var _is_dragging: bool = false
var _touch_index: int = -1

func _ready() -> void:
	_center = size / 2.0
	_handle_pos = _center
	queue_redraw()

func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		_center = size / 2.0
		if not _is_dragging:
			_handle_pos = _center
		queue_redraw()

func _draw() -> void:
	# Base circle
	draw_circle(_center, max_radius, base_color)
	draw_arc(_center, max_radius, 0.0, TAU, 36, border_color, 2.5, true)
	# Inner subtle crosshairs / guidelines
	draw_line(_center - Vector2(max_radius * 0.4, 0), _center + Vector2(max_radius * 0.4, 0), Color(border_color.r, border_color.g, border_color.b, 0.25), 1.5)
	draw_line(_center - Vector2(0, max_radius * 0.4), _center + Vector2(0, max_radius * 0.4), Color(border_color.r, border_color.g, border_color.b, 0.25), 1.5)
	# Handle knob
	draw_circle(_handle_pos, handle_radius, handle_color)
	draw_arc(_handle_pos, handle_radius, 0.0, TAU, 28, handle_border_color, 2.0, true)

func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed and not _is_dragging:
			var touch_dist = (event.position - _center).length()
			if touch_dist <= max_radius * 1.3:
				_start_drag(event.position, event.index)
				accept_event()
		elif not event.pressed and event.index == _touch_index:
			_stop_drag()
			accept_event()

	elif event is InputEventScreenDrag:
		if _is_dragging and event.index == _touch_index:
			_update_drag(event.position)
			accept_event()

	# Mouse fallback for desktop testing
	elif event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed and not _is_dragging:
				var touch_dist = (event.position - _center).length()
				if touch_dist <= max_radius * 1.3:
					_start_drag(event.position, -1)
					accept_event()
			elif not event.pressed and _touch_index == -1:
				_stop_drag()
				accept_event()

	elif event is InputEventMouseMotion:
		if _is_dragging and _touch_index == -1:
			_update_drag(event.position)
			accept_event()

func _start_drag(pos: Vector2, index: int) -> void:
	_is_dragging = true
	_touch_index = index
	_update_drag(pos)

func _update_drag(pos: Vector2) -> void:
	var diff = pos - _center
	var dist = diff.length()
	if dist > max_radius:
		diff = diff.normalized() * max_radius
	
	_handle_pos = _center + diff
	queue_redraw()
	
	var norm_vec = Vector2.ZERO
	if dist > deadzone:
		norm_vec = diff / max_radius
	
	# Send movement vector to InputRouter (x = horizontal, y = forward/back)
	InputRouter.set_virtual_move(norm_vec)

func _stop_drag() -> void:
	_is_dragging = false
	_touch_index = -1
	_handle_pos = _center
	queue_redraw()
	InputRouter.set_virtual_move(Vector2.ZERO)

func reset() -> void:
	_stop_drag()
