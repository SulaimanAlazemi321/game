extends CharacterBody2D

@export var speed: float = 150.0
@export var attack_damage: int = 10
@export var detection_radius: float = 250.0 # Increased for better detection
@export var attack_radius: float = 40.0    # Slightly increased for better attack engagement
@export var attack_cooldown_duration: float = 1.0
@export var max_health: int = 50
@export var damage_number_color: Color = Color(1.0, 0.2, 0.2)

# Time enemy will stay in 'chase' after losing sight before investigating
@export var chase_memory_duration: float = 2.0 
# Time enemy will stay in 'investigate' before returning to patrol
@export var investigate_duration: float = 5.0 

enum AIState { IDLE, PATROL, CHASE, ATTACK, INVESTIGATE, FLANK }
var current_ai_state: AIState = AIState.IDLE

var health: int
var player: CharacterBody2D = null # Assuming player is also a CharacterBodyD
var current_sprite_direction: String = "front" # For animations
var can_attack: bool = true
var attack_cooldown_timer: float = 0.0
var is_attacking: bool = false # To prevent movement/state change during attack animation
var player_detected: bool = false # Tracks if player is currently in detection_area

var animated_sprite: AnimatedSprite2D
var navigation_agent: NavigationAgent2D
var detection_area: Area2D
var health_bar_node: ProgressBar # Renamed for clarity
var health_label_node: Label    # Renamed for clarity

# Pathfinding & Obstacle Avoidance
var last_seen_player_position: Vector2 = Vector2.ZERO
var patrol_points: Array[Vector2] = []
var current_patrol_point_index: int = 0
var navigation_update_timer: float = 0.0
const NAVIGATION_UPDATE_INTERVAL: float = 0.25 # How often to update navigation path

# Timers for state transitions
var chase_memory_timer: float = 0.0
var investigate_timer: float = 0.0

# AI improvements
var stuck_timer = 0.0
var stuck_threshold = 0.8  # Time to consider the enemy stuck
var previous_position = Vector2.ZERO
var stuck_check_timer = 0.0
var stuck_check_interval = 0.2
var alternate_direction = Vector2.ZERO
var is_using_alternate_path = false
var alternate_path_timer = 0.0
var path_change_cooldown = 2.0 # Increased from 1.5
var obstacle_avoidance_rays = []
var ray_length = 30.0
var ray_count = 8

# Strategic behavior enhancements
var ai_state = "idle"  # idle, chase, flank, patrol, attack, investigate
var current_patrol_point = 0
var flank_position = Vector2.ZERO
var flank_cooldown = 0.0
var flank_interval = 5.0  # Time between flanking attempts
var last_seen_player_pos = Vector2.ZERO
var memory_timer = 0.0
var memory_duration = 3.0  # Enemy remembers player position for this long
var other_enemies = []
var has_line_of_sight = false

# --- Initialization ---
func _ready() -> void:
	health = max_health
	add_to_group("enemy")

	# Get required child nodes
	animated_sprite = get_node_or_null("AnimatedSprite2D")
	navigation_agent = get_node_or_null("NavigationAgent2D")
	detection_area = get_node_or_null("enemry-range") # Keep existing name for detection area

	if not animated_sprite:
		print_debug("Enemy: AnimatedSprite2D node not found!")
	if not navigation_agent:
		print_debug("Enemy: NavigationAgent2D node not found! AI movement will be impaired.")
	else:
		# Set navigation agent properties based on exports or defaults
		navigation_agent.path_desired_distance = 10.0 # Stop a bit before reaching exact point
		navigation_agent.target_desired_distance = 5.0 # Stop a bit before the final target
		navigation_agent.radius = 12.0 # Should be slightly larger than collision shape radius
		navigation_agent.neighbor_distance = detection_radius * 0.5
		navigation_agent.max_neighbors = 5
		navigation_agent.max_speed = speed 
		navigation_agent.avoidance_enabled = true
		# Connect signal for when navigation is complete (or target reached)
		navigation_agent.target_reached.connect(_on_navigation_agent_target_reached)
		#navigation_agent.path_changed.connect(_on_navigation_agent_path_changed) # Optional


	if detection_area:
		# Disconnect any existing connections to avoid duplicates
		if detection_area.is_connected("body_entered", _on_detection_area_body_entered):
			detection_area.body_entered.disconnect(_on_detection_area_body_entered)
		if detection_area.is_connected("body_exited", _on_detection_area_body_exited):
			detection_area.body_exited.disconnect(_on_detection_area_body_exited)
			
		# Set up fresh connections
		detection_area.body_entered.connect(_on_detection_area_body_entered)
		detection_area.body_exited.connect(_on_detection_area_body_exited)
		
		# Adjust detection area radius based on export
		var detection_shape = detection_area.get_node_or_null("enemry-range") as CollisionShape2D
		if detection_shape and detection_shape.shape is CircleShape2D:
			(detection_shape.shape as CircleShape2D).radius = detection_radius
		print_debug("Enemy: Connected detection area signals")
	else:
		print_debug("Enemy: Detection Area2D ('enemry-range') not found!")

	create_health_display() # Keep existing health display logic
	generate_initial_patrol_points(global_position, 100.0, 4)

	# Initial animation
	if animated_sprite:
		animated_sprite.play("idle-" + current_sprite_direction)
		animated_sprite.speed_scale = 1.2

	# Attempt to find player immediately
	var players = get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		player = players[0] as CharacterBody2D
		#print_debug("Enemy found player (", player.name, ") on ready.")
	#else:
		#print_debug("Enemy did not find player on ready.")

	set_ai_state(AIState.PATROL) # Start by patrolling


