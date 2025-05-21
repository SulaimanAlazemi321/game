extends CharacterBody2D

@export var speed = 200.0
@export var sprint_speed = 300.0  # Sprint speed when Shift is held
@export var max_health = 100
@export var attack_damage = 20
@export var attack_range = 50.0
@export var damage_number_color = Color(1.0, 0.4, 0.1)  # Orange for player damage

var health = max_health
var current_direction = "front"  # Track the current direction
var is_hurt = false  # Track if player is in hurt state
var hurt_timer = 0.0  # Timer for hurt animation
var is_attacking = false  # Track if player is in attack state
var attack_cooldown = 0.0  # Attack cooldown timer
var can_attack = true  # Can player attack
var is_dead = false  # Track if player is dead

signal health_changed(new_health, max_health)

func _physics_process(delta):
	# Skip all processing if dead
	if is_dead:
		return
		
	# Update attack cooldown
	if attack_cooldown > 0:
		attack_cooldown -= delta
		if attack_cooldown <= 0:
			can_attack = true
	
	# Handle hurt state timer
	if is_hurt:
		hurt_timer -= delta
		if hurt_timer <= 0:
			is_hurt = false
		else:
			# Skip movement processing if player is hurt
			return
	
	# Handle attack input
	if Input.is_action_just_pressed("e_key") and can_attack and not is_attacking:
		attack()
		return
	
	# Skip movement if attacking
	if is_attacking:
		return
	
	# Get input direction
	var direction = Vector2.ZERO
	if Input.is_action_pressed("ui_up") or Input.is_action_pressed("w_key"):
		direction.y -= 1
	if Input.is_action_pressed("ui_down") or Input.is_action_pressed("s_key"):
		direction.y += 1
	if Input.is_action_pressed("ui_left") or Input.is_action_pressed("a_key"):
		direction.x -= 1
	if Input.is_action_pressed("ui_right") or Input.is_action_pressed("d_key"):
		direction.x += 1
	
	# Normalize the direction vector and apply movement
	if direction != Vector2.ZERO:
		direction = direction.normalized()
		
		# Update current direction
		update_direction(direction)
		
		# Check if sprinting (Shift key is pressed)
		var is_sprinting = Input.is_action_pressed("shift_key")
		var current_speed = sprint_speed if is_sprinting else speed
		
		# Play animation if it exists
		if has_node("AnimatedSprite2D"):
			var sprite = $AnimatedSprite2D
			var animations = sprite.sprite_frames.get_animation_names()
			
			# Check if directional animations exist
			if animations.has("back") and animations.has("front") and animations.has("left") and animations.has("right"):
				# Use directional animations
				play_animation(current_direction)
				
				# Adjust animation speed based on sprinting
				sprite.speed_scale = 1.5 if is_sprinting else 1.0
			else:
				# Fallback to default animation
				sprite.play("default")
		
		# Apply velocity with appropriate speed
		velocity = direction * current_speed
	else:
		# Play idle animation if not moving
		play_idle_animation()
		velocity = Vector2.ZERO
	
	move_and_slide()

func update_direction(direction):
	# Determine which direction the player should face based on input direction
	if abs(direction.x) > abs(direction.y):
		# Horizontal movement is dominant
		if direction.x > 0:
			current_direction = "right"
		else:
			current_direction = "left"
	else:
		# Vertical movement is dominant
		if direction.y > 0:
			current_direction = "front"
		else:
			current_direction = "back"

func play_animation(anim_direction):
	if has_node("AnimatedSprite2D") and not is_attacking and not is_hurt:
		$AnimatedSprite2D.play(anim_direction)

func play_idle_animation():
	if has_node("AnimatedSprite2D") and not is_attacking and not is_hurt:
		var idle_anim = "idle-" + current_direction
		if $AnimatedSprite2D.sprite_frames.has_animation(idle_anim):
			$AnimatedSprite2D.play(idle_anim)
		else:
			$AnimatedSprite2D.stop()

func attack():
	# Set attack state
	is_attacking = true
	can_attack = false
	attack_cooldown = 0.6  # Cooldown between attacks
	
	# Play attack animation based on current direction
	var attack_anim = "attack-" + current_direction
	print("Playing attack animation: ", attack_anim)
	
	if has_node("AnimatedSprite2D") and $AnimatedSprite2D.sprite_frames.has_animation(attack_anim):
		$AnimatedSprite2D.play(attack_anim)
		
		# Attack nearby enemies after a short delay (halfway through animation)
		await get_tree().create_timer(0.2).timeout
		hit_enemies()
		
		# Wait for animation to finish
		var attack_duration = 0.4
		await get_tree().create_timer(attack_duration).timeout
		
		# Reset attack state
		is_attacking = false
		play_idle_animation()
	else:
		print("Missing attack animation: ", attack_anim)
		is_attacking = false

