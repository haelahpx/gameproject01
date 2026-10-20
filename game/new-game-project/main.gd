extends Node3D

func _ready() -> void:
	TimeManager.minute_changed.connect(_on_minute)
	TimeManager.player_fainted.connect(_on_faint)

func _on_minute(_min: int) -> void:
	print("Jam Game: ", TimeManager.get_time_string(), " | ", TimeManager.get_date_string())

func _on_faint() -> void:
	print(">>> PLAYER PINGSAN (JAM 03:00)! <<<")