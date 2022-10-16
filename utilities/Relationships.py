class Relationship:
    def __init__(self, from_node, to_node, r_type, lag):
        self.from_node = from_node
        self.to_node = to_node
        self.r_type = r_type
        self.lag = lag

    def __str__(self):
        return self.from_node.label + ',' + self.to_node.label + ',' + self.r_type + ',' + self.lag
