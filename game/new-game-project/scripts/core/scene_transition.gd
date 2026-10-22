extends CanvasLayer

var _is_transitioning: bool = false
var _overlay: ColorRect
var _label: Label

func _ready() -> void:
	layer = 120
	process_mode = Node.PROCESS_MODE_ALWAYS
	
	_overlay = ColorRect.new()
	_overlay.color = Color(0, 0, 0, 0)
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_overlay)
	
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	center.mouse_filter = Control.MOUSE_FILTER_IGNORE
	
	_label = Label.new()
	_label.text = ""
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_label.add_theme_font_size_override("font_size", 20)
	_label.modulate = Color(1, 1, 1, 0)
	center.add_child(_label)
	add_child(center)

func transition_to_scene(target_path: String, label_text: String = "", duration: float = 0.5) -> void:
	if _is_transitioning:
		return
	if target_path.is_empty():
		push_warning("[SceneTransition] Target scene path is empty.")
		return
	
	_is_transitioning = true
	_overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	_label.text = label_text
	
	# Phase 1: Fade out to solid black
	var tween := create_tween().set_parallel(true)
	tween.tween_property(_overlay, "color:a", 1.0, duration)
	if not label_text.is_empty():
		tween.tween_property(_label, "modulate:a", 1.0, duration * 0.8)
	
	await tween.finished
	
	# Phase 2: Perform the actual scene switch
	var err := get_tree().change_scene_to_file(target_path)
	if err != OK:
		push_error("[SceneTransition] Failed to change scene to: %s (error %d)" % [target_path, err])
		_overlay.color.a = 0.0
		_label.modulate.a = 0.0
		_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_is_transitioning = false
		return
	
	# Wait for the new scene tree to be active and fully settled
	await get_tree().process_frame
	await get_tree().process_frame
	
	# Phase 3: Fade in from black in the new scene
	var fade_in := create_tween().set_parallel(true)
	fade_in.tween_property(_overlay, "color:a", 0.0, 0.4)
	fade_in.tween_property(_label, "modulate:a", 0.0, 0.3)
	
	await fade_in.finished
	
	_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_is_transitioning = false
