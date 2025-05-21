extends ProgressBar

# Path to the player node
@export var player_path: NodePath

# Reference to the player
var player
# Reference to the HP values label
var hp_values_label

func _ready():
	# Hide the progress bar's default styling
	self.show_percentage = false
	
	# Get reference to the HP values label (now a child of this node)
	hp_values_label = get_node_or_null("HPValues")
	
	# Connect to the player
	if player_path:
		player = get_node(player_path)
		# Connect to the player's health_changed signal
		player.health_changed.connect(_on_player_health_changed)
		
		# Initialize health bar with player's current health
		value = player.health
		max_value = player.max_health
		
		# Update the HP values label
		if hp_values_label:
			hp_values_label.text = str(int(player.health)) + "/" + str(int(player.max_health))
	else:
		push_error("Player path not set for HealthBar!")

# Update the health bar when player health changes
func _on_player_health_changed(new_health, max_health):
	max_value = max_health
	
	# Animate the health bar
	create_tween().tween_property(self, "value", new_health, 0.3).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_SINE)
	
	# Update the HP values label
	if hp_values_label:
		hp_values_label.text = str(int(new_health)) + "/" + str(int(max_health)) 
