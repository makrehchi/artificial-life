import pygame
import random

from environment import Environment
from agent import Agent
from target import Target

grid_x = 150  # The x coordinate of the simulation grid
grid_y = 100  # The y coordinate of the simulation grid
num_resources = 15  # the number of resources that the agents collect and get fuel from
resource_size = 100  # the amount of fuel that the agents get when they collect the fuel
num_traps = 5  # when an agent collects this, they die
barrier_type = "dynamic" # static or dynamic
num_barriers = 200 # for dynamic enter number of barriers, for static enter the exact coordinates
barriers = [(35,42), (35,43), (35,44), (35,45), (35,46), (35,47), (35,48), (35,49), (35,50), (35,51), (35,52), (35,53), (78, 72), (79, 72), (80, 72), (81, 72), (82, 72), (83, 72), (84, 72), (85, 72), (86, 72), (87, 72), (88, 72), (89, 72)]
num_agents = 10  # the number of agents that will be spawned in the environment
agent_fuel_low_range = 400  # Fuel will be randomly assigned to each agent, but the user gets to decide the range of the fuel
agent_fuel_high_range = 1000
view_range = 10  # an agent has a viewing range, so if they see a target/trap (they don't know the difference) they move towards it.
death_rate = 0.002  # the float rate at which each turn/move die/despawn during the game
birth_rate = 0.004  # the float rate at which agents are randomly spawned in with the fuel range that was earlier specified
generation_period = 500  # After a certain number of moves, the agents that the user specified are spawned again with the same fuel ranges
inheritance_type = "distribute, agent with least fuel, agent with most fuel, random"  # when an agent dies randomly or from traps, their fuel will be transferred to agents depending on the type the user selects

time = 0  # the time of the simulation
if barrier_type == "dynamic":
    barriers = [(random.randint(0, grid_x - 1), random.randint(0, grid_y - 1)) for _ in range(num_barriers)]

# Create an instance of the Environment class
env = Environment(grid_x, grid_y, num_resources, resource_size, num_traps, num_agents, agent_fuel_low_range,
                  agent_fuel_high_range, view_range, death_rate, birth_rate, generation_period, inheritance_type, barriers)

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
view_range = 10  # an agent has a viewing range, so if they see a target/trap(they don't know the difference) they move towards it.
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


def print_environment_stats(env):
    print("Number of Targets:", len(env.targets))
    print("Number of Agents:", len(env.agents))


# Run the simulation
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # Draw barriers
    for barrier_cell in barriers:
        pygame.draw.rect(screen, GRAY, (barrier_cell[0] * 7, barrier_cell[1] * 7, 7, 7))

    # Draw targets
    for target in targets:
        if target.is_resource:
            pygame.draw.rect(screen, GREEN, (target.x * 7, target.y * 7, 7, 7))
        else:
            pygame.draw.rect(screen, RED, (target.x * 7, target.y * 7, 7, 7))

    # Move agents and check for trap collision
    for agent in agents:
        agent.move_randomly()
        agent.fuel -= 1
        if agent.check_trap_collision(env.targets):
            env.remove_target(agent.x, agent.y)
            agents.remove(agent)
            print("FROM TRAP:")
            print("Agent ID:", agent.agent_id, "Coordinates:", agent.x, agent.y, "Birth Time:", agent.birth_time, "Death Time:", time, "Fuel:", agent.fuel)

        
        if agent.fuel <= 0:
            agent.death_time = time
            agents.remove(agent)
            print("FROM FUEL:")
            print("Agent ID:", agent.agent_id, "Coordinates:", agent.x, agent.y, "Birth Time:", agent.birth_time, "Death Time:", agent.death_time, "Fuel:", agent.fuel)


    if random.random() <= death_rate:
        agent.death_time = time
        agents.remove(agent)    
        print("FROM DEATH RATE:")
        print("Agent ID:", agent.agent_id, "Coordinates:", agent.x, agent.y, "Birth Time:", agent.birth_time, "Death Time:", agent.death_time, "Fuel:", agent.fuel)

    if random.random() <= birth_rate:
        env.generate_single_agent()
        new_agent = env.agents[-1]
        print("FROM BIRTH RATE:")
        print("Agent ID:", agent.agent_id, "Coordinates:", agent.x, agent.y, "Birth Time:", agent.birth_time, "Fuel:", agent.fuel)

    # Draw agents
    for agent in agents:
        pygame.draw.rect(screen, BLACK, (agent.x * 7, agent.y * 7, 7, 7))

    pygame.display.flip()
    clock.tick(40)

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
        print("Time:", time)
        print_environment_stats(env)

pygame.quit()
