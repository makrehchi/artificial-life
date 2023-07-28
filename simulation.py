import pygame, random

from environment import Environment
from target import Target

# Read variables from a text file
def read_variables_from_file():
    with open("variables.txt", "r") as variables_file:
        variables = {}
        exec(variables_file.read(), variables)
        return variables

def calculate_income_gini_coefficient(agents):
    if not agents or all(agent.income_collected == 0 for agent in agents):
        return "No income"  # Return 0 if there are no agents or if all agents have zero income_collected
    
    total_fuel_collected = sum(agent.income_collected for agent in agents)
    n = len(agents)
    agents_sorted_by_income = sorted(agents, key=lambda agent: agent.income_collected)
    lorenz_curve = [sum(agent.income_collected for agent in agents_sorted_by_income[:i + 1]) / total_fuel_collected for i in range(n)]
    area_under_lorenz_curve = sum((lorenz_curve[i - 1] + lorenz_curve[i]) * (1 / n) for i in range(1, n))
    gini_coefficient = 1 - 2 * area_under_lorenz_curve
    return gini_coefficient

def calculate_wealth_gini_coefficient(agents):
    total_fuel = sum(agent.fuel for agent in agents)
    n = len(agents)
    agents_sorted_by_wealth = sorted(agents, key=lambda agent: agent.fuel)
    lorenz_curve = [sum(agent.fuel for agent in agents_sorted_by_wealth[:i + 1]) / total_fuel for i in range(n)]
    area_under_lorenz_curve = sum((lorenz_curve[i - 1] + lorenz_curve[i]) * (1 / n) for i in range(1, n))
    gini_coefficient = 1 - 2 * area_under_lorenz_curve
    return gini_coefficient

community_fund = 0

def calculate_total_fuel(agents):
    return sum(agent.fuel for agent in agents)

def redistribute(agents, tax_cutoff_percentage, uniform_tax_distribution):
    total_fuel_before_tax = calculate_total_fuel(agents)

    # Calculate the total amount of tax to be collected
    total_tax_collected = total_fuel_before_tax * (tax_cutoff_percentage / 100)

    # Calculate the tax to be collected from each agent
    individual_tax_amount = total_tax_collected / len(agents)

    # Collect the tax from each agent and add it to the community fund
    for agent in agents:
        tax_collected = min(individual_tax_amount, agent.fuel)
        agent.fuel -= tax_collected
        community_fund += tax_collected

    # Calculate the redistribution amount based on uniform or progressive distribution
    if uniform_tax_distribution:
        redistribution_amount = community_fund // len(agents)
    else:
        agents_sorted_by_income = sorted(agents, key=lambda agent: agent.income_collected)
        for i, agent in enumerate(agents_sorted_by_income):
            proportion = i / (len(agents_sorted_by_income) - 1)  # Progressively reduce the redistribution amount
            redistribution_amount = int(community_fund * proportion)
            agent.fuel += redistribution_amount


pygame.init()

variables = read_variables_from_file()

num_frames = variables.get("num_frames")
tax_frames = variables.get("tax_frames")
tax_cutoff_percentage = variables.get("tax_cutoff_percentage")
uniform_tax_distribution = variables.get("uniform_tax_distribution")
grid = variables.get("grid")
num_resources = variables.get("num_resources")
num_traps = variables.get("num_traps")
barrier_type = variables.get("barrier_type")
num_barriers = variables.get("num_barriers")
barriers = variables.get("barriers")
num_agents = variables.get("num_agents")
agent_fuel_low_range = variables.get("agent_fuel_low_range")
agent_fuel_high_range = variables.get("agent_fuel_high_range")
generation_period = variables.get("generation_period")
age_range_low = variables.get("age_range_low")
age_range_high = variables.get("age_range_high")
intelligence_range_low = variables.get("intelligence_range_low")
intelligence_range_high = variables.get("intelligence_range_high")
target_size_low = variables.get("target_size_low")
target_size_high = variables.get("target_size_high")

num_agents_A = variables.get("num_agents_A")
num_agents_B = variables.get("num_agents_B")
num_agents_C = variables.get("num_agents_C")
num_agents_D = variables.get("num_agents_D")
num_agents_random = variables.get("num_agents_random")
assign_agents_randomly = variables.get("assign_agents_randomly")

if assign_agents_randomly:
    num_agents = num_agents_random
else:
    num_agents = num_agents_A + num_agents_B + num_agents_C + num_agents_D

time = 0
grid_x, grid_y = grid
if barrier_type == "dynamic":
    barriers = [(random.randint(0, grid_x - 1), random.randint(0, grid_y - 1)) for _ in range(num_barriers)]

env = Environment(grid_x, grid_y, num_resources, num_traps, num_agents, agent_fuel_low_range,
                  agent_fuel_high_range, generation_period, barriers, age_range_low, age_range_high, intelligence_range_low, intelligence_range_high, target_size_low, target_size_high)

