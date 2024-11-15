extends Node2D

const SingleKaraoke = preload("res://scenes/main_karaoke.tscn")

@export
var playerCount: int = 2

@export
var songName: String = "Test"

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var gridCount = roundi(sqrt(playerCount))
	
	var vertical = get_node("MultiViewVertical")
	
	var i = 0
	while i < playerCount:
		var hBox = HBoxContainer.new()
		hBox.alignment = BoxContainer.ALIGNMENT_CENTER
		hBox.custom_minimum_size = Vector2(1920.0, 1080.0 / ceil(sqrt(playerCount)))
		
		var j = 0
		while j < gridCount && j < playerCount - i:
			var container = SubViewportContainer.new()
			container.stretch = true
			container.custom_minimum_size = Vector2(1920.0 / ceil(sqrt(playerCount)), 0.0)
			var subView = SubViewport.new()
			container.add_child(subView)
			var subScene = SingleKaraoke.instantiate()
			subScene.load_song(songName)
			var factor = 1.0 / ceil(sqrt(playerCount))
			subScene.scale = Vector2(factor, factor)
			subView.add_child(subScene)
			
			hBox.add_child(container)
			j = j + 1
		
		vertical.add_child(hBox)
		i = i + j
		
		var player = (get_node("MusicPlayer") as AudioStreamPlayer);
		player.stream = load("res://music/" + songName + ".mp3");
		player.play()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta: float) -> void:
	pass
