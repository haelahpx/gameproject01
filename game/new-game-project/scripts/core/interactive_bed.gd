class_name InteractiveBed
extends Interactable

@export var sleep_prompt: String = "Tidur di Kasur"
@export var wake_prompt: String = "Bangun"
@export var fade_duration: float = 0.8
@export var sleep_duration: float = 1.5

var _is_sleeping: bool = false

func _ready() -> void:
	prompt_message = sleep_prompt

func interact(actor: Node = null) -> void:
	if not is_interactable or _is_sleeping:
		return
	
	_is_sleeping = true
	var player = actor if (actor and actor.has_method("show_notice")) else null
	
	if player:
		player.show_notice("Zzz... Tidur nyenyak di kasur lantai.", 2.5)
	
	# Create fade overlay on CanvasLayer
	var canvas = CanvasLayer.new()
	canvas.layer = 99
	var overlay = ColorRect.new()
	overlay.color = Color(0, 0, 0, 0)
	overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	canvas.add_child(overlay)
	
	var root = get_tree().root
	root.add_child(canvas)
	
	var tween = create_tween()
	# Fade to black
	tween.tween_property(overlay, "color:a", 1.0, fade_duration)
	tween.tween_interval(sleep_duration)
	# Fade back in
	tween.tween_property(overlay, "color:a", 0.0, fade_duration)
	tween.finished.connect(func():
		_is_sleeping = false
		canvas.queue_free()
		if player:
			player.show_notice("Pagi telah tiba! Badan terasa segar untuk kuliah.", 3.5)
		interacted.emit(actor)
	)
