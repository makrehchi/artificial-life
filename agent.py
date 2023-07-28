import random
from math import sqrt

class Agent:
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
        self.resources_collected = 0
        self.income_collected = 0
        self.movement_counter = 0

    def move_towards_quarter(self, target_quarter):
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

        target_x = random.choice(x_range)
        target_y = random.choice(y_range)

        # Move towards the randomly selected target point
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

    def move_randomly(self):
        self.become_ill()
        if self.is_trapped:
            return
        self.update_targets_in_sight()

        # Check for trap collision
        trap_collision_targets = [target for target in self.environment.targets if not target.is_resource and self.x == target.x and self.y == target.y]
        if trap_collision_targets:
            # If the agent collides with a trap, set is_trapped to True, remove the trap from the environment,
            # and set trap_cost to the target_size of the trap that they collided with.
            self.is_trapped = True
            trap_target = trap_collision_targets[0]  # Assuming only one trap can be present at a location
            self.trap_cost = trap_target.size
            trap_x, trap_y = self.x, self.y
            self.environment.remove_target(trap_x, trap_y)  # Remove the trap from the environment.
            return  # The agent cannot move if it's trapped.


        if random.random() <= self.morality:
            self.help_trapped_agent()

        # Get the agent's speed based on their fuel
        speed = self.calculate_speed()

        # Check if speed is zero to avoid division by zero
        if speed == 0:
            return

        # Increment the movement counter
        self.movement_counter += 1

        # Check if the agent should move based on the current speed and movement counter
        if self.movement_counter >= 1 / speed:
            # Reset the movement counter
            self.movement_counter = 0
            if random.random() <= self.will:
                self.fuel -= 1
                if self.target_in_sight:
                    self.move_towards_target()
                else:
                    self.move_randomly_without_target()

    def move_randomly_without_target(self):
        random_number = random.random()
        if random_number < self.morality:
            # move randomly if morality is greater than random number
            possible_moves = [(self.x + 1, self.y), (self.x - 1, self.y), (self.x, self.y + 1), (self.x, self.y - 1)]
            valid_moves = [(x, y) for (x, y) in possible_moves if self.can_move(x, y)]
            if valid_moves:
                new_x, new_y = random.choice(valid_moves)
                self.x = new_x
                self.y = new_y
        else:
            target_quarter = self.environment.get_quarter_with_max_targets()
            quarter_x, quarter_y = self.environment.get_random_point_in_quarter(target_quarter)
            self.move_towards_quarter(target_quarter)

    def can_move(self, x, y):
        if (
            0 <= x < self.environment.grid_x
            and 0 <= y < self.environment.grid_y
            and not self.is_occupied(x, y)
            and not self.is_barrier(x, y)
        ):
            return True
        return False

    def is_occupied(self, x, y):
        for agent in self.environment.agents:
            if agent is not self and agent.x == x and agent.y == y:
                return True
        return False

    def is_barrier(self, x, y):
        for barrier in self.environment.barriers:
            if barrier[0] == x and barrier[1] == y:
                return True
        return False

    def check_trap_collision(self, targets):
        for target in targets:
            if not target.is_resource and self.x == target.x and self.y == target.y:
                return True
        return False

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

    def is_in_range(self, target_x, target_y):
        distance = sqrt((self.x - target_x) ** 2 + (self.y - target_y) ** 2)
        return distance <= self.intelligence

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

    def help_trapped_agent(self):
        # Check if the agent sees another trapped agent in their view range and helps them based on their morality
        trapped_agents_in_range = [agent for agent in self.environment.agents if agent.is_trapped and agent != self and self.is_in_range(agent.x, agent.y)]
        if trapped_agents_in_range:
            trapped_agent = trapped_agents_in_range[0]  # Assuming only one trapped agent can be in the view range
            morality_check = random.random()
            if morality_check < self.morality:
                self.fuel -= trapped_agent.trap_cost
                trapped_agent.is_trapped = False
                trapped_agent.fuel += trapped_agent.trap_cost
            else:
                return

    def collect_fuel(self):
        # Check if there is a resource on the agent's current block
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
                    # elf.resources_collected += 1
                    # if self.resources_collected >= 10:
                    #     self.resources_collected = 0
                    #     self.resource_class = 'A'
                    self.environment.targets.remove(target)
                    break
                elif self.resource_class == 'C' and target.resource_class in ('C', 'D'):
                    self.fuel += round(target.size * self.energy)
                    self.income_collected += round(target.size * self.energy)
                    # self.resources_collected += 1
                    # if self.resources_collected >= 10:
                    #     self.resources_collected = 0
                    #     self.resource_class = 'B'
                    self.environment.targets.remove(target)
                    break
                elif self.resource_class == 'D' and target.resource_class == 'D':
                    self.fuel += round(target.size * self.energy)
                    self.income_collected += round(target.size * self.energy)
                    # self.resources_collected += 1
                    # if self.resources_collected >= 10:
                    #     self.resources_collected = 0
                    #     self.resource_class = 'C'
                    self.environment.targets.remove(target)
                    break
                else:
                    break

    def become_ill(self):
        # Determine the probability of becoming ill based on the fat level
        illness_probability = self.fat * 0.001  # Adjust the factor (0.1) as needed for desired impact
        self.is_ill = random.random() < illness_probability

    def calculate_speed(self):
        max_fuel_agent = max(self.environment.agents, key=lambda agent: agent.fuel)
        max_fuel = max_fuel_agent.fuel

        speed = (max_fuel - self.fuel) / max_fuel
        return speed