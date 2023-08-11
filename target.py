class Target:
    #
    # The target class is responsible for keeping track of the target's location, size, and whether it is a resource or a trap.
    #
    def __init__(self, x, y, is_resource=True, size=0, agent_requirement=None, fuel_required=0, fuel_threshold=0, resource_class=None):
        self.x = x
        self.y = y
        self.is_resource = is_resource
        self.size = size
        self.resource_class = resource_class