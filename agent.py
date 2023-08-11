import random
from math import sqrt

class Agent:
    #
    # The Agent class is responsible for the agent's movement, fuel, age, intelligence, morality, will, and resource class.
    #
    def __init__(self, agent_id, x, y, birth_time, fuel, age, max_age, intelligence, morality, will, resource_class, energy, waste, fat, environment):
        self.agent_id = agent_id
        self.x = x
        self.y = y
        self.birth_time = birth_time
        self.death_time = 0
        self.fuel = fuel
        self.age = age
        self.max_age = max_age
        self.intelligence = intelligence
        self.energy = energy
        self.waste = waste
        self.fat = fat
        self.is_ill = False
        self.environment = environment
        self.target_in_sight = []
        self.is_dead = False
        self.morality = morality
        self.will = will
        self.is_trapped = False
        self.trap_cost = 0  # Initialize trap_cost to 0
        self.resource_class = resource_class
        self.income_collected = 0
        self.movement_counter = 0
        self.quadrant = 0
        self.attacked = False
        self.attacker = False
        self.attack_count = 0
    

    #
    # The following methods are used to determine the agent's movement.
    # 

    # Move agent towards the quarter with the most targets
    def move_towards_quarter(self, target_quarter):
        # Determine the target quarter
        if target_quarter == 1:
            x_range = range(self.environment.grid_x // 2)
            y_range = range(self.environment.grid_y // 2)
        elif target_quarter == 2:
            x_range = range(self.environment.grid_x // 2, self.environment.grid_x)
            y_range = range(self.environment.grid_y // 2)
        elif target_quarter == 3:
            x_range = range(self.environment.grid_x // 2)
            y_range = range(self.environment.grid_y // 2, self.environment.grid_y)
        elif target_quarter == 4:
            x_range = range(self.environment.grid_x // 2, self.environment.grid_x)
            y_range = range(self.environment.grid_y // 2, self.environment.grid_y)
        else:
            x_range = range(self.environment.grid_x)
            y_range = range(self.environment.grid_y)

        # Find random point in the target quarter
        target_x = random.choice(x_range)
        target_y = random.choice(y_range)

        # Move towards the target quarter by 1 unit
        if self.x < target_x:
            new_x = self.x + 1
            if self.can_move(new_x, self.y):
                self.x = new_x
        elif self.x > target_x:
            new_x = self.x - 1
            if self.can_move(new_x, self.y):
                self.x = new_x
        if self.y < target_y:
            new_y = self.y + 1
            if self.can_move(self.x, new_y):
                self.y = new_y
        elif self.y > target_y:
            new_y = self.y - 1
            if self.can_move(self.x, new_y):
                self.y = new_y

    # Move agent randomly without a target or without moving towards the quarter with the most targets
    def move_randomly_without_target(self):

        # If the agent has a higher moral value, they will move towards quarter with lower population to possibly help trapped agents
        random_number = random.random()
        if random_number < self.morality:
            possible_moves = [(self.x + 1, self.y), (self.x - 1, self.y), (self.x, self.y + 1), (self.x, self.y - 1)]
            valid_moves = [(x, y) for (x, y) in possible_moves if self.can_move(x, y)]
            if valid_moves:
                new_x, new_y = random.choice(valid_moves)
                self.x = new_x
                self.y = new_y

        # If the agent has a lower moral value, they will move towards quarter with the most targets
        else:
            target_quarter = self.environment.get_quarter_with_max_targets()
            quarter_x, quarter_y = self.environment.get_random_point_in_quarter(target_quarter)
            self.move_towards_quarter(target_quarter)

    # Move function that is called in the main loop at each frame
    def move(self, productivity_rate):
        # Determine if the agent is fit to move
        self.become_ill()

        # If the agent has recently been attacked or has attacked, they will have a flashing effect for 15 frames
        if self.attacked or self.attacker:
            self.attack_count += 1
            if self.attack_count >= 15:
                self.attacked = False
                self.attacker = False
                self.attack_count = 0

        # If the agent is trapped, they will not be able to move
        if self.is_trapped:
            return
        
        # Update the targets that are in agents sight based on their intelligence
        self.update_targets_in_sight()

        # If the agent is in the same location as a target, they will collect the target and it will be removed from the environment
        trap_collision_targets = [target for target in self.environment.targets if not target.is_resource and self.x == target.x and self.y == target.y]
        if trap_collision_targets:
            self.is_trapped = True
            trap_target = trap_collision_targets[0]
            self.trap_cost = trap_target.size
            trap_x, trap_y = self.x, self.y
            self.environment.remove_target(trap_x, trap_y)
            return
        
        # If the agent has a low moral value and high will, they will attack other agents
        if self.environment.tolerance_rate <= ((1-self.morality)*self.will):
            other_agent = None
            for agent in self.environment.agents:

                # Check if the agent with the lower intelligence is in range and has less fuel, then an insurgency will occur
                if agent != self and agent.intelligence < self.intelligence and self.is_in_range(agent.x, agent.y) and agent.fuel > self.fuel:
                    other_agent = agent
                    break
            if other_agent:
                self.insurgency(other_agent)

        # If the agent has high moral value, then they will help trapped agents
        if random.random() <= self.morality:
            self.help_trapped_agent()

        # calculate agent speed based on their fuel and motivation
        speed = self.calculate_speed()
        if speed == 0:
            return
        self.movement_counter += 1

        # Move the agent based on their speed
        if self.movement_counter >= 1 / speed:
            self.movement_counter = 0

            # If the agent has low will, they will not move
            if random.random() <= self.will:

                # Decrement fuel for every movement and increment agent_movements_counter in order to produce more resources
                self.fuel -= 1
                self.environment.agent_movements_counter += 1 * productivity_rate

                # If a target is in sight, move towards it, otherwise move towrads quarter with most targets or randomly
                if self.target_in_sight:
                    self.move_towards_target()
                else:
                    self.move_randomly_without_target()
    
    # Check if the agent can move to the given location
    def can_move(self, x, y):
        if (
            0 <= x < self.environment.grid_x
            and 0 <= y < self.environment.grid_y
            and not self.is_occupied(x, y)
            and not self.is_barrier(x, y)
        ):
            return True
        return False
    
    # Check if the given location is occupied by another agent
    def is_occupied(self, x, y):
        for agent in self.environment.agents:
            if agent is not self and agent.x == x and agent.y == y:
                return True
        return False
    
    # Check if the given location is a barrier
    def is_barrier(self, x, y):
        for barrier in self.environment.barriers:
            if barrier[0] == x and barrier[1] == y:
                return True
        return False
    
    # Check if the agent is in the same location as a target
    def check_trap_collision(self, targets):
        for target in targets:
            if not target.is_resource and self.x == target.x and self.y == target.y:
                return True
        return False
    
    # Update the targets that are in the agent's sight based on their intelligence and resource class
    def update_targets_in_sight(self):
        self.target_in_sight = []
        for target in self.environment.targets:
            if self.is_in_range(target.x, target.y):
                if self.resource_class == 'A' or target.resource_class == self.resource_class:
                    self.target_in_sight.append(target)
                elif self.resource_class == 'B' and target.resource_class in ('B', 'C', 'D'):
                    self.target_in_sight.append(target)
                elif self.resource_class == 'C' and target.resource_class in ('C', 'D'):
                    self.target_in_sight.append(target)
                elif self.resource_class == 'D' and target.resource_class == 'D':
                    self.target_in_sight.append(target)

    # Check if the agent is in range of the given location based on their intelligence
    def is_in_range(self, target_x, target_y):
        distance = sqrt((self.x - target_x) ** 2 + (self.y - target_y) ** 2)
        return distance <= self.intelligence
    
    # Move the agent towards the closet target in their sight by 1 unit
    def move_towards_target(self):
        if not self.target_in_sight:
            return
        closest_target = self.target_in_sight[0]
        min_distance = sqrt((self.x - closest_target.x) ** 2 + (self.y - closest_target.y) ** 2)
        for target in self.target_in_sight[1:]:
            distance = sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)
            if distance < min_distance:
                closest_target = target
                min_distance = distance
        target_x = closest_target.x
        target_y = closest_target.y
        if target_x < self.x:
            new_x = self.x - 1
            if self.can_move(new_x, self.y):
                self.x = new_x
        elif target_x > self.x:
            new_x = self.x + 1
            if self.can_move(new_x, self.y):
                self.x = new_x
        if target_y < self.y:
            new_y = self.y - 1
            if self.can_move(self.x, new_y):
                self.y = new_y
        elif target_y > self.y:
            new_y = self.y + 1
            if self.can_move(self.x, new_y):
                self.y = new_y


    #
    # The following methods are used to determine the agent's behaviour outside of movement.
    #

    # If a trapped agent is in range, the agent will help them based on their morality
    def help_trapped_agent(self):
        trapped_agents_in_range = [agent for agent in self.environment.agents if agent.is_trapped and agent != self and self.is_in_range(agent.x, agent.y)]
        if trapped_agents_in_range:
            trapped_agent = trapped_agents_in_range[0]
            morality_check = random.random()
            if morality_check < self.morality:
                self.fuel -= trapped_agent.trap_cost
                trapped_agent.is_trapped = False
                trapped_agent.fuel += trapped_agent.trap_cost
            else:
                return
            
    # If the agent is in the same location as a resource, they will collect it and it will be removed from the environment
    # The agent will only collect resources that are the same class as them or lower
    # The fuel they collect will be based on their energy(metabolism) and the size of the resource
    # The resource will be removed from the environment
    def collect_fuel(self):
        for target in self.environment.targets:
            if target.x == self.x and target.y == self.y and target.is_resource:
                if self.resource_class == 'A' or target.resource_class == self.resource_class:
                    self.fuel += round(target.size * self.energy)
                    self.income_collected += round(target.size * self.energy)
                    self.environment.targets.remove(target)
                    break
                elif self.resource_class == 'B' and target.resource_class in ('B', 'C', 'D'):
                    self.fuel += round(target.size * self.energy)
                    self.income_collected += round(target.size * self.energy)
                    self.environment.targets.remove(target)
                    break
                elif self.resource_class == 'C' and target.resource_class in ('C', 'D'):
                    self.fuel += round(target.size * self.energy)
                    self.income_collected += round(target.size * self.energy)
                    self.environment.targets.remove(target)
                    break
                elif self.resource_class == 'D' and target.resource_class == 'D':
                    self.fuel += round(target.size * self.energy)
                    self.income_collected += round(target.size * self.energy)
                    self.environment.targets.remove(target)
                    break
                else:
                    break
    
    # Determine if the agent is fit enough to continue based on their fat
    def become_ill(self):
        # Determine the probability of becoming ill based on the fat level
        illness_probability = self.fat * 0.001  # Adjust the factor (0.1) as needed for desired impact
        self.is_ill = random.random() < illness_probability

    # Calculate the agents speed based on their fuel and the agent with the most fuel
    def calculate_speed(self):
        max_fuel_agent = max(self.environment.agents, key=lambda agent: agent.fuel)
        max_fuel = max_fuel_agent.fuel
        speed = (max_fuel - self.fuel) / max_fuel
        return speed
    
    # If the agent has a lower intelligence and higher fuel, they will attack the agent with higher intelligence and higher fuel
    # The attacking agent will take a random percentage of fuel from the other agent
    # The agent being attacked will also lose a random percentage of their life span
    def insurgency(self, other_agent):
        self.attacker = True
        other_agent.attacked = True
        attack_strength = random.uniform(0.1, 0.5)  # Define the attack strength range here
        fuel_loss = int(other_agent.fuel * attack_strength)
        age_reduction_percentage = random.uniform(0.1, 0.5)  # Define the age reduction range here
        age_reduction = int(other_agent.max_age * age_reduction_percentage)
        self.fuel += fuel_loss
        other_agent.fuel -= fuel_loss
        other_agent.max_age -= age_reduction
    
    # Calculate the quadrant the agent is in (used for collecting data)
    def calculate_quadrant(self):
        mid_x = self.environment.grid_x // 2
        mid_y = self.environment.grid_y // 2
        if self.x < mid_x and self.y < mid_y:
            return 1
        elif self.x >= mid_x and self.y < mid_y:
            return 2
        elif self.x < mid_x and self.y >= mid_y:
            return 3
        else:
            return 4
    