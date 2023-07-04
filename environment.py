import random
import string

from agent import Agent
from target import Target

class Environment:
    def __init__(self, grid_x, grid_y, num_resources, resource_size, num_traps, num_agents, agent_fuel_low_range,
                 agent_fuel_high_range, view_range, generation_period, barriers, age_range_low, age_range_high):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.num_resources = num_resources
        self.resource_size = resource_size
        self.num_traps = num_traps
        self.num_agents = num_agents
        self.agent_fuel_low_range = agent_fuel_low_range
        self.agent_fuel_high_range = agent_fuel_high_range
        self.view_range = view_range
        self.generation_period = generation_period
        self.time = 0
        self.agents = []
        self.targets = []
        self.agent_id_counter = 0  # Counter to track the unique IDs of agents
        self.barriers = barriers
        self.age_range_low = age_range_low
        self.age_range_high = age_range_high


    def generate_agents(self):
        # Generate new instances of the Agent class with unique IDs and random spawn coordinates
        for _ in range(self.num_agents):
            agent_id = self.get_unique_agent_id()
            x = random.randint(0, self.grid_x - 1)
            y = random.randint(0, self.grid_y - 1)
            fuel = random.randint(self.agent_fuel_low_range, self.agent_fuel_high_range)
            age = 0
            max_age = random.randint(self.age_range_low, self.age_range_high)  # Assign a random maximum age above the current age
            agent = Agent(agent_id, x, y, self.time, fuel, age, max_age, self)
            self.agents.append(agent)
            agent.birth_time = self.time

    def generate_single_agent(self, fuel):
        agent_id = self.get_unique_agent_id()
        x = random.randint(0, self.grid_x - 1)
        y = random.randint(0, self.grid_y - 1)
        fuel = fuel
        age = 0
        max_age = random.randint(self.age_range_low, self.age_range_low)
        agent = Agent(agent_id, x, y, self.time, fuel, age, max_age, self)
        self.agents.append(agent)
        agent.birth_time = self.time
        print("new agent born at time: ", self.time, ", with age: ", age, " and fuel: ", fuel, " and max age: ", max_age)


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
            size = self.resource_size
            target = Target(x, y, is_resource=True, size=size)
            self.targets.append(target)

        for _ in range(self.num_traps):
            x, y = self.get_valid_target_coordinates()
            target = Target(x, y, is_resource=False)
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