# --- AI State Management ---
func set_ai_state(new_state: AIState) -> void:
	if current_ai_state == new_state and new_state != AIState.PATROL: # Allow re-entering patrol to pick new point
		return

	#print_debug("Enemy changing state from ", AIState.keys()[current_ai_state], " to ", AIState.keys()[new_state])
	current_ai_state = new_state
	
	# Reset timers or specific logic when entering a new state
	match current_ai_state:
		AIState.IDLE:
			velocity = Vector2.ZERO
			if navigation_agent and navigation_agent.is_navigation_finished() == false:
				navigation_agent.set_target_position(global_position) # Stop moving
			play_animation("idle")
		AIState.PATROL:
			investigate_timer = 0.0 # Reset investigate timer
			chase_memory_timer = 0.0 # Reset chase memory
			move_to_next_patrol_point()
		AIState.CHASE:
			investigate_timer = 0.0 # Reset investigate timer
			chase_memory_timer = chase_memory_duration # Start chase memory
			# Target will be set in _physics_process
		AIState.ATTACK:
			velocity = Vector2.ZERO # Stop moving to attack
			if navigation_agent and navigation_agent.is_navigation_finished() == false:
				navigation_agent.set_target_position(global_position)
			# Attack animation will be handled in perform_attack
		AIState.INVESTIGATE:
			chase_memory_timer = 0.0 # Player fully lost for now
			investigate_timer = investigate_duration # Start investigate timer
			if navigation_agent:
				navigation_agent.set_target_position(last_seen_player_position)
			play_animation("idle") # Or a specific "investigate" animation

