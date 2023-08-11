# importing libraries and modules
import pygame, random, csv, datetime
from environment import Environment
from target import Target


#
# Reading variables from a variables.txt file
#
def read_variables_from_file():
    with open("variables.txt", "r") as variables_file:
        variables = {}
        exec(variables_file.read(), variables)
        return variables
    

#
# Initializing, formating and storing variables from the variables.txt file
#
quadrant_data = {
    1: {"num_agents": [], "num_resources": []},
    2: {"num_agents": [], "num_resources": []},
    3: {"num_agents": [], "num_resources": []},
    4: {"num_agents": [], "num_resources": []},
}
variables = read_variables_from_file()
num_frames = variables.get("num_frames")
tax_frames = variables.get("tax_frames")
tax_cutoff_percentage = variables.get("tax_rate")
inheritance_tax_rate = variables.get("inheritance_tax_rate")
uniform_tax_distribution = variables.get("uniform_tax_distribution")
productivity_rate = variables.get("productivity_rate")
tolerance_rate = variables.get("tolerance_rate")
grid = variables.get("grid")
num_resources = variables.get("num_resources")
num_traps = variables.get("num_traps")
barrier_type = variables.get("barrier_type")
num_barriers = variables.get("num_barriers")
barriers = variables.get("barriers")
num_agents = variables.get("num_agents")
agent_fuel_low_range = variables.get("agent_fuel_low_range")
agent_fuel_high_range = variables.get("agent_fuel_high_range")
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
# Converting percentages to decimals
productivity_rate = productivity_rate / 100
tolerance_rate = tolerance_rate / 100
    

#
# Saving data to a csv file with a timestamp
#

# Get current date and time as a string
current_datetime = datetime.datetime.now()
date_time_str = current_datetime.strftime("%Y-%m-%d__%H-%M-%S")

# Create a file path with the current date and time
file_path = f"simulation_data/{date_time_str}.csv"

# Save data to the file
def save_data_to_file(variables, data, quadrant_data):
    filtered_variables = {key: value for key, value in variables.items() if not key.startswith("__")}
    with open(file_path, "a") as file:
        writer = csv.writer(file)
        # Write the variables to the file if they haven't been written yet
        if not variables.get("variables_saved", False):
            writer.writerow(["Variable", "Value"])
            for variable, value in filtered_variables.items():
                writer.writerow([variable, value])
            variables["variables_saved"] = True
        # Write the data header to the file if it hasn't been written yet
        if not variables.get("data_header_written", False):
            headings = list(data.keys()) + ["Quadrant 1 Agents", "Quadrant 1 Resources",
                                            "Quadrant 2 Agents", "Quadrant 2 Resources",
                                            "Quadrant 3 Agents", "Quadrant 3 Resources",
                                            "Quadrant 4 Agents", "Quadrant 4 Resources"]
            writer.writerow(headings)
            variables["data_header_written"] = True
        # Write the data to the file
        row_data = list(data.values()) + [
            quadrant_data[1]["num_agents"],
            quadrant_data[1]["num_resources"],
            quadrant_data[2]["num_agents"],
            quadrant_data[2]["num_resources"],
            quadrant_data[3]["num_agents"],
            quadrant_data[3]["num_resources"],
            quadrant_data[4]["num_agents"],
            quadrant_data[4]["num_resources"],
        ]
        # Write each frame as a row in the csv file
        writer.writerow(row_data)


#
# Calculating the Gini coefficient for income and wealth
#
def calculate_income_gini_coefficient(agents):

    # If there are no agents or all agents have no income, return "No income"
    if not agents or all(agent.income_collected == 0 for agent in agents):
        return "No income"
    
    # Calculate total income collected by all agents and sort agents by income in ascending order
    total_income_collected = sum(agent.income_collected for agent in agents)
    n = len(agents)
    agents_sorted_by_income = sorted(agents, key=lambda agent: agent.income_collected)

    # Calculate the Lorenz curve and the area under the Lorenz curve
    lorenz_curve = [sum(agent.income_collected for agent in agents_sorted_by_income[:i + 1]) / total_income_collected for i in range(n)]
    area_under_lorenz_curve = sum((lorenz_curve[i - 1] + lorenz_curve[i]) * (1 / n) for i in range(1, n))
    gini_coefficient = 1 - 2 * area_under_lorenz_curve
    return gini_coefficient

