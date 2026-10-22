class_name ElevatorController
extends Node3D

enum FloorState {
	FLOOR_1,
	FLOOR_2,
	MOVING
}

@export var floor_1_y: float = 0.40
@export var floor_2_y: float = 4.40
@export var travel_time: float = 3.0

@export var cabin_body: AnimatableBody3D
@export var cabin_panel: CollisionObject3D
@export var call_button_f1: CollisionObject3D
@export var call_button_f2: CollisionObject3D

var current_floor: int = 1
var state: FloorState = FloorState.FLOOR_1
var _tween: Tween = null

func _ready() -> void:
	if cabin_body:
		cabin_body.position.y = floor_1_y
	current_floor = 1
	state = FloorState.FLOOR_1
	_update_prompts()

func _update_prompts() -> void:
	if cabin_panel and cabin_panel.has_method("set_prompt"):
		if state == FloorState.MOVING:
			cabin_panel.set_prompt("Lift sedang bergerak...")
		elif current_floor == 1:
			cabin_panel.set_prompt("Naik ke Lantai 2")
		else:
			cabin_panel.set_prompt("Turun ke Lantai 1")

	if call_button_f1 and call_button_f1.has_method("set_prompt"):
		if state == FloorState.MOVING:
			call_button_f1.set_prompt("Lift sedang bergerak...")
		elif current_floor == 1:
			call_button_f1.set_prompt("Lift sudah di Lantai 1")
		else:
			call_button_f1.set_prompt("Panggil Lift ke Lantai 1")

	if call_button_f2 and call_button_f2.has_method("set_prompt"):
		if state == FloorState.MOVING:
			call_button_f2.set_prompt("Lift sedang bergerak...")
		elif current_floor == 2:
			call_button_f2.set_prompt("Lift sudah di Lantai 2")
		else:
			call_button_f2.set_prompt("Panggil Lift ke Lantai 2")

func interact_cabin(actor: Node = null) -> void:
	if state == FloorState.MOVING:
		return
	var target_floor = 2 if current_floor == 1 else 1
	move_to_floor(target_floor, actor)

func interact_call_f1(actor: Node = null) -> void:
	if state == FloorState.MOVING:
		return
	if current_floor == 1:
		if actor and actor.has_method("show_notice"):
			actor.show_notice("Lift sudah berada di Lantai 1.", 2.0)
		return
	move_to_floor(1, actor)

func interact_call_f2(actor: Node = null) -> void:
	if state == FloorState.MOVING:
		return
	if current_floor == 2:
		if actor and actor.has_method("show_notice"):
			actor.show_notice("Lift sudah berada di Lantai 2.", 2.0)
		return
	move_to_floor(2, actor)

func move_to_floor(target_floor: int, actor: Node = null) -> void:
	if state == FloorState.MOVING or target_floor == current_floor:
		return

	state = FloorState.MOVING
	_update_prompts()

	if actor and actor.has_method("show_notice"):
		actor.show_notice("Lift bergerak menuju Lantai %d..." % target_floor, 3.0)

	var target_y = floor_2_y if target_floor == 2 else floor_1_y

	if _tween and _tween.is_valid():
		_tween.kill()

	_tween = create_tween()
	_tween.set_trans(Tween.TRANS_QUAD)
	_tween.set_ease(Tween.EASE_IN_OUT)
	_tween.tween_property(cabin_body, "position:y", target_y, travel_time)
	_tween.finished.connect(_on_arrival.bind(target_floor, actor))

func _on_arrival(target_floor: int, actor: Node = null) -> void:
	current_floor = target_floor
	state = FloorState.FLOOR_2 if current_floor == 2 else FloorState.FLOOR_1
	_update_prompts()

	if actor and actor.has_method("show_notice"):
		actor.show_notice("Tiba di Lantai %d. Pintu lift terbuka." % current_floor, 2.5)
