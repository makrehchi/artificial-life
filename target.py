class Target:
    def __init__(self, x, y, is_resource=True, size=0, agent_requirement=None, fuel_required=0, fuel_threshold=0):
        self.x = x
        self.y = y
        self.is_resource = is_resource
        self.size = size
        self.agent_requirement = agent_requirement
        self.fuel_required = fuel_required
        self.fuel_threshold = fuel_threshold