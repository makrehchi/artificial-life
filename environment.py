import random
import string

from agent import Agent
from target import Target

class Environment:
    def __init__(self, grid_x, grid_y, num_resources, num_traps, num_agents, agent_fuel_low_range,
                 agent_fuel_high_range, generation_period, barriers, age_range_low, age_range_high, intelligence_range_low, intelligence_range_high, target_size_low, target_size_high):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.num_resources = num_resources
        self.num_traps = num_traps
        self.num_agents = num_agents
        self.agent_fuel_low_range = agent_fuel_low_range
        self.agent_fuel_high_range = agent_fuel_high_range
        self.generation_period = generation_period
        self.time = 0
        self.agents = []
        self.targets = []
        self.agent_id_counter = 0  # Counter to track the unique IDs of agents
        self.barriers = barriers
        self.age_range_low = age_range_low
        self.age_range_high = age_range_high
        self.intelligence_range_low = intelligence_range_low
        self.intelligence_range_high = intelligence_range_high
        self.target_size_low = target_size_low
        self.target_size_high = target_size_high
        self.total_fuel = sum(agent.fuel for agent in self.agents)

    def get_quarter_with_max_targets(self):
        quarter_counts = [0, 0, 0, 0]
        mid_x = self.grid_x // 2
        mid_y = self.grid_y // 2

        for target in self.targets:
            x = target.x
            y = target.y
            if x < mid_x and y < mid_y:
                quarter_counts[0] += 1
            elif x >= mid_x and y < mid_y:
                quarter_counts[1] += 1
            elif x < mid_x and y >= mid_y:
                quarter_counts[2] += 1
            else:
                quarter_counts[3] += 1

        if all(count == 0 for count in quarter_counts):
            max_quarter = 0
        else:
            max_quarter = quarter_counts.index(max(quarter_counts)) + 1
        return max_quarter

    def get_random_point_in_quarter(self, quarter):
        mid_x = self.grid_x // 2
        mid_y = self.grid_y // 2

        if quarter == 1:
            x = random.randint(0, mid_x - 1)
            y = random.randint(0, mid_y - 1)
        elif quarter == 2:
            x = random.randint(mid_x, self.grid_x - 1)
            y = random.randint(0, mid_y - 1)
        elif quarter == 3:
            x = random.randint(0, mid_x - 1)
            y = random.randint(mid_y, self.grid_y - 1)
        else:
            x = random.randint(mid_x, self.grid_x - 1)
            y = random.randint(mid_y, self.grid_y - 1)

        return x, y

    def generate_agents(self, resource_class):
        agent_id = self.get_unique_agent_id()
        x = random.randint(0, self.grid_x - 1)
        y = random.randint(0, self.grid_y - 1)
        age = 0
        fuel = random.randint(self.agent_fuel_low_range, self.agent_fuel_high_range)
        max_age = random.randint(self.age_range_low, self.age_range_high)
        morality = random.uniform(0, 1)
        intelligence = random.randint(self.intelligence_range_low, self.intelligence_range_high)

        energy = random.uniform(0, 1)
        waste = random.uniform(0, 1 - energy)
        fat = 1 - (energy + waste)
        factors = [energy, waste, fat]
        random.shuffle(factors)
        energy, waste, fat = factors

        agent = Agent(agent_id, x, y, self.time, fuel, age, max_age, intelligence, morality, resource_class, energy, waste, fat, self)
        self.agents.append(agent)
        agent.birth_time = self.time

    def generate_single_agent(self, fuel):
        agent_id = self.get_unique_agent_id()
        x = random.randint(0, self.grid_x - 1)
        y = random.randint(0, self.grid_y - 1)
        age = 0
        max_age = random.randint(self.age_range_low, self.age_range_high)
        intelligence = random.randint(self.intelligence_range_low, self.intelligence_range_high)
        morality = random.uniform(0, 1)
        resource_class = random.choice(['A', 'B', 'C', 'D'])

        energy = random.uniform(0, 1)
        waste = random.uniform(0, 1 - energy)
        fat = 1 - (energy + waste)
        factors = [energy, waste, fat]
        random.shuffle(factors)
        energy, waste, fat = factors

        agent = Agent(agent_id, x, y, self.time, fuel, age, max_age, intelligence, morality, resource_class, energy, waste, fat, self)
        self.agents.append(agent)
        agent.birth_time = self.time

    def get_unique_agent_id(self):
        # Generate a unique agent ID using a combination of three capital letters
        agent_id_length = 3  # Define the length of the agent ID
        characters = string.ascii_uppercase  # Use only uppercase letters
        agent_id = ''.join(random.choices(characters, k=agent_id_length))
        used_ids = [agent.agent_id for agent in self.agents if not agent.is_dead]
        while agent_id in used_ids:
            agent_id = ''.join(random.choices(characters, k=agent_id_length))
        return agent_id

    def generate_targets(self):
        # Generate instances of the Target class
        for _ in range(self.num_resources):
            x, y = self.get_valid_target_coordinates()
            size = random.randint(self.target_size_low, self.target_size_high)
            resource_class = random.choice(['A', 'B', 'C', 'D'])
            target = Target(x, y, is_resource=True, size=size, resource_class=resource_class)
            self.targets.append(target)
    
    def generate_single_target(self):
        x, y = self.get_valid_target_coordinates()
        size = random.randint(self.target_size_low, self.target_size_high)
        resource_class = random.choice(['A', 'B', 'C', 'D'])
        target = Target(x, y, is_resource=True, size=size, resource_class=resource_class)
        self.targets.append(target)

    def generate_traps(self):
        for _ in range(self.num_traps):
            x, y = self.get_valid_target_coordinates()
            size = random.randint(self.target_size_low, self.target_size_high)
            target = Target(x, y, is_resource=False, size=size)
            self.targets.append(target)

    def get_valid_target_coordinates(self):
        while True:
            x = random.randint(0, self.grid_x - 1)
            y = random.randint(0, self.grid_y - 1)
            if not self.is_barrier(x, y) and not self.is_target_at(x, y):
                return x, y

    def is_barrier(self, x, y):
        return (x, y) in self.barriers

    def is_target_at(self, x, y):
        for target in self.targets:
            if target.x == x and target.y == y:
                return True
        return False

    def remove_target(self, x, y):
        target_to_remove = None
        for target in self.targets:
            if target.x == x and target.y == y and not target.is_resource:
                target_to_remove = target
                break
        if target_to_remove:
            self.targets.remove(target_to_remove)

    def count_agents_by_type(self):
        agent_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        for agent in self.agents:
            agent_counts[agent.resource_class] += 1
        return agent_counts