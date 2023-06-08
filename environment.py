import random, string

from agent import Agent
from target import Target

class Environment:
    def __init__(self, grid_x, grid_y, num_resources, resource_size, num_traps, num_agents, agent_fuel_low_range,
                 agent_fuel_high_range, view_range, death_rate, birth_rate, generation_period, inhertiance_type):
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
        self.inhertiance_type = inhertiance_type
        self.time = 0
        self.agents = []
        self.targets = []
        self.agent_id_counter = 0  # Counter to track the unique IDs of agents

    def generate_agents(self):
        # Generate new instances of the Agent class with unique IDs and random spawn coordinates
        for _ in range(self.num_agents):
            agent_id = self.get_unique_agent_id()
            x = random.randint(0, self.grid_x - 1)
            y = random.randint(0, self.grid_y - 1)
            fuel = random.randint(self.agent_fuel_low_range, self.agent_fuel_high_range)
            agent = Agent(agent_id, x, y, self.time, fuel, self)
            self.agents.append(agent)

    def get_unique_agent_id(self):
        # Generate a unique agent ID using a combination of letters and numbers
        agent_id_length = 3  # Define the length of the agent ID
        characters = string.ascii_uppercase + string.digits  # Use uppercase letters and digits
        agent_id = ''.join(random.choices(characters, k=agent_id_length))
        while agent_id in [agent.agent_id for agent in self.agents]:
            agent_id = ''.join(random.choices(characters, k=agent_id_length))
        return agent_id

    def generate_targets(self):
        # Generate instances of the Target class
        for _ in range(self.num_resources):
            x = random.randint(0, self.grid_x - 1)
            y = random.randint(0, self.grid_y - 1)
            size = self.resource_size
            target = Target(x, y, is_resource=True, size=size)
            self.targets.append(target)

        for _ in range(self.num_traps):
            x = random.randint(0, self.grid_x - 1)
            y = random.randint(0, self.grid_y - 1)
            target = Target(x, y, is_resource=False)
            self.targets.append(target)
