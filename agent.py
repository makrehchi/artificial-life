import random
from math import sqrt

class Agent:
    def __init__(self, agent_id, x, y, birth_time, fuel, environment):
        self.agent_id = agent_id
        self.x = x
        self.y = y
        self.birth_time = birth_time
        self.death_time = 0
        self.fuel = fuel
        self.environment = environment
        self.target_in_sight = []
        self.is_dead = False

    def move_randomly(self):
        self.update_targets_in_sight()  # Update targets in sight before moving

        if self.target_in_sight:
            self.move_towards_target()
        else:
            direction = random.choice(['up', 'down', 'left', 'right'])

            if direction == 'up':
                new_y = self.y - 1
                if self.can_move(self.x, new_y):
                    self.y = new_y
            elif direction == 'down':
                new_y = self.y + 1
                if self.can_move(self.x, new_y):
                    self.y = new_y
            elif direction == 'left':
                new_x = self.x - 1
                if self.can_move(new_x, self.y):
                    self.x = new_x
            elif direction == 'right':
                new_x = self.x + 1
                if self.can_move(new_x, self.y):
                    self.x = new_x

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
                self.target_in_sight.append(target)

    def is_in_range(self, target_x, target_y):
        distance = sqrt((self.x - target_x) ** 2 + (self.y - target_y) ** 2)
        return distance <= self.environment.view_range

    def move_towards_target(self):
        target = random.choice(self.target_in_sight)
        target_x = target.x
        target_y = target.y

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
    
    def collect_fuel(self):
        # Check if there is a resource/target on the current block
        for target in self.environment.targets:
            if self.x == target.x and self.y == target.y and target.is_resource:
                print("Agent", self.agent_id, "collected", target.size, "fuel from resource at", self.x, self.y)
                # Collect fuel from the resource
                self.fuel += target.size
                # Remove the resource from the environment
                self.environment.targets.remove(target)
                break