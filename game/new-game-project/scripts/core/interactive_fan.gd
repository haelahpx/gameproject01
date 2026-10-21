class_name InteractiveFan
extends Interactable

@export var fan_blades: Node3D
@export var spin_speed: float = 18.0
@export var is_running: bool = false
@export var on_prompt: String = "Nyalakan Kipas"
@export var off_prompt: String = "Matikan Kipas"

func _ready() -> void:
	prompt_message = off_prompt if is_running else on_prompt

func _process(delta: float) -> void:
	if is_running and fan_blades:
		fan_blades.rotate_z(spin_speed * delta)

func interact(actor: Node = null) -> void:
	if not is_interactable:
		return
	is_running = not is_running
	prompt_message = off_prompt if is_running else on_prompt
	interacted.emit(actor)
