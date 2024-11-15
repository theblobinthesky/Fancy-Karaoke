class_name DataLoader
extends Object

func read_note_data(note_file: String) -> Array:
	var file = FileAccess.open("res://music/" + note_file + ".json", FileAccess.READ)
	return JSON.parse_string(file.get_as_text())
