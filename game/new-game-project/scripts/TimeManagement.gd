## Production-ready Autoload (Singleton) script managing in-game time, calendar system,
## day/night cycles, sleep cycles, and fainting mechanics in Godot 4 (GDScript 2.0).
## Configured so 1 in-game hour consists of exactly 30 in-game minutes (00 to 29).
extends Node

# ==============================================================================
# SIGNALS
# ==============================================================================

## Emitted every time an in-game minute ticks forward (guaranteed 0 to 29).
signal minute_changed(current_minute: int)

## Emitted every time an in-game hour changes (06 to 27 / 03:00 AM).
signal hour_changed(current_hour: int)

## Emitted when a new day begins with day, month, and year.
signal day_changed(day: int, month: int, year: int)

## Emitted when the calendar advances to a new year.
signal year_changed(current_year: int)

## Emitted when time reaches 03:00 AM (hour 27) and the player collapses from exhaustion.
signal player_fainted

## Emitted when the player wakes up, specifying the wake hour and whether it was from fainting.
signal player_woke_up(wake_hour: int, was_fainted: bool)


# ==============================================================================
# CONSTANTS
# ==============================================================================

## Calendar month names (Indonesian, 12 months per year).
const MONTH_NAMES: Array[String] = [
	"Januari", "Februari", "Maret", "April", "Mei", "Juni",
	"Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

## Number of in-game minutes in one in-game hour (0 to 29).
const MINUTES_PER_HOUR: int = 30

## Total days in each month (fixed 28 days calendar).
const DAYS_PER_MONTH: int = 28

## Total months in each year.
const MONTHS_PER_YEAR: int = 12

## Standard day start hour (06:00 AM).
const WAKE_HOUR_NORMAL: int = 6

## Late day start hour when recovering from fainting in hospital (08:00 AM).
const WAKE_HOUR_FAINTED: int = 8

## Cutoff hour when player collapses (27 = 03:00 AM next morning).
const FAINT_HOUR: int = 27


# ==============================================================================
# TIME SCALE & TICK CONFIGURATION
# ==============================================================================

@export_group("Time Scale")
## Real-world seconds per in-game minute.
## Ratio: 1 in-game hour = 30 in-game minutes = 15 real-world seconds (0.5s per minute).
@export var minute_duration: float = 0.5


# ==============================================================================
# STATE & CALENDAR VARIABLES
# ==============================================================================

@export_group("Calendar State")
## Current in-game minute (0 to 29).
@export var current_minute: int = 0

## Current in-game hour (Daily cycle: 6 = 06:00 AM to 27 = 03:00 AM next morning).
@export var current_hour: int = 6

## Current day of the month (1 to 28).
@export var current_day: int = 1

## Current month of the year (1 to 12).
@export var current_month: int = 1

## Current year (1 to unlimited).
@export var current_year: int = 1

## Whether the passage of time is currently halted.
@export var is_paused: bool = false

## Whether the player is currently in a fainted state awaiting a new day.
@export var is_fainted: bool = false


# ==============================================================================
# MISSION & TITLE PLACEHOLDERS
# ==============================================================================

@export_group("Mission System Placeholders")
## Number of missions successfully completed by the player.
@export var completed_missions: int = 0

## Target mission threshold required to qualify for success title.
@export var target_missions: int = 100

## Maximum calendar years allowed to fulfill the target mission quota.
@export var max_target_years: int = 4

## Title awarded if target missions are not achieved within the target years.
@export var title_fail: String = "Title A"

## Title awarded if target missions are met by target years.
@export var title_success: String = "Title B"


# ==============================================================================
# PRIVATE ENGINE STATE
# ==============================================================================

## Accumulates delta time in seconds toward the next minute tick.
var _timer: float = 0.0


# ==============================================================================
# LIFECYCLE & PROCESS LOOP
# ==============================================================================

func _process(delta: float) -> void:
	if is_paused or minute_duration <= 0.0:
		return

	_timer += delta

	# Process minute ticks while compensating for frame delta spikes
	while _timer >= minute_duration:
		_timer -= minute_duration
		_advance_minute()

		# Stop immediately if an event (e.g. fainting) paused the game during the tick
		if is_paused:
			break


## Advances time by one in-game minute and handles hour overflow and fainting.
## Guaranteed to reset current_minute to 0 BEFORE minute_changed is emitted when reaching 30.
func _advance_minute() -> void:
	current_minute += 1

	if current_minute >= MINUTES_PER_HOUR:
		current_minute = 0
		current_hour += 1
		hour_changed.emit(current_hour)

		# Exhaustion threshold reached at 03:00 AM (hour 27)
		if current_hour >= FAINT_HOUR:
			is_fainted = true
			pause()
			player_fainted.emit()

	# Guaranteed: current_minute is always in range 0..29, never 30
	minute_changed.emit(current_minute)


# ==============================================================================
# DATE ADVANCEMENT LOGIC
# ==============================================================================

## Advances day, month, and year counters according to the 28-day calendar.
func _advance_day() -> void:
	current_day += 1

	if current_day > DAYS_PER_MONTH:
		current_day = 1
		current_month += 1

		if current_month > MONTHS_PER_YEAR:
			current_month = 1
			current_year += 1
			year_changed.emit(current_year)

	day_changed.emit(current_day, current_month, current_year)


# ==============================================================================
# CORE CONTROL METHODS
# ==============================================================================

## Freezes in-game time advancement.
func pause() -> void:
	is_paused = true


## Resumes in-game time advancement.
func resume() -> void:
	is_paused = false


## Triggered when the player sleeps normally before 03:00 AM.
## Advances the day, resets clock to 06:00 AM, notifies listeners, and resumes time.
func sleep() -> void:
	_timer = 0.0
	_advance_day()

	current_hour = WAKE_HOUR_NORMAL
	current_minute = 0

	hour_changed.emit(current_hour)
	minute_changed.emit(current_minute)
	player_woke_up.emit(current_hour, false)
	resume()


## Triggered when waking up after fainting from exhaustion at 03:00 AM (hospital wake-up).
## Advances the day, sets clock to 08:00 AM penalty, clears faint flag, notifies listeners, and resumes time.
func wake_up_from_faint() -> void:
	_timer = 0.0
	_advance_day()

	current_hour = WAKE_HOUR_FAINTED
	current_minute = 0
	is_fainted = false

	hour_changed.emit(current_hour)
	minute_changed.emit(current_minute)
	player_woke_up.emit(current_hour, true)
	resume()


# ==============================================================================
# FORMATTING & QUERY HELPERS
# ==============================================================================

## Returns formatted time string.
## By default, displays extended military time (e.g. "06:00", "06:29", "26:15").
## If wrap_to_24h is true, hours >= 24 wrap to standard 00:00–03:00 range.
func get_time_string(wrap_to_24h: bool = false) -> String:
	var display_hour: int = (current_hour % 24) if wrap_to_24h else current_hour
	return "%02d:%02d" % [display_hour, current_minute]


## Returns formatted date string in Indonesian (e.g. "1 Januari, Th. 1").
func get_date_string() -> String:
	var month_name: String = ""
	if current_month >= 1 and current_month <= MONTH_NAMES.size():
		month_name = MONTH_NAMES[current_month - 1]
	else:
		month_name = "Bulan %d" % current_month

	return "%d %s, Th. %d" % [current_day, month_name, current_year]


## Returns formatted time string in 12-hour AM/PM notation (e.g. "06:00 AM", "06:29 AM").
func get_time_string_12h() -> String:
	var normalized_hour: int = current_hour % 24
	var period: String = "AM" if normalized_hour < 12 else "PM"
	var hour_12: int = normalized_hour % 12
	if hour_12 == 0:
		hour_12 = 12
	return "%02d:%02d %s" % [hour_12, current_minute, period]


## Evaluates the player's performance against the target mission quota placeholder.
## Returns the corresponding title or an empty string if evaluation period has not elapsed.
func get_evaluated_title() -> String:
	if current_year >= max_target_years:
		return title_success if completed_missions >= target_missions else title_fail
	return ""