func hit_enemies():
	# Find enemies in range
	var space_state = get_world_2d().direct_space_state
	
	# Determine attack direction vector based on current_direction
	var attack_direction = Vector2.ZERO
	if current_direction == "right":
		attack_direction = Vector2.RIGHT
	elif current_direction == "left":
		attack_direction = Vector2.LEFT
	elif current_direction == "front":
		attack_direction = Vector2.DOWN
	else:  # back
		attack_direction = Vector2.UP
	
	# Create a query for detecting enemies
	var query = PhysicsRayQueryParameters2D.new()
	query.from = global_position
	query.to = global_position + (attack_direction * attack_range)
	query.collision_mask = 2  # Assuming enemies are on layer 2, adjust if needed
	
	var result = space_state.intersect_ray(query)
	if result and result.collider.has_method("take_damage"):
		print("Hit enemy: ", result.collider.name)
		result.collider.take_damage(attack_damage)
	
	# Alternative: use Area2D detection if raycasting doesn't work well
	var nearby_bodies = get_tree().get_nodes_in_group("enemy")
	for body in nearby_bodies:
		if body.has_method("take_damage"):
			var distance = global_position.distance_to(body.global_position)
			if distance < attack_range:
				var dir_to_enemy = (body.global_position - global_position).normalized()
				# Check if enemy is in front of player (using dot product)
				if dir_to_enemy.dot(attack_direction) > 0.5:
					print("Hit enemy in range: ", body.name)
					body.take_damage(attack_damage)

func _ready():
	# Add player to the player group for detection
	add_to_group("player")
	
	# Register inputs if they don't exist yet
	register_input_keys()
	
	# Initialize health
	health = max_health
	emit_signal("health_changed", health, max_health)
	
	# Start with idle animation
	play_idle_animation()

func register_input_keys():
	# Register WASD inputs
	if not InputMap.has_action("w_key"):
		InputMap.add_action("w_key")
		var w_event = InputEventKey.new()
		w_event.keycode = KEY_W
		InputMap.action_add_event("w_key", w_event)
	
	if not InputMap.has_action("a_key"):
		InputMap.add_action("a_key")
		var a_event = InputEventKey.new()
		a_event.keycode = KEY_A
		InputMap.action_add_event("a_key", a_event)
	
	if not InputMap.has_action("s_key"):
		InputMap.add_action("s_key")
		var s_event = InputEventKey.new()
		s_event.keycode = KEY_S
		InputMap.action_add_event("s_key", s_event)
	
	if not InputMap.has_action("d_key"):
		InputMap.add_action("d_key")
		var d_event = InputEventKey.new()
		d_event.keycode = KEY_D
		InputMap.action_add_event("d_key", d_event)
	
	# Register Shift key for sprinting
	if not InputMap.has_action("shift_key"):
		InputMap.add_action("shift_key")
		var shift_event = InputEventKey.new()
		shift_event.keycode = KEY_SHIFT
		InputMap.action_add_event("shift_key", shift_event)
	
	# Register E key for attacking
	if not InputMap.has_action("e_key"):
		InputMap.add_action("e_key")
		var e_event = InputEventKey.new()
		e_event.keycode = KEY_E
		InputMap.action_add_event("e_key", e_event)

func take_damage(damage_amount):
	# Skip if dead
	if is_dead:
		return
		
	health -= damage_amount
	health = max(0, health)  # Ensure health doesn't go below 0
	emit_signal("health_changed", health, max_health)
	
	# Show damage number
	show_damage_number(damage_amount)
	
	# Flash the player to indicate damage
	modulate = Color(1, 0.5, 0.5)  # Light red tint
	await get_tree().create_timer(0.1).timeout
	modulate = Color(1, 1, 1)  # Back to normal
	
	# Play hurt animation based on current direction
	play_hurt_animation()
	
	# If health is zero or less, die but make sure we're not already dying
	if health <= 0 and !is_dead:
		# Make sure we call die after the hurt animation
		await get_tree().create_timer(0.2).timeout
		die()

