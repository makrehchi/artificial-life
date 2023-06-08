import random

class Agent:
    def __init__(self, agent_id, x, y, birth_time, fuel, environment):
        self.agent_id = agent_id
        self.x = x
        self.y = y
        self.birth_time = birth_time
        self.death_time = 0
        self.fuel = fuel
        self.environment = environment
        self.target_in_sight = None

    def move_randomly(self):
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
            if agent.x == x and agent.y == y:
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