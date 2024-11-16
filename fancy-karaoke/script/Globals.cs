using Godot;
using System;
using Godot.Collections;

public partial class Globals : Node
{
	public static Globals Instance { get; private set;}
	
	public int PlayerCount { get; set; }
	
	public Dictionary<string, string> PlayerTeams = new Dictionary<string, string>();
	public Dictionary<string, Color> TeamColors = new Dictionary<string, Color>();
	
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		Instance = this;
		TeamColors.Add("Default", new Color(1, 1, 1, 1));
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
}
