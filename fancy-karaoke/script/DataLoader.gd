class_name DataLoader
extends Object

func read_note_data(song: String) -> Array:
	var file = FileAccess.open("res://music/" + song + "_notes.json", FileAccess.READ)
	return JSON.parse_string(file.get_as_text())

func read_lyrics_data(song: String) -> Array:
	var file = FileAccess.open("res://music/" + song + "_lyrics.json", FileAccess.READ)
	return JSON.parse_string(file.get_as_text())