def generate_agents_by_specified_count(num_agents_A, num_agents_B, num_agents_C, num_agents_D):
    agents = []
    agents.extend([('A', num_agents_A), ('B', num_agents_B), ('C', num_agents_C), ('D', num_agents_D)])
    for resource_class, num_agents in agents:
        for _ in range(num_agents):
            env.generate_agents(resource_class)

# Generate agents and targets in the environment
if assign_agents_randomly:
    # Generate agents randomly
    for _ in range(num_agents_random):
        resource_class = random.choice(['A', 'B', 'C', 'D'])
        env.generate_agents(resource_class)
else:
    # Generate agents based on user-specified counts
    generate_agents_by_specified_count(num_agents_A, num_agents_B, num_agents_C, num_agents_D)

env.generate_targets()
env.generate_traps()

# Initialize total_redistributed_fuel outside the loop
total_redistributed_fuel = 0

# Access the agents and targets in the environment
agents = env.agents
targets = env.targets

scaled_grid_x = grid_x * 7
scaled_grid_y = grid_y * 7

clock = pygame.time.Clock()
screen = pygame.display.set_mode((scaled_grid_x, scaled_grid_y))
pygame.display.set_caption("Grid Simulation")

# Quadrant numbers for respective keys: 1 - Top Left, 2 - Top Right, 3 - Bottom Left, 4 - Bottom Right
key_to_quadrant = {
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
}

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 150, 0)
GRAY = (169, 169, 169)
LIGHT_GRAY = (249, 249, 249)

# Run the simulation
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Check if the pressed key is 1, 2, 3, or 4, and create a resource in the respective quadrant
            quadrant = key_to_quadrant.get(event.key)
            if quadrant is not None:
                x, y = env.get_random_point_in_quarter(quadrant)
                size = random.randint(env.target_size_low, env.target_size_high)
                resource_class = random.choice(['A', 'B', 'C', 'D'])
                target = Target(x, y, is_resource=True, size=size, resource_class=resource_class)
                env.targets.append(target)
    
    num_frames -= 1
    if num_frames <= 0:
        running = False

    screen.fill(WHITE)

    # Move agents and check for trap collision
    for agent in agents:
        if agent.check_trap_collision(env.targets):
        # If the agent collides with a trap, set is_trapped to True and remove the trap from the environment.
            agent.is_trapped = True
            agent.move_randomly()  # This prevents the trapped agent from moving.
            trap_x, trap_y = agent.x, agent.y
            env.remove_target(trap_x, trap_y)  # Remove the trap from the environment.
        else:
            # If the agent is not trapped, they can move normally.
            agent.move_randomly()
        agent.age += 1
        # Collect fuel if there is a resource/target on the current block
        agent.collect_fuel()

        if (agent.fuel <= 0) or (agent.age >= agent.max_age) or (agent.is_ill):
            agent.death_time = time
            if agent in agents:
                agents.remove(agent)
            if agent.fuel <= 5:
                agent.fuel += 100
            env.generate_single_agent(agent.fuel)

    # Draw barriers
    for barrier_cell in barriers:
        pygame.draw.rect(screen, GRAY, (barrier_cell[0] * 7, barrier_cell[1] * 7, 7, 7))

    # Draw targets
    for target in targets:
        target_pos = (target.x * 7 + 3, target.y * 7 + 3)
        target_radius = 3
        if target.is_resource:
            # Draw the symbol of the target resource class in GREEN
            font = pygame.font.Font(None, 16)
            text_surface = font.render(target.resource_class, True, GREEN)
            text_rect = text_surface.get_rect(center=target_pos)
            screen.blit(text_surface, text_rect)
        else:
            # Draw 'T' for traps in RED
            font = pygame.font.Font(None, 16)
            text_surface = font.render('T', True, RED)
            text_rect = text_surface.get_rect(center=target_pos)
            screen.blit(text_surface, text_rect)

    # Draw agents
    for agent in agents:
        # Draw the symbol of the agent ('A', 'B', 'C', or 'D') in GREEN
        font = pygame.font.Font(None, 16)
        text_surface = font.render(agent.resource_class, True, BLACK)
        text_rect = text_surface.get_rect(center=(agent.x * 7 + 3, agent.y * 7 + 3))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(20)

    # Increment time
    time += 1
    env.time += 1

    if time % tax_frames == 0:
        income_gini_coefficient = calculate_income_gini_coefficient(agents)
        wealth_gini_coefficient = calculate_wealth_gini_coefficient(agents)
        print("Income Gini Coefficient:", income_gini_coefficient)
        print("Wealth Gini Coefficient:", wealth_gini_coefficient)

        # Update the assignment with the function call
        redistribute(agents, tax_cutoff_percentage, uniform_tax_distribution)


    # Print the counts of each agent type
    # agent_counts = env.count_agents_by_type()
    # print("Agent Counts:", agent_counts)

pygame.quit()