# --- Physics & AI Processing ---
func _physics_process(delta: float) -> void:
	if not is_instance_valid(player): 
		if current_ai_state != AIState.PATROL:
			set_ai_state(AIState.PATROL)
		# Try to find player again
		var players = get_tree().get_nodes_in_group("player")
		if players.size() > 0:
			player = players[0] as CharacterBody2D

	if not can_attack:
		attack_cooldown_timer -= delta
		if attack_cooldown_timer <= 0:
			can_attack = true

	if is_attacking:
		return 

	if current_ai_state == AIState.CHASE:
		chase_memory_timer -= delta
		if chase_memory_timer <= 0:
			set_ai_state(AIState.INVESTIGATE)
	elif current_ai_state == AIState.INVESTIGATE:
		investigate_timer -= delta
		if investigate_timer <= 0:
			set_ai_state(AIState.PATROL)

	var distance_to_player: float = INF # Initialize with infinity
	var direction_to_player: Vector2 = Vector2.ZERO
	var player_is_valid_and_alive = false

	if is_instance_valid(player):
		distance_to_player = global_position.distance_to(player.global_position)
		direction_to_player = global_position.direction_to(player.global_position)
		var player_is_dead = false
		if player.has_method("get_is_dead"): 
			player_is_dead = player.get_is_dead()
		elif "is_dead" in player: 
			player_is_dead = player.is_dead
		player_is_valid_and_alive = not player_is_dead
		
		# Direct follow logic without navigation agent
		if player_detected and player_is_valid_and_alive:
			# Always update last known position when player is visible
			last_seen_player_position = player.global_position
			
			# If within attack range and can attack, attack
			if distance_to_player <= attack_radius and can_attack:
				set_ai_state(AIState.ATTACK)
			# Otherwise if player detected but outside attack range, chase
			elif current_ai_state != AIState.CHASE:
				set_ai_state(AIState.CHASE)

	if not player_is_valid_and_alive and current_ai_state != AIState.PATROL and current_ai_state != AIState.IDLE:
		set_ai_state(AIState.PATROL)

	navigation_update_timer -= delta

	match current_ai_state:
		AIState.PATROL:
			# Direct patrol movement without NavigationAgent
			if global_position.distance_to(patrol_points[current_patrol_point_index]) < 20.0:
				move_to_next_patrol_point()
			else:
				var direction_to_patrol = global_position.direction_to(patrol_points[current_patrol_point_index])
				velocity = direction_to_patrol * (speed * 0.7) # Slower patrol speed
				update_sprite_direction(velocity)
				play_animation("idle") # Use walk animation if available
				move_and_slide()
				
			if player_detected and player_is_valid_and_alive:
				set_ai_state(AIState.CHASE)

		AIState.CHASE:
			if not player_detected and chase_memory_timer <=0: 
				set_ai_state(AIState.INVESTIGATE)
			elif player_detected and player_is_valid_and_alive: 
				# This part is critical - we need to move toward the player when chasing
				if distance_to_player <= attack_radius and can_attack:
					set_ai_state(AIState.ATTACK)
				else:
					# Direct movement toward player when NavigationAgent is not available
					velocity = direction_to_player * speed
					update_sprite_direction(velocity)
					play_animation("idle") # We'll use idle as fallback if walk/run isn't available
					move_and_slide()
			elif not player_detected and chase_memory_timer > 0: # Lost sight but still remembering
				# Move toward last seen position
				var direction_to_last_seen = global_position.direction_to(last_seen_player_position)
				if global_position.distance_to(last_seen_player_position) > 10.0:
					velocity = direction_to_last_seen * speed
					update_sprite_direction(velocity)
					play_animation("idle") # We'll use idle as fallback if walk/run isn't available
					move_and_slide()

		AIState.ATTACK:
			if not player_is_valid_and_alive:
				set_ai_state(AIState.PATROL)
			elif distance_to_player > attack_radius * 1.1 or not player_detected : # Player moved out of effective range
				is_attacking = false # Ensure we can transition out if attack animation was interrupted
				set_ai_state(AIState.CHASE) 
			elif can_attack and not is_attacking:
				perform_attack(direction_to_player)

		AIState.INVESTIGATE:
			if player_detected and player_is_valid_and_alive: 
				set_ai_state(AIState.CHASE)
			elif global_position.distance_to(last_seen_player_position) > 10.0:
				# Move toward last seen position
				var direction_to_investigate = global_position.direction_to(last_seen_player_position)
				velocity = direction_to_investigate * speed
				update_sprite_direction(velocity)
				play_animation("idle") # Use your run animation if available
				move_and_slide()
			elif investigate_timer <= 0: 
				set_ai_state(AIState.PATROL)
	
	# Remove NavigationAgent specific movement code
	if is_attacking:
		velocity = Vector2.ZERO
		move_and_slide()

# --- Navigation Callbacks ---
func _on_navigation_agent_target_reached() -> void:
	# This function can be kept for compatibility but simplified
	if current_ai_state == AIState.PATROL:
		await get_tree().create_timer(randf_range(0.5, 1.5)).timeout
		if current_ai_state == AIState.PATROL: 
			move_to_next_patrol_point()

# func _on_navigation_agent_path_changed() -> void:
# 	pass

# --- Patrol Logic ---
func generate_initial_patrol_points(center: Vector2, radius: float, num_points: int) -> void:
	patrol_points.clear()
	if num_points <= 0: return
	for i in range(num_points):
		var angle: float = (2 * PI / num_points) * i
		var point: Vector2 = center + Vector2(cos(angle), sin(angle)) * radius
		patrol_points.append(point)
	current_patrol_point_index = 0 # Start from the first point

