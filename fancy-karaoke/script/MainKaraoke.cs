using Godot;
using System;
using System.Collections.Generic;

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
	
	private int score = 0;
	
	private List<(double limit, string text, Color color, double scoreMul)> noteHits = new List<(double limit, string text, Color color, double scoreMul)>();

	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		noteHits.Add((Double.MaxValue, "Miss", new Color(1, 0, 0, 1), 0.0d));
		noteHits.Add((45.0d, "Ok", new Color(1, 1, 1, 1), 0.75d));
		noteHits.Add((30.0d, "Gut", new Color(0, 0, 1, 1), 1.0d));
		noteHits.Add((20.0d, "Super", new Color(0, 1, 0, 1), 1.5d));
		noteHits.Add((10.0d, "Hurra!", new Color(1, 0.647059f, 0, 1), 2.0d));
		noteHits.Add((2.0d, "Unglaublich!!!", new Color(1, 0.843137f, 0, 1), 5.0d));
		
		this.setup_notify_label();
		
		_timeBegin = Time.GetTicksUsec();
		_timeDelay = AudioServer.GetTimeToNextMix() + AudioServer.GetOutputLatency();
	}
	
	public void setup_player(string player) {
		Label playerLabel = GetNode<Label>("KaraokeCam/Control/Player");
		playerLabel.Text = "Player: " + player;
		LabelSettings settings = GD.Load<LabelSettings>("res://fonts/score_font.tres");
		
		Color color = Globals.Instance.TeamColors[Globals.Instance.PlayerTeams[player]];
		
		playerLabel.LabelSettings = new LabelSettings();
		playerLabel.LabelSettings.FontSize = settings.FontSize;
		playerLabel.LabelSettings.FontColor = color;
		playerLabel.LabelSettings.OutlineSize = settings.OutlineSize;
		playerLabel.LabelSettings.OutlineColor = color.Inverted();
		
		
		StyleBoxFlat style = new StyleBoxFlat();
		style.BgColor = color;
		style.BorderColor = color;
		style.BorderWidthLeft = 20;
		style.BorderWidthTop = 20;
		style.BorderWidthRight = 20;
		style.BorderWidthBottom = 20;
		
		playerLabel.AddThemeStyleboxOverride("normal", style);
	}
	
	public void setup_notify_label() {
		Label notify = GetNode<Label>("KaraokeCam/Control/NotifyText");
		LabelSettings settings = GD.Load<LabelSettings>("res://fonts/notify_font.tres");
		notify.LabelSettings = new LabelSettings();
		notify.LabelSettings.FontSize = settings.FontSize;
		notify.LabelSettings.OutlineSize = settings.OutlineSize;
		notify.LabelSettings.ShadowSize = settings.ShadowSize;
		notify.LabelSettings.ShadowColor = settings.ShadowColor;
		notify.LabelSettings.ShadowOffset = settings.ShadowOffset;
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
		own_note_count %= 10;
		
		if (own_note_count == 0)
		{
			(double, Sprite2D) dist = GetNode<NotenLeiste>("NotenLeiste").add_singing_node(((float) new Random().NextDouble()) * 4.0f, pos.X);
			if (!Double.IsNaN(dist.Item1)) {
				int hit_index = 0;
				for (; hit_index < noteHits.Count - 1 && noteHits[hit_index + 1].limit > dist.Item1; hit_index++) {}
				
				Label notify = GetNode<Label>("KaraokeCam/Control/NotifyText");
				notify.Text = noteHits[hit_index].text;
				notify.LabelSettings.FontColor = noteHits[hit_index].color;
				
				Color[] colors = ((GradientTexture2D) dist.Item2.Texture).Gradient.Colors;
				colors[0] = noteHits[hit_index].color;
				((GradientTexture2D) dist.Item2.Texture).Gradient.Colors = colors;
				
				Label notifyLabel = GetNode<Label>("KaraokeCam/Control/Score");
				if (dist.Item1 > 1) {
					score += (int) Math.Floor(-1.0 * Math.Log(1 / Math.Pow(dist.Item1, 2.0)) * noteHits[hit_index].scoreMul);
				} else if (dist.Item1 < 0.00001) {
					score += (int) (1.0 / dist.Item1 * noteHits[hit_index].scoreMul);
				} else {
					score += (int) Math.Floor(-1.0 * Math.Log(Math.Pow(dist.Item1, 4.0)) * noteHits[hit_index].scoreMul);
				}
				
				notifyLabel.Text = "Score: " + score;
				
				AnimationPlayer player = GetNode<AnimationPlayer>("KaraokeCam/Control/NotifyText/AnimationPlayer");
				player.Play("PopOut");
			}
		}
	}
	
	public void load_song(string name)
	{
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
