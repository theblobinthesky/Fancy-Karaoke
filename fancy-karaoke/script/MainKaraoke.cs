using Godot;
using System;

public partial class MainKaraoke : Node2D
{
	private double _timeBegin;
	private double _timeDelay;
	
	private const float speed = 100.0f;
	
	private int own_note_count = 0;
	
	private int last_mod_pos = 0;
	
	private Godot.Collections.Array lyrics = new Godot.Collections.Array();
	private int line_index = -1;
	private int word_index = 0;

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		_timeBegin = Time.GetTicksUsec();
		_timeDelay = AudioServer.GetTimeToNextMix() + AudioServer.GetOutputLatency();
		this.load_song("Test");
		GetNode<AudioStreamPlayer>("MusicPlayer").Play();
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
		double time = (Time.GetTicksUsec() - _timeBegin) / 1000000.0d;
		time = Math.Max(0.0d, time - _timeDelay);
		
		var cam = GetNode<Camera2D>("KaraokeCam");
		var pos = cam.Position;
		pos.X = speed * (float) time;
		cam.Position = pos;
		
		HBoxContainer lyricsContainer = GetNode<HBoxContainer>("KaraokeCam/Control/LyricsContainer");
		
		if (line_index < lyrics.Count) {
			if (line_index >= 0) {
				Godot.Collections.Dictionary line = lyrics[line_index].As<Godot.Collections.Dictionary>();
				Godot.Collections.Array words = line["word_finished"].As<Godot.Collections.Array>();
			
				if (line["offset"].As<float>() + words[words.Count - 1].As<float>() + 0.5f < time) {
					foreach (Node child in lyricsContainer.GetChildren())
					{
						lyricsContainer.RemoveChild(child);
						child.QueueFree();
					}
				} else if (word_index < words.Count && line["offset"].As<float>() + words[word_index].As<float>() < time) {
					((Label) lyricsContainer.GetChildren()[word_index]).LabelSettings = GD.Load<LabelSettings>("res://fonts/lyrics_past.tres");
					word_index++;
				}
			}
			
			if (line_index < lyrics.Count - 1 && lyrics[line_index + 1].As<Godot.Collections.Dictionary>()["offset"].As<float>() - 0.5f < time) {
				line_index++;
				word_index = 0;
				
				foreach (Node child in lyricsContainer.GetChildren())
				{
					lyricsContainer.RemoveChild(child);
					child.QueueFree();
				}
				
				Godot.Collections.Dictionary nextLine = lyrics[line_index].As<Godot.Collections.Dictionary>();
				string[] wordsText = nextLine["line"].As<string>().Split(" ");
				foreach (string wordText in wordsText) {
					Label word = new Label();
					word.LabelSettings = GD.Load<LabelSettings>("res://fonts/lyrics_future.tres");
					word.Text = wordText;
					lyricsContainer.AddChild(word);
				}
			}
		}
		
		var mod_pos = ((int) Math.Floor(pos.X)) % 2000;
		
		if (mod_pos < last_mod_pos) {
			GetNode<NotenLeiste>("NotenLeiste").drift_lines();
		}
		
		last_mod_pos = mod_pos;
		
		own_note_count++;
		own_note_count %= 60;
		
		if (own_note_count == 0)
		{
			double dist = GetNode<NotenLeiste>("NotenLeiste").add_singing_node(((float) Math.Sin(time) + 1.0f) * 2.0f, pos.X);
			if (dist < 45.0f) {
				AnimationPlayer player = GetNode<AnimationPlayer>("KaraokeCam/Control/NotifyText/AnimationPlayer");
				player.Play("PopOut");
			}
		}
	}
	
	public void load_song(string name)
	{
		GetNode<AudioStreamPlayer>("MusicPlayer").Stream = GD.Load<AudioStream>("res://music/" + name + ".mp3");
		
		GDScript DataLoad = GD.Load<GDScript>("res://script/DataLoader.gd");
		GodotObject dataLoad = (GodotObject) DataLoad.New();
		Godot.Collections.Array notes = (Godot.Collections.Array) dataLoad.Call("read_note_data", name);
		lyrics = (Godot.Collections.Array) dataLoad.Call("read_lyrics_data", name);
		
		NotenLeiste main = GetNode<NotenLeiste>("NotenLeiste");
		main.load_notes(notes);
	}
	
	[Signal]
	public delegate void MusicStartEventHandler();
}