func move_to_next_patrol_point() -> void:
	if patrol_points.is_empty():
		# Generate new patrol points if none exist
		generate_initial_patrol_points(global_position, 100.0, 4)
		if patrol_points.is_empty():
			set_ai_state(AIState.IDLE) 
			return

	# Ensure player reference is attempted if null, or default to patrol
	if not is_instance_valid(player):
		var players = get_tree().get_nodes_in_group("player")
		if players.size() > 0:
			player = players[0] as CharacterBody2D
		# If still no player, enemy will just patrol its points without further player checks until detected.

	current_patrol_point_index = (current_patrol_point_index + 1) % patrol_points.size()
	
	# Wait at patrol point for a short time
	velocity = Vector2.ZERO
	play_animation("idle")

# --- Attack Logic ---
func perform_attack(direction_to_player: Vector2) -> void:
	if not can_attack or is_attacking:
		return

	is_attacking = true
	can_attack = false # Start cooldown
	attack_cooldown_timer = attack_cooldown_duration
	
	# Stop movement for attack
	velocity = Vector2.ZERO
	if navigation_agent:
		navigation_agent.set_target_position(global_position) # Explicitly stop nav agent

	update_sprite_direction(direction_to_player) # Face the player
	play_animation("attack") # Play attack animation for current_sprite_direction

	# Damage dealing tied to animation frame or timer
	# Create a one-shot timer for damage application mid-animation
	var damage_timer = Timer.new()
	damage_timer.wait_time = 0.3 # Adjust this to match your attack animation's impact frame
	damage_timer.one_shot = true
	damage_timer.timeout.connect(func():
		if is_instance_valid(player) and is_attacking: # Still attacking and player exists
			var distance_to_player_on_damage = global_position.distance_to(player.global_position)
			if distance_to_player_on_damage <= attack_radius * 1.15: # Generous check
				if player.has_method("take_damage"):
					player.take_damage(attack_damage)
		# Ensure timer is freed
		if is_instance_valid(damage_timer):
			damage_timer.queue_free()
		elif damage_timer != null : # Check if it was added to tree but became invalid
			print_debug("Damage timer was invalid before queue_free could be called")
	)
	add_child(damage_timer) # Add timer to scene tree to make it run
	damage_timer.start()

	var attack_animation_duration = get_animation_duration("attack")
	
	# Create another timer for resetting is_attacking after animation
	var anim_finish_timer = Timer.new()
	anim_finish_timer.wait_time = attack_animation_duration
	anim_finish_timer.one_shot = true

	var on_anim_finish_timeout_callable = func():
		is_attacking = false
		# Cooldown is already running, state will be re-evaluated in physics_process
		if is_instance_valid(anim_finish_timer):
			anim_finish_timer.queue_free()
		elif anim_finish_timer != null:
			print_debug("Anim finish timer was invalid before queue_free could be called (check if already freed)")

	anim_finish_timer.timeout.connect(on_anim_finish_timeout_callable)
	add_child(anim_finish_timer)
	anim_finish_timer.start()

# --- Player Detection ---
func _on_detection_area_body_entered(body: Node) -> void:
	if body.is_in_group("player"):
		print_debug("Enemy detected player entering range!")
		# Ensure we don't re-assign if it's already the current player and valid
		if not is_instance_valid(player) or player != body:
			player = body as CharacterBody2D 
		player_detected = true
		
		var player_is_dead = false
		if is_instance_valid(player):
			if player.has_method("get_is_dead"): 
				player_is_dead = player.get_is_dead()
			elif "is_dead" in player: 
				player_is_dead = player.is_dead

		if not player_is_dead and (current_ai_state == AIState.PATROL or current_ai_state == AIState.IDLE or current_ai_state == AIState.INVESTIGATE):
			set_ai_state(AIState.CHASE)
			print_debug("Enemy changing to CHASE state due to player detection")

func _on_detection_area_body_exited(body: Node) -> void:
	if body == player:
		print_debug("Enemy lost player from detection range!")
		player_detected = false
		# Start chase memory timer - we'll keep chasing for a bit after losing sight
		chase_memory_timer = chase_memory_duration
		# Don't change state immediately; let chase_memory_timer handle it in _physics_process
		#print_debug("Enemy lost direct sight of player.")

# --- Animation & Direction ---
func update_sprite_direction(move_direction: Vector2) -> void:
	if move_direction.length_squared() < 0.01: # Check if direction is not negligible
		return # Don't change direction if not moving significantly

	var new_direction_str: String = current_sprite_direction
	# Prioritize horizontal aiming if significant, otherwise vertical
	if abs(move_direction.x) > abs(move_direction.y) * 0.8: # More sensitive to horizontal
		new_direction_str = "right" if move_direction.x > 0 else "left"
	else:
		new_direction_str = "front" if move_direction.y > 0 else "back"
	
	if new_direction_str != current_sprite_direction:
		current_sprite_direction = new_direction_str
		# Animation will be updated by play_animation call

