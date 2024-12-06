using Godot;
using System;
using System.Collections.Generic;

public partial class StartScreen : Control
{
	private VBoxContainer players = null;
	
	private PackedScene karaoke = GD.Load<PackedScene>("res://scenes/multiplayer_karaoke.tscn");
	private PackedScene chooseTeam = GD.Load<PackedScene>("res://scenes/choose_teams.tscn");
	
	private List<string> playerList = new List<string>();
	
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		players = GetNode<VBoxContainer>("GlobalLayout/PlayerScroll/Players");
		players.ChildEnteredTree += PlayerAdded;
		players.ChildExitingTree += PlayerRemoved;
		GetNode<Button>("GlobalLayout/HBoxContainer/StartButton").Disabled = true;
		GetNode<Button>("GlobalLayout/HBoxContainer/StartButton").Pressed += StartGame;
		GetNode<Button>("GlobalLayout/HBoxContainer/ChooseTeams").Pressed += ChooseTeams;
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
		int rand = new Random().Next(100);
		
		if (rand == 0) {
			Label label = new Label();
			label.LabelSettings = GD.Load<LabelSettings>("res://fonts/score_font.tres");
			label.Text = "Player: " + (playerList.Count + 1).ToString();
			
			playerList.Add((playerList.Count + 1).ToString());
			
			players.AddChild(label);
		}
	}
	
	public void PlayerAdded(Node child) {
		GetNode<Button>("GlobalLayout/HBoxContainer/StartButton").Disabled = false;
	}
	
	public void PlayerRemoved(Node child) {
		if (players.GetChildren().Count == 1) {
			GetNode<Button>("GlobalLayout/HBoxContainer/StartButton").Disabled = true;
		}
	}
	
	public void StartGame() {
		Globals.Instance.PlayerCount = playerList.Count;
		foreach (string player in playerList) {
			Globals.Instance.PlayerTeams.Add(player, "Default");
		}
		GetTree().ChangeSceneToPacked(karaoke);
	}
	
	public void ChooseTeams() {
		Globals.Instance.PlayerCount = playerList.Count;
		foreach (string player in playerList) {
			Globals.Instance.PlayerTeams.Add(player, "Default");
		}
		
		GetTree().ChangeSceneToPacked(chooseTeam);
	}
}
