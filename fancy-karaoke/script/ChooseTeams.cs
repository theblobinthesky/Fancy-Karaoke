using Godot;
using System;
using System.Collections.Generic;

public partial class ChooseTeams : Control
{
	private PopupPanel addTeamPopup = null;
	
	private VBoxContainer teams = null;
	private VBoxContainer players = null;
	
	private string currentTeam = "Default";
	
	// Called when the node enters the scene tree for the first time.
	public override void _Ready()
	{
		addTeamPopup = GetNode<PopupPanel>("TeamDialog");
		teams = GetNode<VBoxContainer>("GlobalLayout/Selection/VBoxContainer/TeamScroll/Teams");
		GetNode<Button>("GlobalLayout/Selection/VBoxContainer/TeamScroll/Teams/Default").Pressed += () => {
			SelectTeam("Default");
		};
		((Button) addTeamPopup.FindChild("Confirm")).Pressed += AddTeam;
		GetNode<Button>("GlobalLayout/Selection/VBoxContainer/HBoxContainer/AddTeam").Pressed += RequestNewTeam;
		GetNode<Button>("GlobalLayout/HBoxContainer/StartButton").Pressed += StartGame;
		
		LoadPlayers();
	}
	
	public void LoadPlayers() {
		players = GetNode<VBoxContainer>("GlobalLayout/Selection/PlayerScroll/Players");
		foreach ( KeyValuePair<string, string> player in Globals.Instance.PlayerTeams) {
			Button button = new Button();
			button.Text = player.Key;
			StyleBoxFlat boxColor = new StyleBoxFlat();
			boxColor.BgColor = Globals.Instance.TeamColors[player.Value];
			button.AddThemeStyleboxOverride("normal", boxColor);
			button.AddThemeColorOverride("font_color", Globals.Instance.TeamColors[player.Value].Inverted());
			button.AddThemeFontSizeOverride("font_size", 64);
			button.Pressed += () => {
				AddPlayerToTeam(player.Key, button, currentTeam);
			};
			
			players.AddChild(button);
		}
	}

	// Called every frame. 'delta' is the elapsed time since the previous frame.
	public override void _Process(double delta)
	{
	}
	
	public void RequestNewTeam() {
		((LineEdit) addTeamPopup.FindChild("TeamName")).Text = "";
		((ColorPickerButton) addTeamPopup.FindChild("TeamColor")).Color = new Color(1, 1, 1, 1);
		addTeamPopup.Visible = true;
	}
	
	public void AddTeam() {
		string name = ((LineEdit) addTeamPopup.FindChild("TeamName")).Text;
		Color color = ((ColorPickerButton) addTeamPopup.FindChild("TeamColor")).Color;
		
		if (!Globals.Instance.TeamColors.ContainsKey(name)) {
			Globals.Instance.TeamColors.Add(name, color);
			
			Button button = new Button();
			button.Text = name;
			StyleBoxFlat boxColor = new StyleBoxFlat();
			boxColor.BgColor = color;
			button.AddThemeStyleboxOverride("normal", boxColor);
			button.AddThemeColorOverride("font_color", color.Inverted());
			button.AddThemeFontSizeOverride("font_size", 64);
			button.Pressed += () => {
				SelectTeam(name);
			};
			
			teams.AddChild(button);
			
			addTeamPopup.Visible = false;
		}
	}
	
	public void SelectTeam(string name) {
		currentTeam = name;
		GetNode<ColorRect>("GlobalLayout/Selection/VBoxContainer/HBoxContainer/TeamColor").Color = Globals.Instance.TeamColors[name];
	}
	
	public void AddPlayerToTeam(string player, Button playerButton, string team) {
		Globals.Instance.PlayerTeams[player] = team;
		
		StyleBoxFlat boxColor = new StyleBoxFlat();
		boxColor.BgColor = Globals.Instance.TeamColors[team];
		playerButton.AddThemeStyleboxOverride("normal", boxColor);
		playerButton.AddThemeColorOverride("font_color", Globals.Instance.TeamColors[team].Inverted());
	}
	
	public void StartGame() {
		GetTree().ChangeSceneToPacked(GD.Load<PackedScene>("res://scenes/multiplayer_karaoke.tscn"));
	}
	
}
