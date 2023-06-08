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
            if 0 <= new_y < self.environment.grid_y:
                is_occupied = any(agent.x == self.x and agent.y == new_y for agent in self.environment.agents)
                if not is_occupied:
                    self.y = new_y
        elif direction == 'down':
            new_y = self.y + 1
            if 0 <= new_y < self.environment.grid_y:
                is_occupied = any(agent.x == self.x and agent.y == new_y for agent in self.environment.agents)
                if not is_occupied:
                    self.y = new_y
        elif direction == 'left':
            new_x = self.x - 1
            if 0 <= new_x < self.environment.grid_x:
                is_occupied = any(agent.x == new_x and agent.y == self.y for agent in self.environment.agents)
                if not is_occupied:
                    self.x = new_x
        elif direction == 'right':
            new_x = self.x + 1
            if 0 <= new_x < self.environment.grid_x:
                is_occupied = any(agent.x == new_x and agent.y == self.y for agent in self.environment.agents)
                if not is_occupied:
                    self.x = new_x
    


    def check_trap_collision(self, targets):
        for target in targets:
            if not target.is_resource and self.x == target.x and self.y == target.y:
                return True
        return False