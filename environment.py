import random
import string

from agent import Agent
from target import Target

class Environment:
    def __init__(self, grid_x, grid_y, num_resources, resource_size, num_traps, num_agents, agent_fuel_low_range,
                 agent_fuel_high_range, view_range, death_rate, birth_rate, generation_period, inheritance_type, barriers, agent_specific_resource, fuel_requirement_resource, fuel_threshold_resource, fuel_required, fuel_threshold):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.num_resources = num_resources
        self.resource_size = resource_size
        self.num_traps = num_traps
        self.num_agents = num_agents
        self.agent_fuel_low_range = agent_fuel_low_range
        self.agent_fuel_high_range = agent_fuel_high_range
        self.view_range = view_range
        self.death_rate = death_rate
        self.birth_rate = birth_rate
        self.generation_period = generation_period
        self.inheritance_type = inheritance_type
        self.time = 0
        self.agents = []
        self.targets = []
        self.agent_id_counter = 0  # Counter to track the unique IDs of agents
        self.barriers = barriers
        self.agent_specific_resource = agent_specific_resource
        self.fuel_requirement_resource = fuel_requirement_resource
        self.fuel_threshold_resource = fuel_threshold_resource
        self.fuel_required = fuel_required
        self.fuel_threshold = fuel_threshold

    def generate_agents(self):
        # Generate new instances of the Agent class with unique IDs and random spawn coordinates
        for _ in range(self.num_agents):
            agent_id = self.get_unique_agent_id()
            x = random.randint(0, self.grid_x - 1)
            y = random.randint(0, self.grid_y - 1)
            fuel = random.randint(self.agent_fuel_low_range, self.agent_fuel_high_range)
            agent = Agent(agent_id, x, y, self.time, fuel, self)
            self.agents.append(agent)
            agent.birth_time = self.time

    def generate_single_agent(self):
        agent_id = self.get_unique_agent_id()
        x = random.randint(0, self.grid_x - 1)
        y = random.randint(0, self.grid_y - 1)
        fuel = random.randint(self.agent_fuel_low_range, self.agent_fuel_high_range)
        agent = Agent(agent_id, x, y, self.time, fuel, self)
        self.agents.append(agent)

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

        for agent in self.agents:
            for _ in range(self.agent_specific_resource):
                x, y = self.get_valid_target_coordinates()
                target = Target(x, y, is_resource=True, size=self.resource_size, agent_requirement=agent.agent_id)
                self.targets.append(target)

        for _ in range(self.fuel_requirement_resource):
            x, y = self.get_valid_target_coordinates()
            target = Target(x, y, is_resource=True, size=self.resource_size, fuel_required=self.fuel_required)
            self.targets.append(target)

        for _ in range(self.fuel_threshold_resource):
            x, y = self.get_valid_target_coordinates()
            target = Target(x, y, is_resource=True, size=self.resource_size, fuel_threshold=self.fuel_threshold)
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
