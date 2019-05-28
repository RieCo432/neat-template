class Connection:

    # simple connection class. A connection takes the output value of the from_node, multiplies it by the weight and
    # then adds it to the to_node's input sum

    def __init__(self, from_node, to_node, weight, conn_num):
        self.from_node = from_node  # node from which it takes the output value
        self.to_node = to_node  # node which takes the final result
        self.weight = weight  # weight that is applied to the value of the from_node
        self.conn_num = conn_num  # index number of the connection in the list of all connections
        self.active = True  # determines whether a connection is active or not. Deleted connections stay in the
        # network's connections list so that indexes don't get messed up, however those connections must not be used

    def __str__(self):
        # returns a string with the connection's properties for debugging purposes
        return "conn %d, from %d to %d weight %f" % (self.conn_num, self.from_node, self.to_node, self.weight)
