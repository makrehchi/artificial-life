import pygame, random

from environment import Environment

grid = (200, 100)  # The size of the grid
num_resources = 15  # the number of resources that the agents collect and get fuel from
resource_size = 100  # the amount of fuel that the agents get when they collect the fuel
num_traps = 5  # when an agent collects this, they die
barrier_type = "dynamic" # static or dynamic
num_barriers = 200 # for dynamic enter number of barriers, for static enter the exact coordinates
barriers = [(35,42), (35,43), (35,44), (35,45), (35,46), (35,47), (35,48), (35,49), (35,50), (35,51), (35,52), (35,53), (78, 72), (79, 72), (80, 72), (81, 72), (82, 72), (83, 72), (84, 72), (85, 72), (86, 72), (87, 72), (88, 72), (89, 72)]
num_agents = 20  # the number of agents that will be spawned in the environment
agent_fuel_low_range = 400  # Fuel will be randomly assigned to each agent, but the user gets to decide the range of the fuel
agent_fuel_high_range = 1000
view_range = 10  # an agent has a viewing range, so if they see a target/trap (they don't know the difference) they move towards it.
death_rate = 0.002  # the float rate at which each turn/move die/despawn during the game
birth_rate = 0.004  # the float rate at which agents are randomly spawned in with the fuel range that was earlier specified
generation_period = 500  # After a certain number of moves, the agents that the user specified are spawned again with the same fuel ranges
inheritance_type = "random"  # (distribute, agent with least fuel, agent with most fuel, random) when an agent dies randomly or from traps, their fuel will be transferred to agents depending on the type the user selects

time = 0  # the time of the simulation
grid_x, grid_y = grid
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
LIGHT_GRAY = (249, 249, 249)

# print environment stats
def print_environment_stats(env):
    print("Number of Targets:", len(env.targets))
    print("Number of Agents:", len(env.agents))

# Inherit fuel from dead agents to alive agents depending on the inheritance type
def inherit_fuel(agent, fuel_to_inherit, inheritance_type, agents):
    if inheritance_type == "distribute":
        num_alive_agents = len(agents)
        if num_alive_agents > 0:
            fuel_to_add = fuel_to_inherit // num_alive_agents
            for alive_agent in agents:
                alive_agent.fuel += fuel_to_add
            print("Agent", agent.agent_id, "died.", "Inherited", fuel_to_inherit, "Using", inheritance_type, "went to all agents")

    elif inheritance_type == "agent_with_least_fuel":
        if len(agents) > 0:
            agent_with_least_fuel = min(agents, key=lambda a: a.fuel)
            agent_with_least_fuel.fuel += fuel_to_inherit
            print("Agent", agent.agent_id, "died.", "Inherited", fuel_to_inherit, "Using", inheritance_type, "went to agent with least fuel:", agent_with_least_fuel.agent_id)

    elif inheritance_type == "agent_with_most_fuel":
        if len(agents) > 0:
            agent_with_most_fuel = max(agents, key=lambda a: a.fuel)
            agent_with_most_fuel.fuel += fuel_to_inherit
            print("Agent", agent.agent_id, "died.", "Inherited", fuel_to_inherit, "Using", inheritance_type, "went to agent with most fuel:", agent_with_most_fuel.agent_id)

    elif inheritance_type == "random":
        if len(agents) > 0:
            random_agent = random.choice(agents)
            random_agent.fuel += fuel_to_inherit
            print("Agent", agent.agent_id, "died.", "Inherited", fuel_to_inherit, "Using", inheritance_type, "went to random agent:", random_agent.agent_id)


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
            agents.remove(agent)
            print("FROM TRAP:")
            print("Agent ID:", agent.agent_id, "Coordinates:", agent.x, agent.y, "Birth Time:", agent.birth_time, "Death Time:", time, "Fuel:", agent.fuel)
            inherit_fuel(agent, fuel_to_inherit, inheritance_type, agents)

        
        if agent.fuel <= 0:
            agent.death_time = time
            agents.remove(agent)
            print("FROM FUEL:")
            print("Agent ID:", agent.agent_id, "Coordinates:", agent.x, agent.y, "Birth Time:", agent.birth_time, "Death Time:", agent.death_time, "Fuel:", agent.fuel)


    if random.random() <= death_rate:
        agent.death_time = time
        fuel_to_inherit = agent.fuel
        agents.remove(agent)    
        print("FROM DEATH RATE:")
        print("Agent ID:", agent.agent_id, "Coordinates:", agent.x, agent.y, "Birth Time:", agent.birth_time, "Death Time:", agent.death_time, "Fuel:", agent.fuel)
        inherit_fuel(agent, fuel_to_inherit, inheritance_type, agents)

    if random.random() <= birth_rate:
        env.generate_single_agent()
        new_agent = env.agents[-1]
        print("FROM BIRTH RATE:")
        print("Agent ID:", agent.agent_id, "Coordinates:", agent.x, agent.y, "Birth Time:", agent.birth_time, "Fuel:", agent.fuel)

    for agent in agents:
        pygame.draw.circle(screen, LIGHT_GRAY, (agent.x * 7 + 3, agent.y * 7 + 3), 35)
    
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
    clock.tick(20)

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