def calculate_wealth_gini_coefficient(agents):

    # Calcualte total fuel collected by all agents and sort agents by fuel in ascending order
    total_fuel = sum(agent.fuel for agent in agents)
    agents_sorted_by_wealth = sorted(agents, key=lambda agent: agent.fuel)
    fuel_data = [agent.fuel for agent in agents_sorted_by_wealth]
    n = len(fuel_data)

    # Calculate the Lorenz curve and the area under the Lorenz curve
    lorenz_curve = [sum(fuel_data[:i + 1]) / total_fuel for i in range(n)]
    area_under_lorenz_curve = sum((lorenz_curve[i - 1] + lorenz_curve[i]) * (1 / n) for i in range(1, n))
    gini_coefficient = 1 - 2 * area_under_lorenz_curve
    gini_coefficient = round((gini_coefficient + 1) / 2, 2)
    return gini_coefficient


#
# Redistributing fuel (taxation)
#

# The community fund is the total amount of fuel collected from the tax
community_fund = 0

# Calculate the total fuel collected by all agents
def calculate_total_fuel(agents):
    return sum(agent.fuel for agent in agents)

# Redistribute fuel from the top earners to the bottom earners
def redistribute(agents, tax_cutoff_percentage, uniform_tax_distribution):
    global community_fund
    total_fuel_before_tax = calculate_total_fuel(agents)

    # Calculate the total amount of fuel to be collected from the tax
    total_tax_collected = total_fuel_before_tax * (tax_cutoff_percentage / 100)
    individual_tax_amount = total_tax_collected / len(agents)

    # Collect the tax from each agent and add it to the community fund
    for agent in agents:
        tax_collected = min(individual_tax_amount, agent.fuel)
        agent.fuel -= tax_collected
        community_fund += tax_collected

    # If the tax is set to uniform distribution, redistribute the community fund equally among all agents
    if uniform_tax_distribution:
        redistribution_amount = int(community_fund // len(agents))
        for agent in agents:
            agent.fuel += redistribution_amount

    # If the tax is not set to uniform distribution, redistribute the community fund proportionally among all agents based on their income
    else:
        agents_sorted_by_income = sorted(agents, key=lambda agent: agent.income_collected)
        for i, agent in enumerate(agents_sorted_by_income):
            proportion = i / (len(agents_sorted_by_income) - 1)
            redistribution_amount = int(community_fund * proportion)
            agent.fuel += redistribution_amount


#
# Upgrading agents to a higher class
#
def upgrade_class(agents, upgrade_percentage):
    # Sort agents by income in descending order
    agents_sorted_by_income = sorted(agents, key=lambda agent: agent.income_collected, reverse=True)

    # Calculate the number of agents to be upgraded
    num_agents_to_upgrade = max(int(len(agents_sorted_by_income) * (upgrade_percentage / 100)), 1)

    # Move the top earners to the upper class
    for i in range(num_agents_to_upgrade):
        agent = agents_sorted_by_income[i]
        if agent.resource_class != 'A':
            if agent.resource_class == 'B':
                agent.resource_class = 'A'
            elif agent.resource_class == 'C':
                agent.resource_class = 'B'
            elif agent.resource_class == 'D':
                agent.resource_class = 'C'


# Initializing the simulation
pygame.init()


#
# Generating the environment
#

# If the barrier type is set to dynamic barriers, generate random barriers in the environment
if barrier_type == "dynamic":
    barriers = [(random.randint(0, grid_x - 1), random.randint(0, grid_y - 1)) for _ in range(num_barriers)]

# Generate the environment object with the specified variables
env = Environment(grid_x, grid_y, num_resources, num_traps, num_agents, agent_fuel_low_range,
                  agent_fuel_high_range, barriers, age_range_low, age_range_high, intelligence_range_low, intelligence_range_high, target_size_low, target_size_high, tolerance_rate)

# Generate agents in the environment based classes
def generate_agents_by_specified_count(num_agents_A, num_agents_B, num_agents_C, num_agents_D):
    agents = []
    agents.extend([('A', num_agents_A), ('B', num_agents_B), ('C', num_agents_C), ('D', num_agents_D)])
    for resource_class, num_agents in agents:
        for _ in range(num_agents):
            env.generate_agents(resource_class)

# Generate agents in the environment randomly if the assign_agents_randomly variable is set to True
if assign_agents_randomly:
    for _ in range(num_agents_random):
        resource_class = random.choice(['A', 'B', 'C', 'D'])
        env.generate_agents(resource_class)

# Generate agents in the environment based on the specified number of agents in each class
else:
    generate_agents_by_specified_count(num_agents_A, num_agents_B, num_agents_C, num_agents_D)

# Generate targets and traps in the environment
env.generate_targets()
env.generate_traps()

# Initializing variables for the simulation
total_redistributed_fuel = 0
agents = env.agents
targets = env.targets

# Initializing the pygame window
scaled_grid_x = grid_x * 7
scaled_grid_y = grid_y * 7
clock = pygame.time.Clock()
screen = pygame.display.set_mode((scaled_grid_x, scaled_grid_y))
pygame.display.set_caption("Grid Simulation")

# Mapping keys to quadrants for generating targets
key_to_quadrant = {
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
}

# Initializing colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 150, 0)
GRAY = (169, 169, 169)
BLUE = (0, 0, 255)

# Running the simulation
running = True
while running:
    quadrant_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    
    # Checking for events
    for event in pygame.event.get():
        # Quitting the simulation if the user closes the window
        if event.type == pygame.QUIT:
            running = False
        
        # Generating targets if the user presses a number key from 1 to 4
        elif event.type == pygame.KEYDOWN:
            quadrant = key_to_quadrant.get(event.key)
            if quadrant is not None:
                x, y = env.get_random_point_in_quarter(quadrant)
                size = random.randint(env.target_size_low, env.target_size_high)
                resource_class = random.choice(['A', 'B', 'C', 'D'])
                target = Target(x, y, is_resource=True, size=size, resource_class=resource_class)
                env.targets.append(target)

    # Decrementing the number of frames left to run and quitting the simulation if there are no more frames left to run
    num_frames -= 1
    if num_frames <= 0:
        running = False

    # Setting the background color to white
    screen.fill(WHITE)

    # Moving agents and checking for collisions with targets
    for agent in agents:
        if agent.check_trap_collision(env.targets):
            agent.is_trapped = True
            agent.move(productivity_rate)
            trap_x, trap_y = agent.x, agent.y
            env.remove_target(trap_x, trap_y)
        else:
            agent.move(productivity_rate)

        # incrementing the agent's age and collecting fuel
        agent.age += 1
        agent.collect_fuel()

        # Checking for fuel depletion, age, and illness and removing the agent if any of these conditions are met
        if (agent.fuel <= 0) or (agent.age >= agent.max_age) or (agent.is_ill):
            agent.death_time = time
            if agent in agents:
                agents.remove(agent)

            # If the new agent has fuel below 20, it will recieve a boost of 60 fuel
            if agent.fuel <= 20:
                agent.fuel += 60
            
            # If the agent dies, it will pay an inheritance tax for its fuel and the tax will be added to the community fund
            else:
                interhitance_tax = (agent.fuel*(inheritance_tax_rate/100))
                agent.fuel = agent.fuel - interhitance_tax
                community_fund += interhitance_tax

            # Generate a new agent with only the same fuel attribute as the dead agent
            env.generate_single_agent(agent.fuel)

    # Generating new targets based on the agent's movements
    if random.random() <= 0.1:
        if env.agent_movements_counter > agent_fuel_low_range:
            env_agent_movements_counter = round(env.agent_movements_counter)
            env.generate_single_target(env.agent_movements_counter)
            env.agent_movements_counter = 0

    # Calculating and storing the gini coefficient for income and wealth
    income_gini_coefficient = calculate_income_gini_coefficient(agents)
    wealth_gini_coefficient = calculate_wealth_gini_coefficient(agents)

    # Drawing the barriers, targets and agents in the pygame window
    # Barriers set to be gray squares
    for barrier_cell in barriers:
        pygame.draw.rect(screen, GRAY, (barrier_cell[0] * 7, barrier_cell[1] * 7, 7, 7))

    # Resources set to be green letters based on class and traps set to be red letter T
    for target in targets:
        target_pos = (target.x * 7 + 3, target.y * 7 + 3)
        target_radius = 3
        if target.is_resource:
            font = pygame.font.Font(None, 16)
            text_surface = font.render(target.resource_class, True, GREEN)
            text_rect = text_surface.get_rect(center=target_pos)
            screen.blit(text_surface, text_rect)
        else:
            font = pygame.font.Font(None, 16)
            text_surface = font.render('T', True, RED)
            text_rect = text_surface.get_rect(center=target_pos)
            screen.blit(text_surface, text_rect)

    # Agents set to be black letter based on class
    for agent in agents:
        font = pygame.font.Font(None, 16)
        text_surface = font.render(agent.resource_class, True, BLACK)
        text_rect = text_surface.get_rect(center=(agent.x * 7 + 3, agent.y * 7 + 3))

        # Draw a blue circle around agents that have been attacked
        if agent.attacked:
            pygame.draw.circle(screen, BLUE, (agent.x * 7 + 3, agent.y * 7 + 3), 15, 2)

        # Draw a red circle around agents that is the attacker
        if agent.attacker:
            pygame.draw.circle(screen, RED, (agent.x * 7 + 3, agent.y * 7 + 3), 15, 2)
        screen.blit(text_surface, text_rect)
        
    # Updating the pygame window
    pygame.display.flip()
    clock.tick(40)

    # Incrementing the time and the environment's time
    time += 1
    env.time += 1

    # Redistributing fuel and upgrading agents every tax_frames
    if time % tax_frames == 0:
        redistribute(agents, tax_cutoff_percentage, uniform_tax_distribution)
        # 10 means that only top 10% of earners will become a class higher
        upgrade_class(agents, 10)
    

    #
    # Calculating and storing data for each frame of the simulation into a csv file
    #

    # Initializing variables for the data
    total_fuel = 0
    total_morality = 0
    total_intelligence = 0
    total_age = 0
    total_will = 0
    total_age = 0
    trapped_agents = 0
    num_agents_A = 0
    num_agents_B = 0
    num_agents_C = 0
    num_agents_D = 0
    num_resources_A = 0
    num_resources_B = 0
    num_resources_C = 0
    num_resources_D = 0

    # Calculating the total fuel, morality, intelligence, age, will, age, number of trapped agents and number of agents and resources in each class
    for agent in agents:
        total_fuel += agent.fuel
        total_morality += agent.morality
        total_intelligence += agent.intelligence
        total_age += agent.age
        total_will += agent.will
        total_age += agent.age
        if agent.is_trapped:
            trapped_agents += 1
        grid_x, grid_y = env.grid_size
        quadrant_num = env.get_quadrant_number(agent.x, agent.y, grid_x, grid_y)
        quadrant_counts[quadrant_num] += 1
        if agent.resource_class == 'A':
            num_agents_A += 1
        elif agent.resource_class == 'B':
            num_agents_B += 1
        elif agent.resource_class == 'C':
            num_agents_C += 1
        elif agent.resource_class == 'D':
            num_agents_D += 1
    for target in targets:
        if target.is_resource:
            if target.resource_class == 'A':
                num_resources_A += 1
            elif target.resource_class == 'B':
                num_resources_B += 1
            elif target.resource_class == 'C':
                num_resources_C += 1
            elif target.resource_class == 'D':
                num_resources_D += 1

    # Calculating the average fuel, morality, intelligence, age, will and age
    average_fuel = round(total_fuel / len(agents), 2)
    average_morality = round(total_morality / len(agents), 2)
    average_intelligence = round(total_intelligence / len(agents), 2)
    average_age = round(total_age / len(agents), 2)
    average_will = round(total_will / len(agents), 2)
    average_age = round(total_age / len(agents), 2)

    # Storing the data for each frame of the simulation with the corresponding variable name
    for quadrant_num, num_agents in quadrant_counts.items():
        quadrant_data[quadrant_num]["num_agents"] = num_agents
        quadrant_data[quadrant_num]["num_resources"] = env.count_resources_in_quadrant(quadrant_num)
    data = {
        "Time": time,
        "Income Gini Coefficient": income_gini_coefficient,
        "Wealth Gini Coefficient": wealth_gini_coefficient,
        "Average Fuel": average_fuel,
        "Average Morality": average_morality,
        "Average Intelligence": average_intelligence,
        "Average Age": average_age,
        "Average Will": average_will,
        "Average Age": average_age,
        "Trapped Agents": trapped_agents,
        "Number of Agents A": num_agents_A,
        "Number of Agents B": num_agents_B,
        "Number of Agents C": num_agents_C,
        "Number of Agents D": num_agents_D,
        "Number of Resources A": num_resources_A,
        "Number of Resources B": num_resources_B,
        "Number of Resources C": num_resources_C,
        "Number of Resources D": num_resources_D,
    }

    # Saving the data to a csv file
    save_data_to_file(variables, data, quadrant_data)


# Quitting the simulation
pygame.quit()