func show_damage_number(amount):
	# Create a label for the damage number
	var damage_label = Label.new()
	damage_label.text = str(amount)
	damage_label.add_theme_color_override("font_color", damage_number_color)
	
	# Set font size and outline
	damage_label.add_theme_font_size_override("font_size", 16)
	damage_label.add_theme_color_override("font_outline_color", Color(0, 0, 0))
	damage_label.add_theme_constant_override("outline_size", 2)
	
	# Position it above the player with slight randomization
	damage_label.position = Vector2(randf_range(-15, 15), -40)
	
	# Add it to the player
	add_child(damage_label)
	
	# Animate the damage number floating up and fading out
	var tween = create_tween()
	tween.tween_property(damage_label, "position", Vector2(damage_label.position.x, damage_label.position.y - 30), 0.7)
	tween.parallel().tween_property(damage_label, "modulate:a", 0.0, 0.7)
	
	# Remove the label after animation
	await tween.finished
	damage_label.queue_free()

func play_hurt_animation():
	if has_node("AnimatedSprite2D"):
		var sprite = $AnimatedSprite2D
		
		# Set hurt state
		is_hurt = true
		hurt_timer = 0.4  # Hurt animation duration in seconds
		
		# Play the appropriate hurt animation based on current direction
		var hurt_anim = "hurt_" + current_direction
		if sprite.sprite_frames.has_animation(hurt_anim):
			sprite.play(hurt_anim)
		else:
			# Fallback to regular hurt animation if directional not available
			if sprite.sprite_frames.has_animation("hurt"):
				sprite.play("hurt")

func heal(amount):
	health += amount
	health = min(health, max_health)  # Ensure health doesn't exceed max
	emit_signal("health_changed", health, max_health)

func die():
	# Handle player death logic
	print("Player died!")
	
	# Skip if already dead
	if is_dead:
		return
	
	# Set dead state
	is_dead = true
	
	# Disable movement and collision
	set_physics_process(false)
	if has_node("CollisionShape2D"):
		$CollisionShape2D.disabled = true
	
	# Play death animation if it exists
	if has_node("AnimatedSprite2D"):
		# Check available animations
		var animations = $AnimatedSprite2D.sprite_frames.get_animation_names()
		print("Available player animations: ", animations)
		
		var death_anim = "death-" + current_direction
		print("Looking for player death animation: ", death_anim)
		
		if $AnimatedSprite2D.sprite_frames.has_animation(death_anim):
			print("Playing player directional death animation")
			play_death_animation(death_anim)
		elif $AnimatedSprite2D.sprite_frames.has_animation("death"):
			print("Playing generic player death animation")
			play_death_animation("death")
		else:
			print("No player death animation found")
			# No animation - just respawn after a delay
			await respawn_player()
	else:
		# No AnimatedSprite2D - just respawn after a delay
		await respawn_player()

func play_death_animation(anim_name):
	# Make sure death animation doesn't loop
	$AnimatedSprite2D.sprite_frames.set_animation_loop(anim_name, false)
	
	# Use faster animation speed for death animation (0.8 instead of 0.3)
	$AnimatedSprite2D.speed_scale = 0.8
	
	# Play the animation
	$AnimatedSprite2D.play(anim_name)
	
	# Calculate how long the animation should take based on frame count
	var frame_count = $AnimatedSprite2D.sprite_frames.get_frame_count(anim_name)
	var anim_duration = (frame_count / $AnimatedSprite2D.sprite_frames.get_animation_speed(anim_name)) * (1.0 / $AnimatedSprite2D.speed_scale)
	print("Player death animation has ", frame_count, " frames, expected duration: ", anim_duration, "s")
	
	# Wait for the full animation duration (reduced buffer for faster animation)
	await get_tree().create_timer(anim_duration + 0.2).timeout
	
	# Now we can respawn
	await respawn_player()

func respawn_player():
	print("Respawning player")
	
	# Respawn player at the center of the map
	position = Vector2(582, 362)
		
	# Reset player health
	health = max_health
	emit_signal("health_changed", health, max_health)
	
	# Re-enable movement and collision
	set_physics_process(true)
	if has_node("CollisionShape2D"):
		$CollisionShape2D.disabled = false
	
	# Reset dead state
	is_dead = false
	
	# Reset to idle animation
	$AnimatedSprite2D.speed_scale = 1.0  # Reset animation speed
	play_idle_animation()
	print("Player respawned")
