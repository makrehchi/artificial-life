import pygame, random

from environment import Environment


grid = (200, 100)
num_resources = 0
resource_size = 100
num_traps = 0
agent_specific_resource = 0
fuel_requirement_resource = 0
fuel_threshold_resource = 0
fuel_required = 700
fuel_threshold = 400
barrier_type = "static" # static or dynamic
num_barriers = 200 # for dynamic enter number of barriers, for static enter the exact coordinates
barriers = barriers = [
    *[(x, 32) for x in range(20, 60)],
    *[(x, 90) for x in range(130, 170)],
    *[(40, y) for y in range(63, 93)],
    *[(150, y) for y in range(20, 33)],
]
num_agents = 20
agent_fuel_low_range = 400
agent_fuel_high_range = 700
view_range = 10
death_rate = 0.002
birth_rate = 0.008
generation_period = 500
inheritance_type = "random"  # distribute, agent_with_least_fuel, agent_with_most_fuel, random


time = 0
grid_x, grid_y = grid
if barrier_type == "dynamic":
    barriers = [(random.randint(0, grid_x - 1), random.randint(0, grid_y - 1)) for _ in range(num_barriers)]

# Create an instance of the Environment class
env = Environment(grid_x, grid_y, num_resources, resource_size, num_traps, num_agents, agent_fuel_low_range,
                  agent_fuel_high_range, view_range, death_rate, birth_rate, generation_period, inheritance_type, barriers, agent_specific_resource, fuel_requirement_resource, fuel_threshold_resource, fuel_required, fuel_threshold)

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
LIGHT_GRAY = (249, 249, 249)

# print environment stats
def print_environment_stats(env):
    print("\033[1;33mNumber of Targets:", len(env.targets), "\033[0m")
    print("\033[1;33mNumber of Agents:", len(env.agents), "\033[0m")

# Inherit fuel from dead agents to alive agents depending on the inheritance type
def inherit_fuel(agent, fuel_to_inherit, inheritance_type, agents):
    if inheritance_type == "distribute":
        num_alive_agents = len(agents)
        if num_alive_agents > 0:
            fuel_to_add = fuel_to_inherit // num_alive_agents
            for alive_agent in agents:
                alive_agent.fuel += fuel_to_add
            print("\033[1;33mAgent", agent.agent_id, "expired with", fuel_to_inherit, "fuel, which was distributed across all agents.\033[0m")

    elif inheritance_type == "agent_with_least_fuel":
        if len(agents) > 0:
            agent_with_least_fuel = min(agents, key=lambda a: a.fuel)
            agent_with_least_fuel.fuel += fuel_to_inherit
            print("\033[1;33mAgent", agent.agent_id, "expired with", fuel_to_inherit, "fuel, which was inherited by agent with the least fuel:", agent_with_least_fuel.agent_id, "\033[0m")

    elif inheritance_type == "agent_with_most_fuel":
        if len(agents) > 0:
            agent_with_most_fuel = max(agents, key=lambda a: a.fuel)
            agent_with_most_fuel.fuel += fuel_to_inherit
            print("\033[1;33mAgent", agent.agent_id, "expired with", fuel_to_inherit, "fuel, which was inherited by agent with the most fuel:", agent_with_most_fuel.agent_id, "\033[0m")

    elif inheritance_type == "random":
        if len(agents) > 0:
            random_agent = random.choice(agents)
            random_agent.fuel += fuel_to_inherit
            print("\033[1;34mAgent", agent.agent_id, "expired with", fuel_to_inherit, "fuel, which was inherited by a random agent:", random_agent.agent_id, "\033[0m")


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
            fuel_to_inherit = agent.fuel
            if agent in agents:
                agents.remove(agent)
                print("\033[1;31mAgent", agent.agent_id, "expired due to a trap at coordinates:", "(" + str(agent.x) + "," + str(agent.y) + "). With a birth time of", agent.birth_time, "and an expiration time of", time, "and fuel of", agent.fuel, "\033[0m")
                inherit_fuel(agent, fuel_to_inherit, inheritance_type, agents)

        
        if agent.fuel <= 0:
            agent.death_time = time
            agents.remove(agent)
            print("\033[1;31mAgent", agent.agent_id, "expired due to lack of fuel at coordinates:", "(" + str(agent.x) + "," + str(agent.y) + "). With a birth time of", agent.birth_time, "and an expiration time of", agent.death_time, "\033[0m")


    if random.random() <= death_rate:
        agent.death_time = time
        fuel_to_inherit = agent.fuel
        agents.remove(agent)    
        print("\033[1;31mAgent", agent.agent_id, "expired at coordinates:", "(" + str(agent.x) + "," + str(agent.y) + "). With a birth time of", agent.birth_time, "and an expiration time of", agent.death_time, "and fuel of", agent.fuel, "\033[0m")
        inherit_fuel(agent, fuel_to_inherit, inheritance_type, agents)

    if random.random() <= birth_rate:
        env.generate_single_agent()
        new_agent = env.agents[-1]
        print("\033[1;32mAgent", agent.agent_id, "was spawned at coordinates:", "(" + str(agent.x) + "," + str(agent.y) + "). With a birth time of", agent.birth_time, "and fuel of", agent.fuel , "\033[0m")

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
