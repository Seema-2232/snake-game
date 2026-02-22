import tkinter as tk
import random
import winsound
import os

# ================= SETTINGS =================
WIDTH = 700
HEIGHT = 650
SNAKE_SIZE = 20
HIGH_SCORE_FILE = "highscores.txt"

# Difficulty presets
DIFFICULTIES = {
    "Easy": 150,
    "Medium": 110,
    "Hard": 80
}

# ================= INIT =================
root = tk.Tk()
root.title("Ultimate Snake Pro Edition")
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#0f0f1a", highlightthickness=0)
canvas.pack()

# ================= GLOBAL VARIABLES =================
snake1 = []
snake2 = []
food = None
power_up = None
power_type = None
score1 = 0
score2 = 0
direction1 = "Right"
direction2 = "Left"
game_over = False
multiplayer = False
difficulty_speed = 110
gradient_offset = 0
high_scores = []
double_points = False
speed_modifier = 0

# ================= FILE HANDLING =================
def load_scores():
    global high_scores
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            high_scores = [int(x.strip()) for x in f.readlines()]
    else:
        high_scores = []

def save_score(score):
    high_scores.append(score)
    high_scores.sort(reverse=True)
    high_scores[:] = high_scores[:5]
    with open(HIGH_SCORE_FILE, "w") as f:
        for s in high_scores:
            f.write(str(s) + "\n")

load_scores()

# ================= MUSIC =================
def play_music():
    if os.path.exists("bgmusic.wav"):
        winsound.PlaySound("bgmusic.wav", winsound.SND_LOOP | winsound.SND_ASYNC)

def stop_music():
    winsound.PlaySound(None, winsound.SND_ASYNC)

# ================= SPAWN FUNCTIONS =================
def spawn_food():
    global food
    while True:
        fx = random.randrange(0, WIDTH, SNAKE_SIZE)
        fy = random.randrange(80, HEIGHT, SNAKE_SIZE)
        if (fx, fy) not in snake1 and (fx, fy) not in snake2:
            food = (fx, fy)
            break

def spawn_powerup():
    global power_up, power_type
    types = ["Speed", "Slow", "Double"]
    power_type = random.choice(types)
    while True:
        px = random.randrange(0, WIDTH, SNAKE_SIZE)
        py = random.randrange(80, HEIGHT, SNAKE_SIZE)
        if (px, py) not in snake1 and (px, py) not in snake2:
            power_up = (px, py)
            break

# ================= DRAW FUNCTIONS =================
def draw_grid():
    for i in range(0, WIDTH, SNAKE_SIZE):
        canvas.create_line(i, 80, i, HEIGHT, fill="#1f1f2e")
    for i in range(80, HEIGHT, SNAKE_SIZE):
        canvas.create_line(0, i, WIDTH, i, fill="#1f1f2e")

def draw_snake(snake, base_color):
    global gradient_offset
    for idx, (x, y) in enumerate(snake):
        color_value = (idx*15 + gradient_offset) % 255
        if base_color == "green":
            color = f'#00{color_value:02x}66'
        else:
            color = f'#{color_value:02x}0066'
        canvas.create_rectangle(x, y, x+SNAKE_SIZE, y+SNAKE_SIZE, fill=color, outline="")

def draw_objects():
    canvas.delete("all")
    draw_grid()

    # HUD
    canvas.create_rectangle(0,0,WIDTH,70, fill="#141428")
    canvas.create_text(150,35,text=f"P1: {score1}", fill="cyan", font=("Consolas",18,"bold"))
    if multiplayer:
        canvas.create_text(WIDTH-150,35,text=f"P2: {score2}", fill="magenta", font=("Consolas",18,"bold"))
    canvas.create_text(WIDTH//2,35,text=f"High: {max(high_scores) if high_scores else 0}",
                       fill="yellow", font=("Consolas",16))

    draw_snake(snake1,"green")
    if multiplayer:
        draw_snake(snake2,"red")

    # Food
    if food:
        canvas.create_oval(food[0], food[1],
                           food[0]+SNAKE_SIZE, food[1]+SNAKE_SIZE,
                           fill="red")

    # Power-up
    if power_up:
        color = {"Speed":"orange","Slow":"blue","Double":"gold"}[power_type]
        canvas.create_rectangle(power_up[0], power_up[1],
                                power_up[0]+SNAKE_SIZE, power_up[1]+SNAKE_SIZE,
                                fill=color)