func play_animation(animation_name_base: String) -> void:
	if not animated_sprite or not animated_sprite.sprite_frames:
		return

	# Check if we're moving and should play walk/run animation instead
	if animation_name_base == "idle" and velocity.length_squared() > 900.0: # If moving faster than ~30 units/sec
		animation_name_base = "idle" # We'll still use idle since that's what we have
		# If you have a walk/run animation, use it here with: animation_name_base = "walk" or "run"
	
	var animation_to_play: String = animation_name_base + "-" + current_sprite_direction
	
	# Hurt and Death animations often have specific directional versions
	if animation_name_base == "hurt" and not animated_sprite.sprite_frames.has_animation(animation_to_play):
		if animated_sprite.sprite_frames.has_animation("hurt"): # Generic hurt
			animation_to_play = "hurt"
	
	elif animation_name_base == "death" and not animated_sprite.sprite_frames.has_animation(animation_to_play):
		if animated_sprite.sprite_frames.has_animation("death"): # Generic death
			animation_to_play = "death"

	if animated_sprite.sprite_frames.has_animation(animation_to_play):
		if animated_sprite.animation != animation_to_play or not animated_sprite.is_playing():
			animated_sprite.play(animation_to_play)
	#else:
		#print_debug("Enemy: Animation not found - ", animation_to_play)

func get_animation_duration(anim_name_base: String) -> float:
	if not animated_sprite or not animated_sprite.sprite_frames:
		return 0.5 # Default if no animated sprite or sprite frames
		
	var anim_name = anim_name_base + "-" + current_sprite_direction
	var speed_scale = animated_sprite.speed_scale if animated_sprite.speed_scale > 0 else 1.0
	
	# Try with direction suffix first
	if animated_sprite.sprite_frames.has_animation(anim_name):
		var frame_count = animated_sprite.sprite_frames.get_frame_count(anim_name)
		var fps = animated_sprite.sprite_frames.get_animation_speed(anim_name)
		if fps <= 0:
			fps = 1.0 # Avoid division by zero
		return (frame_count / fps) * (1.0 / speed_scale)
	
	# Try base animation name without direction
	if animated_sprite.sprite_frames.has_animation(anim_name_base):
		var frame_count = animated_sprite.sprite_frames.get_frame_count(anim_name_base)
		var fps = animated_sprite.sprite_frames.get_animation_speed(anim_name_base)
		if fps <= 0:
			fps = 1.0 # Avoid division by zero
		return (frame_count / fps) * (1.0 / speed_scale)
		
	return 0.5 # Default if animation not found

# --- Health & Damage (Keeping existing logic mostly) ---
func create_health_display():
	var health_display_container = Control.new() 
	health_display_container.name = "HealthDisplay"
	health_display_container.position = Vector2(-20, -40) 
	
	health_bar_node = ProgressBar.new()
	health_bar_node.name = "Bar"
	health_bar_node.max_value = max_health
	health_bar_node.value = health
	health_bar_node.show_percentage = false
	health_bar_node.custom_minimum_size = Vector2(40, 6) 
	health_bar_node.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	
	var fg_style = StyleBoxFlat.new()
	fg_style.bg_color = Color(0.8, 0.2, 0.2)
	fg_style.corner_radius_top_left = 2
	fg_style.corner_radius_top_right = 2
	fg_style.corner_radius_bottom_left = 2
	fg_style.corner_radius_bottom_right = 2
	health_bar_node.add_theme_stylebox_override("fill", fg_style)
	
	var bg_style = StyleBoxFlat.new()
	bg_style.bg_color = Color(0.2, 0.2, 0.2, 0.8)
	bg_style.corner_radius_top_left = 2
	bg_style.corner_radius_top_right = 2
	bg_style.corner_radius_bottom_left = 2
	bg_style.corner_radius_bottom_right = 2
	health_bar_node.add_theme_stylebox_override("background", bg_style)
	
	health_label_node = Label.new()
	health_label_node.name = "HealthLabel"
	# Use LabelSettings for better text control
	var label_settings = LabelSettings.new()
	label_settings.font_size = 10
	label_settings.font_color = Color.WHITE
	label_settings.outline_size = 2
	label_settings.outline_color = Color.BLACK
	health_label_node.label_settings = label_settings
	health_label_node.text = "%d/%d" % [health, max_health]
	health_label_node.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	health_label_node.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	# Position label above the bar by anchoring or manual offset if needed
	health_label_node.position = Vector2(0, -12) # Adjust as needed relative to health_display_container

	health_display_container.add_child(health_bar_node)
	health_display_container.add_child(health_label_node)
	add_child(health_display_container)

