class Target:
    def __init__(self, x, y, is_resource=True, size=None):
        self.x = x
        self.y = y
        self.is_resource = is_resource
        self.size = size