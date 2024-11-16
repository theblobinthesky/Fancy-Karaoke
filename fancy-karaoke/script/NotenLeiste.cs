using Godot;
using System;

public partial class NotenLeiste : Node2D
{
	private const float pixelsPerSecond = 100.0f;
	private const float startX = 960.0f;
	private const float startY = 80.0f;
	private const float xPerLine = -40.0f;
	
	private int drift_index = 1;
	
	private int song_note_index = 0;
	private double song_note_min = Double.MaxValue;
	
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
	
	public (double, Sprite2D) add_singing_node(float line, float offset)
	{
		Sprite2D note = new Sprite2D();
		note.Texture = GD.Load<Texture2D>("res://textures/own_note_texture.tres");
		var pos = note.Position;
		pos.X = offset + 960.0f;
		pos.Y = startY + xPerLine * line;
		note.Position = pos;
		this.GetNode<Node2D>("OwnNotes").AddChild(note);
		
		double dist = Double.NaN;
		Sprite2D songNote = null;
		
		Godot.Collections.Array<Node> songNotes = GetNode<Node2D>("SongNotes").GetChildren();

		if (song_note_index < songNotes.Count && Math.Abs(((Sprite2D) songNotes[song_note_index]).Position.X - pos.X) < 15.0f) {
			double current_dist = Math.Abs(((Sprite2D) songNotes[song_note_index]).Position.Y - pos.Y);
			if (current_dist < song_note_min) {
				song_note_min = current_dist;
			}
		} else if (song_note_index < songNotes.Count && song_note_min < Double.MaxValue && Math.Abs(pos.X - ((Sprite2D) songNotes[song_note_index]).Position.X) > 15.0f) {
			dist = song_note_min;
			songNote = (Sprite2D) songNotes[song_note_index];
			song_note_index++;
			song_note_min = Double.MaxValue;
		}
		
		return (dist, songNote);
	}
	
	public void load_notes(Godot.Collections.Array notes)
	{
		GradientTexture2D resTexture = GD.Load<GradientTexture2D>("res://textures/note_texture.tres");
		for (int i = 0; i < notes.Count; i++)
		{
			Godot.Collections.Dictionary noteDat = (Godot.Collections.Dictionary) notes[i];
			Sprite2D note = new Sprite2D();
			
			GradientTexture2D nodeTexture = new GradientTexture2D();
			nodeTexture.Width = resTexture.Width;
			nodeTexture.Height = resTexture.Height;
			nodeTexture.Fill = resTexture.Fill;
			nodeTexture.FillFrom = resTexture.FillFrom;
			
			nodeTexture.Gradient = new Gradient();
			float[] offsets = { resTexture.Gradient.Offsets[0], resTexture.Gradient.Offsets[1] };
			nodeTexture.Gradient.Offsets = offsets;
			Color[] colors = { resTexture.Gradient.Colors[0], resTexture.Gradient.Colors[1] };
			nodeTexture.Gradient.Colors = colors;
			
			note.Texture = (GradientTexture2D) nodeTexture;
			var pos = note.Position;
			pos.X = startX + pixelsPerSecond * noteDat["timestamp"].As<float>();
			pos.Y = startY + xPerLine * noteDat["line"].As<int>();
			note.Position = pos;
			this.GetNode<Node2D>("SongNotes").AddChild(note);
		}
	}
	
	public void drift_lines() {
		Node2D lineNode = this.GetNode<Node2D>(string.Format("Lines{0}", drift_index));
		var pos = lineNode.Position;
		pos.X += 4000.0f;
		lineNode.Position = pos;
		if (drift_index == 1) {
			drift_index = 2;
		} else {
			drift_index = 1;
		}
		
		Godot.Collections.Array<Node> childs = GetNode<Node2D>("OwnNotes").GetChildren();
		for(int i = 0; i < childs.Count; i++) {
			if (childs[i] is Sprite2D) {
				var sprite = (Sprite2D) childs[i];
				if (sprite.Position.X < pos.X - 2000.0f) {
					GetNode<Node2D>("OwnNotes").RemoveChild(sprite);
					sprite.QueueFree();
				}
			}
		}
	}
}
