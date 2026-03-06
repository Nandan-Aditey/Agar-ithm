import pygame
import random
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# --- Configuration Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 10
SIMULATION_TIME = 5 # seconds per generation
POP_SIZE = 30
MAX_TRAIT = 100

SENSING_RADIUS = 150 
FOOD_SPAWN_RATE = 1 # Spawning faster to accommodate starvation mechanic

# Colors
BG_COLOR = (30, 30, 30)
PLAYER_COLOR = (50, 150, 255)
COMPUTER_COLOR = (255, 50, 50)
FOOD_COLOR = (50, 255, 50)

class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Cell(Entity):
    def __init__(self, x, y, strength, color):
        super().__init__(x, y)
        self.strength = max(0.1, min(MAX_TRAIT, strength))
        self.agility = MAX_TRAIT - self.strength
        
        self.speed = 0.5 + (self.agility / 20.0) 
        self.radius = 4 + (self.strength / 10.0)
        self.color = color
        self.food_eaten = 0
        
        # --- NEW: Starvation Mechanic ---
        self.frames_since_meal = 0
        # High agility = lower metabolic rate = survives longer without food
        # Ranges from 2 seconds (0 agility) to 6 seconds (100 agility)
        self.max_hunger_frames = FPS * (2 + (self.agility / 25.0))

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def update(self, foods, enemies):
        self.frames_since_meal += 1
        
        best_target = None
        min_dist = float('inf')

        for enemy in enemies:
            if self.strength > enemy.strength:
                dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
                if dist < SENSING_RADIUS and dist < min_dist:
                    best_target = enemy
                    min_dist = dist

        if best_target is None:
            for f in foods:
                dist = math.hypot(self.x - f.x, self.y - f.y)
                if dist < min_dist:
                    best_target = f
                    min_dist = dist

        if best_target:
            self.move_towards(best_target.x, best_target.y)
        else:
            self.move_towards(self.x + random.uniform(-1, 1), self.y + random.uniform(-1, 1))

        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

def show_analytics(history_data):
    if not history_data:
        print("Not enough data to graph.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    plt.subplots_adjust(bottom=0.25)

    def draw_graph(val):
        ax.clear()
        gen_idx = int(slider.val) - 1
        data = history_data[gen_idx]
        
        strengths = data['comp_strengths']
        
        if strengths:
            ax.hist(strengths, bins=np.linspace(0, 100, 20), color='red', alpha=0.7, edgecolor='black')
        
        ax.set_xlim(0, 100)
        ax.set_ylim(0, POP_SIZE)
        ax.set_title(f"Generation {data['gen']} | Computer Alive: {data['c_alive']} | Player Alive: {data['p_alive']}")
        ax.set_xlabel("Strength (0-100)")
        ax.set_ylabel("Number of Cells")
        fig.canvas.draw_idle()

    ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
    slider = Slider(ax_slider, 'Generation', 1, len(history_data), valinit=1, valstep=1)
    slider.on_changed(draw_graph)

    draw_graph(1)
    plt.show()

def main():
    while True:
        try:
            player_strength = float(input("Enter Player Cell Strength (0-100): "))
            if 0 <= player_strength <= 100:
                break
            print("Please enter a value between 0 and 100.")
        except ValueError:
            print("Invalid input.")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Natural Selection Spatial Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    comp_mean_strength = 50.0
    comp_std_strength = 30.0
    generation = 1
    history_data = [] # Stores data for matplotlib

    def spawn_populations(comp_mean, comp_std):
        p = [Cell(random.randint(0, WIDTH), random.randint(0, HEIGHT), player_strength, PLAYER_COLOR) for _ in range(POP_SIZE)]
        c = [Cell(random.randint(0, WIDTH), random.randint(0, HEIGHT), np.random.normal(comp_mean, comp_std), COMPUTER_COLOR) for _ in range(POP_SIZE)]
        return p, c

    p_cells, c_cells = spawn_populations(comp_mean_strength, comp_std_strength)
    foods = []
    frames = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        frames += 1

        if frames % FOOD_SPAWN_RATE == 0:
            foods.append(Entity(random.randint(10, WIDTH-10), random.randint(10, HEIGHT-10)))

        for p in p_cells: p.update(foods, c_cells)
        for c in c_cells: c.update(foods, p_cells)

        # Handle Starvation
        p_cells = [p for p in p_cells if p.frames_since_meal < p.max_hunger_frames]
        c_cells = [c for c in c_cells if c.frames_since_meal < c.max_hunger_frames]

        # Eating Food
        for cell_list in [p_cells, c_cells]:
            for cell in cell_list:
                for f in foods[:]: 
                    if math.hypot(cell.x - f.x, cell.y - f.y) < cell.radius + 3:
                        if f in foods:
                            foods.remove(f)
                            cell.food_eaten += 1
                            cell.frames_since_meal = 0 # Reset hunger

        # Combat
        for p in p_cells[:]:
            for c in c_cells[:]:
                if math.hypot(p.x - c.x, p.y - c.y) < (p.radius + c.radius):
                    if p.strength > c.strength:
                        if c in c_cells: c_cells.remove(c)
                        p.food_eaten += 1 
                        p.frames_since_meal = 0
                    elif c.strength > p.strength:
                        if p in p_cells: p_cells.remove(p)
                        c.food_eaten += 1 
                        c.frames_since_meal = 0

        # Evolution Phase
        if frames >= SIMULATION_TIME * FPS or len(p_cells) == 0:
            # Record data before respawning8
            history_data.append({
                'gen': generation,
                'p_alive': len(p_cells),
                'c_alive': len(c_cells),
                'comp_strengths': [c.strength for c in c_cells]
            })

            generation += 1
            frames = 0
            foods.clear()
            
            if len(c_cells) > 0:
                surviving_strengths = [c.strength for c in c_cells]
                comp_mean_strength = np.mean(surviving_strengths)
                comp_std_strength = max(np.std(surviving_strengths), 2.0) 
            else:
                comp_mean_strength += random.uniform(-5, 5)

            p_cells, c_cells = spawn_populations(comp_mean_strength, comp_std_strength)

        screen.fill(BG_COLOR)
        
        for f in foods: pygame.draw.circle(screen, FOOD_COLOR, (f.x, f.y), 3)
        for c in c_cells: c.draw(screen)
        for p in p_cells: p.draw(screen)

        time_left = max(0, SIMULATION_TIME - (frames / FPS))
        ui_text = [
            f"Generation: {generation}",
            f"Time Left: {time_left:.1f}s",
            f"Player (Blue) Alive: {len(p_cells)} | Str: {player_strength:.1f}",
            f"Comp (Red) Alive: {len(c_cells)} | Avg Str: {comp_mean_strength:.1f}"
        ]
        
        for i, text in enumerate(ui_text):
            img = font.render(text, True, (255, 255, 255))
            screen.blit(img, (10, 10 + (i * 25)))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    
    # Show Analytics after Pygame closes
    print("Launching analytics dashboard...")
    show_analytics(history_data)

if __name__ == "__main__":
    main()