# ================= GAME LOGIC =================
def move():
    global snake1, snake2, score1, score2, game_over
    global gradient_offset, speed_modifier, double_points

    if game_over:
        return

    gradient_offset += 10

    snake1 = update_snake(snake1, direction1)
    if multiplayer:
        snake2 = update_snake(snake2, direction2)

    check_collisions()

    draw_objects()

    delay = max(50, difficulty_speed + speed_modifier)
    root.after(delay, move)

def update_snake(snake, direction):
    head_x, head_y = snake[0]

    if direction == "Up":
        head_y -= SNAKE_SIZE
    elif direction == "Down":
        head_y += SNAKE_SIZE
    elif direction == "Left":
        head_x -= SNAKE_SIZE
    elif direction == "Right":
        head_x += SNAKE_SIZE

    head_x %= WIDTH
    head_y = max(80, head_y % HEIGHT)

    new_head = (head_x, head_y)

    # Collision with self or other snake
    if new_head in snake or (multiplayer and snake == snake1 and new_head in snake2) or (multiplayer and snake == snake2 and new_head in snake1):
        end_game()
        return snake

    snake = [new_head] + snake[:-1]
    return snake

def check_collisions():
    global score1, score2, food, power_up
    global speed_modifier, double_points

    # Player 1 food
    if snake1[0] == food:
        snake1.append(snake1[-1])
        score1 += 2 if double_points else 1
        spawn_food()
        if random.random() < 0.3:
            spawn_powerup()

    # Player 2 food
    if multiplayer and snake2[0] == food:
        snake2.append(snake2[-1])
        score2 += 1
        spawn_food()

    # Power-ups for P1
    if power_up and snake1[0] == power_up:
        apply_powerup()
        power_up = None

    # Power-ups for P2
    if multiplayer and power_up and snake2[0] == power_up:
        apply_powerup()
        power_up = None

def apply_powerup():
    global speed_modifier, double_points

    if power_type == "Speed":
        speed_modifier = -40
        root.after(5000, reset_speed)
    elif power_type == "Slow":
        speed_modifier = 40
        root.after(5000, reset_speed)
    elif power_type == "Double":
        double_points = True
        root.after(5000, reset_double)

def reset_speed():
    global speed_modifier
    speed_modifier = 0

def reset_double():
    global double_points
    double_points = False

def end_game():
    global game_over
    game_over = True
    stop_music()
    save_score(max(score1, score2))
    show_menu()

# ================= CONTROLS =================
def key_control(event):
    global direction1, direction2
    keys = event.keysym.lower()

    # Player 1 arrows
    if keys == "up": direction1 = "Up"
    if keys == "down": direction1 = "Down"
    if keys == "left": direction1 = "Left"
    if keys == "right": direction1 = "Right"

    # Player 2 WASD
    if multiplayer:
        if keys == "w": direction2 = "Up"
        if keys == "s": direction2 = "Down"
        if keys == "a": direction2 = "Left"
        if keys == "d": direction2 = "Right"

root.bind("<Key>", key_control)

# ================= MENU =================
def start_game(mode, diff):
    global snake1, snake2, score1, score2
    global multiplayer, difficulty_speed, game_over

    multiplayer = mode
    difficulty_speed = DIFFICULTIES[diff]

    snake1 = [(200,200),(180,200),(160,200)]
    snake2 = [(500,200),(520,200),(540,200)]
    score1 = 0
    score2 = 0
    game_over = False

    spawn_food()
    play_music()
    move()

def show_menu():
    canvas.delete("all")

    canvas.create_text(WIDTH//2,150,text="ULTIMATE SNAKE",
                       fill="cyan", font=("Consolas",36,"bold"))

    tk.Button(root,text="Single Player - Easy",
              command=lambda:start_game(False,"Easy")).place(x=260,y=250)

    tk.Button(root,text="Single Player - Medium",
              command=lambda:start_game(False,"Medium")).place(x=250,y=290)

    tk.Button(root,text="Single Player - Hard",
              command=lambda:start_game(False,"Hard")).place(x=270,y=330)

    tk.Button(root,text="Multiplayer Mode",
              command=lambda:start_game(True,"Medium")).place(x=280,y=380)

# ================= START =================
show_menu()
root.mainloop()
