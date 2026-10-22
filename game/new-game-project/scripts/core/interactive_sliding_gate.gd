class_name InteractiveSlidingGate
extends Interactable

## Interactive Sliding Gate for Kampung Gang Houses
## Smoothly slides horizontally (X axis) when interacted with.

@export var slide_offset: Vector3 = Vector3(1.05, 0.0, 0.0)
@export var is_open: bool = false
@export var gate_body: Node3D
@export var open_prompt: String = "Buka Pagar"
@export var close_prompt: String = "Tutup Pagar"
@export var gate_name: String = ""
@export var slide_duration: float = 0.55

var _initial_pos: Vector3
var _initial_gate_body_pos: Vector3
var _tween: Tween

func _ready() -> void:
	_initial_pos = position
	if gate_body:
		_initial_gate_body_pos = gate_body.position
	_update_prompt()

func _update_prompt() -> void:
	var base = close_prompt if is_open else open_prompt
	if gate_name != "" and not base.ends_with(gate_name):
		prompt_message = "%s %s" % [base, gate_name]
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
	
	var target_pos = _initial_pos + (slide_offset if is_open else Vector3.ZERO)
	
	if _tween and _tween.is_valid():
		_tween.kill()
	_tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_tween.tween_property(self, "position", target_pos, slide_duration)
	
	if gate_body:
		var target_body_pos = _initial_gate_body_pos + (slide_offset if is_open else Vector3.ZERO)
		_tween.parallel().tween_property(gate_body, "position", target_body_pos, slide_duration)
	
	interacted.emit(actor)

