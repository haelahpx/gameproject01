class_name InteractiveDoor
extends Interactable

@export var open_rotation_y: float = 90.0
@export var close_rotation_y: float = 0.0
@export var is_open: bool = false
@export var door_pivot: Node3D
@export var open_prompt: String = "Buka Pintu"
@export var close_prompt: String = "Tutup Pintu"
@export var door_name: String = ""

var _tween: Tween

func _ready() -> void:
	_update_prompt()

func _update_prompt() -> void:
	var base = close_prompt if is_open else open_prompt
	if door_name != "" and not base.ends_with(door_name):
		prompt_message = "%s %s" % [base, door_name]
	else:
		prompt_message = base

func get_prompt() -> String:
	_update_prompt()
	return prompt_message

func interact(actor: Node = null) -> void:
	if not is_interactable:
		return
	is_open = not is_open
	_update_prompt()
	var target_node: Node3D = door_pivot if door_pivot else self
	var target_deg = open_rotation_y if is_open else close_rotation_y
	
	if _tween and _tween.is_valid():
		_tween.kill()
	_tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_tween.tween_property(target_node, "rotation_degrees:y", target_deg, 0.4)
	
	interacted.emit(actor)