func update_health_display():
	if health_bar_node:
		health_bar_node.value = health
	if health_label_node:
		health_label_node.text = "%d/%d" % [health, max_health]

func show_damage_number(amount: int):
	var damage_label = Label.new()
	
	var lbl_settings = LabelSettings.new() # Use local var for clarity
	lbl_settings.font_color = damage_number_color
	lbl_settings.font_size = 18 
	lbl_settings.outline_size = 3 
	lbl_settings.outline_color = Color(0,0,0,0.8)
	damage_label.label_settings = lbl_settings
	damage_label.text = str(amount)
	
	# Add to a general UI layer if you have one, or get_parent() for local space
	# For damage numbers, usually better to add to a canvas layer or the main scene tree
	var main_scene = get_tree().current_scene
	if main_scene:
		main_scene.add_child(damage_label)
		# Position globally then adjust for camera if needed, or position relative to enemy
		damage_label.global_position = global_position + Vector2(randf_range(-10, 10), -35)
	else: # Fallback if no main scene (e.g. testing enemy scene directly)
		add_child(damage_label)
		damage_label.position = Vector2(randf_range(-10, 10), -35)

	var tween = create_tween()
	tween.set_parallel(true)
	# Adjust tween properties for better visual appeal
	tween.tween_property(damage_label, "global_position:y", damage_label.global_position.y - 40, 0.7).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tween.tween_property(damage_label, "modulate:a", 0.0, 0.7).set_delay(0.1).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	tween.chain().tween_callback(damage_label.queue_free)

func take_damage(damage: int):
	if health <= 0: # Already dead
		return

	health -= damage
	update_health_display()
	show_damage_number(damage)
	
	if animated_sprite: 
		animated_sprite.modulate = Color(1, 0.5, 0.5)
		await get_tree().create_timer(0.1).timeout
		if is_instance_valid(animated_sprite): 
			animated_sprite.modulate = Color(1, 1, 1)
	
	if health <= 0:
		die()
	else:
		# Brief stun or interruption logic
		if not is_attacking: # Don't interrupt attack animation for hurt if already mid-swing
			var prev_state = current_ai_state
			# Temporarily set to IDLE or a specific HURT state if you have one
			# This can prevent immediate re-engagement while hurt animation plays.
			# For now, just play hurt animation. Player can create a proper hurt state.
			play_animation("hurt")
			# Short pause for hurt animation to be visible
			if get_animation_duration("hurt") > 0.1: # Only await if hurt anim exists
				await get_tree().create_timer(get_animation_duration("hurt") * 0.8).timeout
			
			# After hurt, decide next state. If player still around, likely CHASE.
			if is_instance_valid(player) and player_detected and current_ai_state != AIState.ATTACK:
				# Check if player is dead before chasing again
				var player_is_dead = false
				if player.has_method("get_is_dead"): player_is_dead = player.get_is_dead()
				elif "is_dead" in player: player_is_dead = player.is_dead
				if not player_is_dead:
					set_ai_state(AIState.CHASE)
				else:
					set_ai_state(AIState.PATROL)
			elif current_ai_state != AIState.ATTACK: # If not attacking and lost player, patrol
				set_ai_state(AIState.PATROL)

func die():
	if current_ai_state == AIState.IDLE and health <=0: # Already processed death
		return
		
	set_ai_state(AIState.IDLE) # Set to IDLE to stop other behaviors
	health = 0 # Ensure health is 0
	set_process(false) 
	set_physics_process(false)
	remove_from_group("enemy")
	
	var coll_shape = get_node_or_null("CollisionShape2D") as CollisionShape2D
	if coll_shape:
		coll_shape.set_deferred("disabled", true)

	# Hide health display immediately
	var health_display_container = get_node_or_null("HealthDisplay")
	if health_display_container:
		health_display_container.visible = false

	play_animation("death") 
	
	var death_animation_duration = get_animation_duration("death")
		
	await get_tree().create_timer(death_animation_duration).timeout
	queue_free()
