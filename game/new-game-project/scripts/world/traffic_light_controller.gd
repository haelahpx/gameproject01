extends Node3D
class_name TrafficLightController

## Controls the 4-way intersection (perempatan) traffic lights:
## Cycles between North-South and East-West approaches:
## GREEN (7s) -> YELLOW (2.5s) -> ALL-RED (1s) -> GREEN (7s) -> etc.

@export var green_duration: float = 7.0
@export var yellow_duration: float = 2.5
@export var all_red_duration: float = 1.0

enum Phase {
	NS_GREEN,
	NS_YELLOW,
	ALL_RED_1,
	EW_GREEN,
	EW_YELLOW,
	ALL_RED_2
}

var current_phase: Phase = Phase.NS_GREEN
var phase_timer: float = 0.0

# Material instances for dynamic emission toggling
var mat_red_on: StandardMaterial3D
var mat_red_off: StandardMaterial3D
var mat_yellow_on: StandardMaterial3D
var mat_yellow_off: StandardMaterial3D
var mat_green_on: StandardMaterial3D
var mat_green_off: StandardMaterial3D

# Lens nodes grouped by approach
var ns_lenses_red: Array[MeshInstance3D] = []
var ns_lenses_yellow: Array[MeshInstance3D] = []
var ns_lenses_green: Array[MeshInstance3D] = []

var ew_lenses_red: Array[MeshInstance3D] = []
var ew_lenses_yellow: Array[MeshInstance3D] = []
var ew_lenses_green: Array[MeshInstance3D] = []

# Optional dynamic omni lights for realistic night illumination
var ns_omni_lights: Array[OmniLight3D] = []
var ew_omni_lights: Array[OmniLight3D] = []

func _ready() -> void:
	_create_materials()
	_discover_lenses(self)
	_discover_lenses_in_parent()
	_apply_phase(current_phase)
	print("[TrafficLightController] Initialized with %d NS lenses, %d EW lenses." % [
		ns_lenses_red.size() + ns_lenses_yellow.size() + ns_lenses_green.size(),
		ew_lenses_red.size() + ew_lenses_yellow.size() + ew_lenses_green.size()
	])

func _create_materials() -> void:
	# RED
	mat_red_on = StandardMaterial3D.new()
	mat_red_on.albedo_color = Color(0.95, 0.08, 0.08)
	mat_red_on.emission_enabled = true
	mat_red_on.emission = Color(1.0, 0.1, 0.1)
	mat_red_on.emission_energy_multiplier = 4.0
	mat_red_on.roughness = 0.2

	mat_red_off = StandardMaterial3D.new()
	mat_red_off.albedo_color = Color(0.25, 0.04, 0.04)
	mat_red_off.roughness = 0.6

	# YELLOW
	mat_yellow_on = StandardMaterial3D.new()
	mat_yellow_on.albedo_color = Color(0.98, 0.80, 0.05)
	mat_yellow_on.emission_enabled = true
	mat_yellow_on.emission = Color(1.0, 0.85, 0.1)
	mat_yellow_on.emission_energy_multiplier = 4.0
	mat_yellow_on.roughness = 0.2

	mat_yellow_off = StandardMaterial3D.new()
	mat_yellow_off.albedo_color = Color(0.25, 0.20, 0.02)
	mat_yellow_off.roughness = 0.6

	# GREEN
	mat_green_on = StandardMaterial3D.new()
	mat_green_on.albedo_color = Color(0.05, 0.95, 0.25)
	mat_green_on.emission_enabled = true
	mat_green_on.emission = Color(0.1, 1.0, 0.3)
	mat_green_on.emission_energy_multiplier = 4.0
	mat_green_on.roughness = 0.2

	mat_green_off = StandardMaterial3D.new()
	mat_green_off.albedo_color = Color(0.02, 0.25, 0.06)
	mat_green_off.roughness = 0.6

func _discover_lenses(node: Node) -> void:
	for child in node.get_children():
		var cname = String(child.name)
		if "TrafficLight" in cname and child is MeshInstance3D and "Lens" in cname:
			var is_ns = ("_NE_" in cname or "_SW_" in cname)
			var is_ew = ("_NW_" in cname or "_SE_" in cname)

			if "Red" in cname:
				if is_ns: ns_lenses_red.append(child)
				elif is_ew: ew_lenses_red.append(child)
			elif "Yellow" in cname:
				if is_ns: ns_lenses_yellow.append(child)
				elif is_ew: ew_lenses_yellow.append(child)
			elif "Green" in cname:
				if is_ns: ns_lenses_green.append(child)
				elif is_ew: ew_lenses_green.append(child)

		_discover_lenses(child)

func _discover_lenses_in_parent() -> void:
	if ns_lenses_red.is_empty() and get_parent():
		_discover_lenses(get_parent())

func _process(delta: float) -> void:
	phase_timer += delta

	match current_phase:
		Phase.NS_GREEN:
			if phase_timer >= green_duration:
				_set_phase(Phase.NS_YELLOW)
		Phase.NS_YELLOW:
			if phase_timer >= yellow_duration:
				_set_phase(Phase.ALL_RED_1)
		Phase.ALL_RED_1:
			if phase_timer >= all_red_duration:
				_set_phase(Phase.EW_GREEN)
		Phase.EW_GREEN:
			if phase_timer >= green_duration:
				_set_phase(Phase.EW_YELLOW)
		Phase.EW_YELLOW:
			if phase_timer >= yellow_duration:
				_set_phase(Phase.ALL_RED_2)
		Phase.ALL_RED_2:
			if phase_timer >= all_red_duration:
				_set_phase(Phase.NS_GREEN)

func _set_phase(new_phase: Phase) -> void:
	current_phase = new_phase
	phase_timer = 0.0
	_apply_phase(new_phase)

func _apply_phase(phase: Phase) -> void:
	var ns_state = "RED"
	var ew_state = "RED"

	match phase:
		Phase.NS_GREEN:
			ns_state = "GREEN"
			ew_state = "RED"
		Phase.NS_YELLOW:
			ns_state = "YELLOW"
			ew_state = "RED"
		Phase.ALL_RED_1, Phase.ALL_RED_2:
			ns_state = "RED"
			ew_state = "RED"
		Phase.EW_GREEN:
			ns_state = "RED"
			ew_state = "GREEN"
		Phase.EW_YELLOW:
			ns_state = "RED"
			ew_state = "YELLOW"

	_update_group(ns_lenses_red, ns_lenses_yellow, ns_lenses_green, ns_state)
	_update_group(ew_lenses_red, ew_lenses_yellow, ew_lenses_green, ew_state)

func _update_group(reds: Array[MeshInstance3D], yellows: Array[MeshInstance3D], greens: Array[MeshInstance3D], state: String) -> void:
	var red_mat = mat_red_on if state == "RED" else mat_red_off
	var yellow_mat = mat_yellow_on if state == "YELLOW" else mat_yellow_off
	var green_mat = mat_green_on if state == "GREEN" else mat_green_off

	for mesh in reds:
		mesh.material_override = red_mat
	for mesh in yellows:
		mesh.material_override = yellow_mat
	for mesh in greens:
		mesh.material_override = green_mat
