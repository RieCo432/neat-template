from math import e


class Node:

    # Contains a basic Node class. Nodes can be either input, output or hidden nodes

    def __init__(self):

        self.input_sum = 0.0  # sum of all the values that feed into the node
        self.output_value = 0.0  # final output value, after sigmoid has been applied
        self.layer = 0  # determines what layer the node belongs to
        self.connections = []  # contains a list of connections that start at this node

    def activate(self):

        self.output_value = Node.sigmoid(self.input_sum)

    @staticmethod
    def sigmoid(x):
        return 2 / (1 + e**(-4.9 * x)) - 1
