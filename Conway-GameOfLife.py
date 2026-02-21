import numpy    #type: ignore
import matplotlib.pyplot as plt #type: ignore
import matplotlib.animation as animation    #type: ignore
from matplotlib.colors import ListedColormap    #type: ignore
from matplotlib.patches import Patch    #type: ignore

class probabilityCelluarAutomata:
    def __init__(self, size, states, neighborhood = "8_neighbours"):
        self.size = size
        self.states = states
        self.grid = numpy.zeros((size, size), dtype=int)

        if neighborhood == "8_neighbours":
            self.neighbors = [(x_axis, y_axis) for x_axis in (-1, 0, 1) for y_axis in (-1, 0, 1) if not (x_axis == 0 and y_axis == 0)]
        elif neighborhood == "4_neighbours":
            self.neighbors = [(-1,0),(1,0),(0,-1),(0,1)]

    def randomize(self, probabilities = None):
        if probabilities is None:
            self.grid = numpy.random.choice(self.states, size = (self.size, self.size))
        else:
            self.grid = numpy.random.choice(self.states, size = (self.size, self.size), p = probabilities)


    def count_neighbors(self, state):
        total = numpy.zeros_like(self.grid)

        for neighbour_x, neighbour_y in self.neighbors:
            total = total + (numpy.roll(numpy.roll(self.grid, neighbour_x, axis = 0), neighbour_y, axis=1) == state)

        return total



class probabilisticGameOfLife(probabilityCelluarAutomata):
    def __init__(self, size, into_existence_probs = 1.0, death_variance = 0.0):

        super().__init__(size, states = [0,1])

        self.into_existence_probs = into_existence_probs
        self.death_variance = death_variance

    def next_frame(self):
        neighbors = self.count_neighbors(1)

        grid = numpy.zeros_like(self.grid)

        exist = (self.grid == 0) & (neighbors == 3)
        exist_random = numpy.random.rand(self.size, self.size)

        grid[exist & (exist_random < self.into_existence_probs)] = 1

        survive = (self.grid == 1) & ((neighbors == 2) | (neighbors == 3))
        death_randon = numpy.random.rand(self.size, self.size)

        grid[survive & (death_randon > self.death_variance)] = 1

        self.grid = grid


class PredatorPrey(probabilityCelluarAutomata):
    def __init__(self, size, prey_exists = 0.25, predator_val = 0.4, predator_death = 0.2):
        super().__init__(size, states=[0,1,2])

        self.prey_exists = prey_exists
        self.predator_val = predator_val
        self.predator_death = predator_death

    def next_frame(self):
        new_grid = self.grid.copy()

        prey_neighbors = self.count_neighbors(1)
        predator_neighbors = self.count_neighbors(2)

        random_prey = numpy.random.rand(self.size, self.size)
        random_predator = numpy.random.rand(self.size, self.size)

        empty = (self.grid == 0)
        prey_exists = empty & (prey_neighbors > 0)
        new_grid[prey_exists & (random_prey < self.prey_exists)] = 1

        prey_cells = (self.grid == 1)
        prey_unalives = prey_cells & (predator_neighbors > 0)
        new_grid[prey_unalives & (random_predator < self.predator_val)] = 2

        predator_cells = (self.grid == 2)
        predator_unalives = numpy.random.rand(self.size, self.size)
        new_grid[predator_cells & (predator_unalives < self.predator_death)] = 0

        self.grid = new_grid



def animate_ca(automata, steps=200, interval=1000):
    fig, ax = plt.subplots()

    cmap = ListedColormap(["white", "green", "red"])

    im = ax.imshow(automata.grid, cmap=cmap, vmin=0, vmax=2, interpolation='nearest')
    ax.set_title("Predator–Prey Probabilistic Cellular Automaton")
    ax.axis("off")

    legend_elements = [
        Patch(facecolor="white", edgecolor="black", label="Empty"),
        Patch(facecolor="green", label="Prey"),
        Patch(facecolor="red", label="Predator"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    def update(frame):
        automata.next_frame()
        im.set_array(automata.grid)
        return [im]

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=steps,
        interval=interval,
        blit=False
    )

    plt.show()



SIZE = 100

GameOfLife = probabilisticGameOfLife(SIZE, 0.9, 0.05)
GameOfLife.randomize()

predator_prey = PredatorPrey(SIZE, 0.1, 0.5, 0.25)
predator_prey.randomize(probabilities = [0.95, 0.025, 0.025])

animate_ca(GameOfLife, steps = 500)