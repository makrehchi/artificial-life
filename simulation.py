import pygame, random

from environment import Environment


grid = (100, 100)
num_resources = 50
resource_size = 100
num_traps = 10
barrier_type = "static"
num_barriers = 100
barriers = [
    *[(x, 40) for x in range(20, 40)],
    *[(x, 50) for x in range(60, 80)],
    *[(x, 60) for x in range(100, 120)],
    *[(x, 70) for x in range(140, 160)],
]
num_agents = 30
agent_fuel_low_range = 300
agent_fuel_high_range = 800
view_range = 15
generation_period = 1000



time = 0
grid_x, grid_y = grid
if barrier_type == "dynamic":
    barriers = [(random.randint(0, grid_x - 1), random.randint(0, grid_y - 1)) for _ in range(num_barriers)]

# Create an instance of the Environment class
env = Environment(grid_x, grid_y, num_resources, resource_size, num_traps, num_agents, agent_fuel_low_range,
                  agent_fuel_high_range, view_range, generation_period, barriers)

# Generate agents and targets in the environment
env.generate_agents()
env.generate_targets()

# Access the agents and targets in the environment
agents = env.agents
targets = env.targets


# Pygame initialization
pygame.init()

scaled_grid_x = grid_x * 7
scaled_grid_y = grid_y * 7

# Define the scaled view range
scaled_view_range = view_range * 7

clock = pygame.time.Clock()
screen = pygame.display.set_mode((scaled_grid_x, scaled_grid_y))
pygame.display.set_caption("Grid Simulation")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (169, 169, 169)
LIGHT_GRAY = (249, 249, 249)

# print environment stats
def print_environment_stats(env):
    print("\033[1;33mNumber of Targets:", len(env.targets), "\033[0m")
    print("\033[1;33mNumber of Agents:", len(env.agents), "\033[0m")

# Run the simulation
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # Move agents and check for trap collision
    for agent in agents:
        agent.move_randomly()
        agent.fuel -= 1
        # Collect fuel if there is a resource/target on the current block
        agent.collect_fuel()
        # Check for trap collision
        if agent.check_trap_collision(env.targets):
            env.remove_target(agent.x, agent.y)
            if agent in agents:
                agents.remove(agent)
                print("\033[1;31mAgent", agent.agent_id, "expired due to a trap at coordinates:", "(" + str(agent.x) + "," + str(agent.y) + "). With a birth time of", agent.birth_time, "and an expiration time of", time, "and fuel of", agent.fuel, "\033[0m")

        
        if agent.fuel <= 0:
            agent.death_time = time
            agents.remove(agent)
            print("\033[1;31mAgent", agent.agent_id, "expired due to lack of fuel at coordinates:", "(" + str(agent.x) + "," + str(agent.y) + "). With a birth time of", agent.birth_time, "and an expiration time of", agent.death_time, "\033[0m")

    for agent in agents:
        pygame.draw.circle(screen, LIGHT_GRAY, (agent.x * 7 + 3, agent.y * 7 + 3), scaled_view_range)
    
    # Draw barriers
    for barrier_cell in barriers:
        pygame.draw.rect(screen, GRAY, (barrier_cell[0] * 7, barrier_cell[1] * 7, 7, 7))

    # Draw targets
    for target in targets:
        target_pos = (target.x * 7 + 3, target.y * 7 + 3)
        target_radius = 3
        if target.is_resource:
            pygame.draw.circle(screen, GREEN, target_pos, target_radius)
        else:
            pygame.draw.circle(screen, RED, target_pos, target_radius)

    # Draw agents
    for agent in agents:
        pygame.draw.circle(screen, BLACK, (agent.x * 7 + 3, agent.y * 7 + 3), 4)

    pygame.display.flip()
    clock.tick(50)

    # Increment time
    time += 1
    env.time += 1

    # Regenerate agents and targets after generation period
    if time % generation_period == 0:
        env.generate_agents()   
        env.generate_targets()
        agents = env.agents
        targets = env.targets

    # Print environment statistics
    if time % generation_period == 0:
        print("\033[1;33mTime:", time, "\033[0m")
        print_environment_stats(env)

pygame.quit()
