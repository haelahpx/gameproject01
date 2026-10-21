class_name InteractiveProp
extends Interactable

@export_multiline var inspection_text: String = ""
@export var toggleable_light: Light3D
@export var alternate_prompt: String = ""

var _is_toggled: bool = false

func _ready() -> void:
	if toggleable_light:
		_is_toggled = toggleable_light.visible
		_update_light_prompt()

func _update_light_prompt() -> void:
	if toggleable_light:
		if _is_toggled:
			prompt_message = "Matikan Lampu"
		else:
			prompt_message = alternate_prompt if alternate_prompt != "" else "Nyalakan Lampu"

func interact(actor: Node = null) -> void:
	if not is_interactable:
		return
	if toggleable_light:
		_is_toggled = not _is_toggled
		toggleable_light.visible = _is_toggled
		_update_light_prompt()
		inspection_text = "Lampu kamar dinyalakan." if _is_toggled else "Lampu kamar dimatikan."
	interacted.emit(actor)
