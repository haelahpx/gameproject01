class_name Interactable
extends StaticBody3D

signal interacted(actor: Node)

@export var prompt_message: String = "Interaksi"
@export var is_interactable: bool = true

func get_prompt() -> String:
	return prompt_message

func set_prompt(new_prompt: String) -> void:
	prompt_message = new_prompt

func interact(actor: Node = null) -> void:
	if not is_interactable:
		return
	interacted.emit(actor)
