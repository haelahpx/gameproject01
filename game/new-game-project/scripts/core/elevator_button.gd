class_name ElevatorButton
extends Interactable

enum ButtonType {
	CABIN_PANEL,
	CALL_F1,
	CALL_F2
}

@export var button_type: ButtonType = ButtonType.CABIN_PANEL
@export var controller: Node

func interact(actor: Node = null) -> void:
	if not is_interactable or not controller:
		return
	match button_type:
		ButtonType.CABIN_PANEL:
			controller.interact_cabin(actor)
		ButtonType.CALL_F1:
			controller.interact_call_f1(actor)
		ButtonType.CALL_F2:
			controller.interact_call_f2(actor)
	interacted.emit(actor)
