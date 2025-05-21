extends ProgressBar

# Reference to the player
var player
# Reference to the HP values label
var hp_values_label

func _ready():
	# Hide the progress bar's default styling
	self.show_percentage = false
	
	# Get reference to the HP values label (now a child of this node)
	hp_values_label = get_node_or_null("HPValues")
	
	# Find the player through the player group instead of direct parent reference
	var players = get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		player = players[0]
		
		# Connect to the player's health_changed signal
		if player.has_signal("health_changed"):
			player.health_changed.connect(_on_player_health_changed)
			
			# Initialize health bar with player's current health
			value = player.health
			max_value = player.max_health
			
			# Update the HP values label
			if hp_values_label:
				hp_values_label.text = str(int(player.health)) + "/" + str(int(player.max_health))
		else:
			push_error("Player doesn't have health_changed signal!")
	else:
		push_error("Could not find player for health updates!")

# Update the health bar when player health changes
func _on_player_health_changed(new_health, max_health):
	max_value = max_health
	
	# Animate the health bar
	create_tween().tween_property(self, "value", new_health, 0.3).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_SINE)
	
	# Update the HP values label
	if hp_values_label:
		hp_values_label.text = str(int(new_health)) + "/" + str(int(max_health)) 