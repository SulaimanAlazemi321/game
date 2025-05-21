extends Area2D

var player_in_area = false
var prompt_label: Label = null
var canvas_layer: CanvasLayer = null
var panel: Panel = null

func _ready():
	# Connect signals
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	
	# Create a CanvasLayer to ensure prompt appears on top
	canvas_layer = CanvasLayer.new()
	canvas_layer.layer = 10 # High layer value to be on top
	add_child(canvas_layer)
	
	# Create a panel background
	panel = Panel.new()
	panel.size = Vector2(180, 40)
	panel.position = Vector2(get_viewport_rect().size.x / 2 - 90, 20)
	panel.visible = false
	canvas_layer.add_child(panel)
	
	# Create a prompt label
	prompt_label = Label.new()
	var label_settings = LabelSettings.new()
	label_settings.font_size = 24
	label_settings.outline_size = 3
	label_settings.outline_color = Color.BLACK
	label_settings.font_color = Color.WHITE
	prompt_label.label_settings = label_settings
	prompt_label.text = "Press F to enter"
	prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	prompt_label.size = Vector2(180, 40)
	prompt_label.position = Vector2(get_viewport_rect().size.x / 2 - 90, 20)
	prompt_label.visible = false
	canvas_layer.add_child(prompt_label)
	
	# Register F key input if not already registered
	if not InputMap.has_action("f_key"):
		InputMap.add_action("f_key")
		var f_event = InputEventKey.new()
		f_event.keycode = KEY_F
		InputMap.action_add_event("f_key", f_event)

func _process(_delta):
	if player_in_area and Input.is_action_just_pressed("f_key"):
		# Change to the inside house scene
		get_tree().change_scene_to_file("res://insideHouse.tscn")

func _on_body_entered(body):
	if body.is_in_group("player"):
		player_in_area = true
		panel.visible = true
		prompt_label.visible = true

func _on_body_exited(body):
	if body.is_in_group("player"):
		player_in_area = false
		panel.visible = false
		prompt_label.visible = false 