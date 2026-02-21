import pygame
import random
import math
import sys

WIDTH = 1100
HEIGHT = 750
FPS = 60
SIM_TIME = 30
INITIAL_CELLS = 30
POINT_BUDGET = 100

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AGAR-RITHM: Evolutionary Arena")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22)
big_font = pygame.font.SysFont(None, 40)


class Species:
    def __init__(self, name, color):
        self.name = name
        self.color = color

        self.strength = 25
        self.health = 25
        self.reproduction = 25
        self.agility = 25

    def normalize(self):
        total = self.strength + self.health + self.reproduction + self.agility
        scale = POINT_BUDGET / total
        self.strength *= scale
        self.health *= scale
        self.reproduction *= scale
        self.agility *= scale


class Cell:
    def __init__(self, x, y, species):
        self.x = x
        self.y = y
        self.species = species
        self.health = species.health / 5

        angle = random.uniform(0, 2 * math.pi)
        speed = species.agility / 20

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.radius = 4

    def move(self, cells):

        nearest_enemy = None
        min_dist = 9999

        for c in cells:
            if c.species != self.species:
                d = math.hypot(self.x - c.x, self.y - c.y)
                if d < min_dist:
                    min_dist = d
                    nearest_enemy = c

        if nearest_enemy:
            if self.species.strength > nearest_enemy.species.strength:
                angle = math.atan2(nearest_enemy.y - self.y,
                                   nearest_enemy.x - self.x)
            else:
                angle = math.atan2(self.y - nearest_enemy.y,
                                   self.x - nearest_enemy.x)

            speed = self.species.agility / 20
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed

        self.x += self.vx
        self.y += self.vy


        arena_width = WIDTH - 250

        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx *= -1

        if self.x + self.radius >= arena_width:
            self.x = arena_width - self.radius
            self.vx *= -1

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy *= -1

        if self.y + self.radius >= HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -1

    def draw(self):
        pygame.draw.circle(
            screen,
            self.species.color,
            (int(self.x), int(self.y)),
            self.radius
        )



species_list = [
    Species("Blue", (0,150,255)),
    Species("Red", (255,50,50)),
    Species("Green", (0,200,0)),
    Species("Purple", (150,0,150)),
    Species("Yellow", (240,220,0))
]

selected_species = 0
editing = True

def draw_ui():
    panel_x = WIDTH - 240
    pygame.draw.rect(screen, (30,30,30), (panel_x, 0, 240, HEIGHT))

    s = species_list[selected_species]

    y = 50
    for label, value in [
        ("Strength", s.strength),
        ("Health", s.health),
        ("Reproduction", s.reproduction),
        ("Agility", s.agility)
    ]:
        text = font.render(f"{label}: {int(value)}", True, (255,255,255))
        screen.blit(text, (panel_x+20, y))
        pygame.draw.rect(screen, s.color,
                         (panel_x+20, y+20, value*2, 10))
        y += 70

    instruction = font.render("Arrow Keys Adjust", True, (200,200,200))
    screen.blit(instruction, (panel_x+20, HEIGHT-80))



def run_simulation():
    cells = []
    spawn_positions = [
        (100,100),(WIDTH-350,100),
        (100,HEIGHT-100),
        (WIDTH-350,HEIGHT-100),
        (WIDTH//2-125, HEIGHT//2)
    ]

    for sp,(sx,sy) in zip(species_list, spawn_positions):
        for _ in range(INITIAL_CELLS):
            cells.append(Cell(
                sx+random.randint(-20,20),
                sy+random.randint(-20,20),
                sp
            ))

    start_time = pygame.time.get_ticks()

    running = True
    while running:
        clock.tick(FPS)
        screen.fill((15,15,15))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    mutate_random_species()

        elapsed = (pygame.time.get_ticks()-start_time)/1000
        if elapsed > SIM_TIME:
            running = False

        for cell in cells:
            cell.move(cells)

        for i in range(len(cells)):
            for j in range(i+1, len(cells)):
                c1 = cells[i]
                c2 = cells[j]
                if c1.species != c2.species:
                    if math.hypot(c1.x-c2.x, c1.y-c2.y) < 6:
                        if random.random() < c1.species.strength/100:
                            c2.health -= 1
                        if random.random() < c2.species.strength/100:
                            c1.health -= 1

        cells = [c for c in cells if c.health > 0]

        new_cells = []
        for cell in cells:
            if random.random() < cell.species.reproduction/5000:
                new_cells.append(Cell(cell.x, cell.y, cell.species))
        cells.extend(new_cells)

        for cell in cells:
            cell.draw()

        draw_population_graph(cells)

        pygame.display.flip()

    return cells


def draw_population_graph(cells):
    panel_x = WIDTH-240
    counts = {sp.name:0 for sp in species_list}
    for c in cells:
        counts[c.species.name]+=1

    y=50
    for sp in species_list:
        pygame.draw.rect(screen, sp.color,
                         (panel_x+20, y,
                          counts[sp.name], 10))
        label = font.render(f"{sp.name}: {counts[sp.name]}",
                            True,(255,255,255))
        screen.blit(label,(panel_x+20,y-15))
        y+=40

def mutate_random_species():
    sp = random.choice(species_list)
    attr = random.choice(["strength","health",
                          "reproduction","agility"])
    change = random.uniform(-5,5)
    setattr(sp, attr,
            max(5, getattr(sp,attr)+change))
    sp.normalize()


while editing:
    clock.tick(FPS)
    screen.fill((15,15,15))
    draw_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:

            s = species_list[selected_species]

            if event.key == pygame.K_1: selected_species=0
            if event.key == pygame.K_2: selected_species=1
            if event.key == pygame.K_3: selected_species=2
            if event.key == pygame.K_4: selected_species=3
            if event.key == pygame.K_5: selected_species=4

            if event.key == pygame.K_UP:
                s.strength +=5
            if event.key == pygame.K_DOWN:
                s.strength -=5
            if event.key == pygame.K_RIGHT:
                s.agility +=5
            if event.key == pygame.K_LEFT:
                s.agility -=5
            if event.key == pygame.K_SPACE:
                editing=False

            s.normalize()

    pygame.display.flip()

cells = run_simulation()

winner_names = set(c.species.name for c in cells)

screen.fill((0,0,0))
if len(winner_names)==1:
    winner = winner_names.pop()
    text = big_font.render(f"{winner} WINS!", True,(255,255,255))
else:
    text = big_font.render("TIME UP!", True,(255,255,255))

screen.blit(text,(WIDTH//2-150, HEIGHT//2))
pygame.display.flip()
pygame.time.wait(5000)
pygame.quit()
sys.exit()
