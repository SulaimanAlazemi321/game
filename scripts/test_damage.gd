extends Node

# This script can be attached to any node to test the player's health system
# with keyboard shortcuts

# Reference to the player
@export var player_path: NodePath
var player

func _ready():
	if player_path:
		player = get_node(player_path)
	else:
		# Try to find the player automatically
		player = get_tree().get_nodes_in_group("player")[0] if get_tree().get_nodes_in_group("player").size() > 0 else null
		
		if player == null:
			# Last resort: try a common player name
			player = get_node_or_null("/root/Main/charctar20") 
			
	if player == null:
		push_error("Could not find player for test_damage script")

func _process(delta):
	# Press T to take 10 damage
	if Input.is_action_just_pressed("ui_focus_next"):  # Tab key
		if player:
			player.take_damage(10)
			print("Player took 10 damage. Health: ", player.health)
	
	# Press H to heal 5 health
	if Input.is_action_just_pressed("ui_home"):  # Home key
		if player:
			player.heal(5)
			print("Player healed 5 health. Health: ", player.health)
	
	# Press Q to reduce health by 10%
	if Input.is_action_just_pressed("ui_text_completion_replace"):  # Q key
		if player:
			var damage_amount = player.max_health * 0.1  # 10% of max health
			player.take_damage(damage_amount)
			print("Player lost 10% health. Current health: ", player.health)
			
	# Test directional hurt animations directly
	# Number keys 1-4 for different direction hurt animations
	if Input.is_action_just_pressed("key_1") and player:  # 1 key
		player.current_direction = "front"
		player.play_hurt_animation()
		print("Playing front hurt animation")
		
	if Input.is_action_just_pressed("key_2") and player:  # 2 key
		player.current_direction = "back"
		player.play_hurt_animation()
		print("Playing back hurt animation")
		
	if Input.is_action_just_pressed("key_3") and player:  # 3 key
		player.current_direction = "left"
		player.play_hurt_animation()
		print("Playing left hurt animation")
		
	if Input.is_action_just_pressed("key_4") and player:  # 4 key
		player.current_direction = "right"
		player.play_hurt_animation()
		print("Playing right hurt animation") 
