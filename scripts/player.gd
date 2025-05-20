extends CharacterBody2D

@export var speed = 200.0
@export var sprint_speed = 160.0  # Sprint speed when Shift is held
@export var max_health = 100
var health = max_health
var current_direction = "front"  # Track the current direction
var is_hurt = false  # Track if player is in hurt state
var hurt_timer = 0.0  # Timer for hurt animation

signal health_changed(new_health, max_health)

func _physics_process(delta):
	# Handle hurt state timer
	if is_hurt:
		hurt_timer -= delta
		if hurt_timer <= 0:
			is_hurt = false
		else:
			# Skip movement processing if player is hurt
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
				if abs(direction.x) > abs(direction.y):
					# Horizontal movement is dominant
					if direction.x > 0:
						sprite.play("right")
						current_direction = "right"
					else:
						sprite.play("left")
						current_direction = "left"
				else:
					# Vertical movement is dominant
					if direction.y > 0:
						sprite.play("front")
						current_direction = "front"
					else:
						sprite.play("back")
						current_direction = "back"
				
				# Adjust animation speed based on sprinting
				sprite.speed_scale = 1.5 if is_sprinting else 1.0
			else:
				# Fallback to default animation
				sprite.play("default")
	else:
		# Stop animation if not moving
		if has_node("AnimatedSprite2D"):
			$AnimatedSprite2D.stop()
	
	# Apply velocity with appropriate speed
	var current_speed = sprint_speed if Input.is_action_pressed("shift_key") else speed
	velocity = direction * current_speed
	move_and_slide()

func _ready():
	# Register WASD inputs if they don't exist yet
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
	
	# Initialize health
	health = max_health
	emit_signal("health_changed", health, max_health)

func take_damage(damage_amount):
	health -= damage_amount
	health = max(0, health)  # Ensure health doesn't go below 0
	emit_signal("health_changed", health, max_health)
	
	# Play hurt animation based on current direction
	play_hurt_animation()
	
	if health <= 0:
		die()

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
			
			# Connect to animation finished if not already connected
			if not sprite.animation_finished.is_connected(_on_hurt_animation_finished):
				sprite.animation_finished.connect(_on_hurt_animation_finished)

func _on_hurt_animation_finished():
	if is_hurt:
		# Continue showing the last frame of hurt animation until hurt timer expires
		pass
	else:
		# If not hurt anymore, switch back to idle or movement animation
		var sprite = $AnimatedSprite2D
		if sprite.animation.begins_with("hurt_"):
			sprite.stop()

func heal(amount):
	health += amount
	health = min(health, max_health)  # Ensure health doesn't exceed max
	emit_signal("health_changed", health, max_health)

#من عيون الناس بسم الله عليك :)
func die():
	# Handle player death logic
	print("Player died!")
	
	# Respawn player at the center of the map
	position = Vector2(582, 362)
	
	# Reset player health
	health = max_health
	emit_signal("health_changed", health, max_health)
	
	# Optional: play respawn animation or sound effect
