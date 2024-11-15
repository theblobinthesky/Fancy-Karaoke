using Godot;
using System;

public partial class NotenLeiste : Node2D
{
	private const float pixelsPerSecond = 100.0f;
	private const float startX = 960.0f;
	private const float startY = 80.0f;
	private const float xPerLine = -40.0f;
	
	private int drift_index = 1;
	
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
	
	public void add_singing_node(float line, float offset)
	{
		Sprite2D note = new Sprite2D();
		note.Texture = GD.Load<Texture2D>("res://textures/own_note_texture.tres");
		var pos = note.Position;
		pos.X = offset + 960.0f;
		pos.Y = startY + xPerLine * line;
		note.Position = pos;
		this.GetNode<Node2D>("OwnNotes").AddChild(note);
	}
	
	public void load_notes(Godot.Collections.Array notes)
	{
		for (int i = 0; i < notes.Count; i++)
		{
			Godot.Collections.Dictionary noteDat = (Godot.Collections.Dictionary) notes[i];
			Sprite2D note = new Sprite2D();
			note.Texture = GD.Load<Texture2D>("res://textures/note_texture.tres");
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
