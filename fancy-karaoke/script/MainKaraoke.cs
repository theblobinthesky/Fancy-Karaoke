using Godot;
using System;

public partial class MainKaraoke : Node2D
{
	private double _timeBegin;
	private double _timeDelay;
	
	private const float speed = 100.0f;
	
	private int own_note_count = 0;
	
	private int last_mod_pos = 0;

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
		
		var mod_pos = ((int) Math.Floor(pos.X)) % 2000;
		
		if (mod_pos < last_mod_pos) {
			GetNode<NotenLeiste>("NotenLeiste").drift_lines();
		}
		
		last_mod_pos = mod_pos;
		
		own_note_count++;
		own_note_count %= 60;
		
		if (own_note_count == 0)
		{
			GetNode<NotenLeiste>("NotenLeiste").add_singing_node(((float) Math.Sin(time) + 1.0f) * 2.0f, pos.X);
		}
	}
	
	public void load_song(string name)
	{
		GetNode<AudioStreamPlayer>("MusicPlayer").Stream = GD.Load<AudioStream>("res://music/" + name + ".mp3");
		
		GDScript DataLoad = GD.Load<GDScript>("res://script/DataLoader.gd");
		GodotObject dataLoad = (GodotObject) DataLoad.New();
		Godot.Collections.Array notes = (Godot.Collections.Array) dataLoad.Call("read_note_data", name + "_notes");
		
		NotenLeiste main = GetNode<NotenLeiste>("NotenLeiste");
		main.load_notes(notes);
	}
	
	[Signal]
	public delegate void MusicStartEventHandler();
}
