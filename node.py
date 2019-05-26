from math import e
from config import ActivationFunctions

class Node:

    # Contains a basic Node class. Nodes can be either input, output or hidden nodes

    def __init__(self):

        self.input_sum = 0.0  # sum of all the values that feed into the node
        self.output_value = 0.0  # final output value, after sigmoid has been applied
        self.layer = 0  # determines what layer the node belongs to
        self.connections = []  # contains a list of connections that start at this node

    def activate(self, func, sigmoid_fact=-4.9):

        if func == ActivationFunctions.sigmoid:
            self.output_value = Node.sigmoid(self.input_sum, sigmoid_fact)
        elif func == ActivationFunctions.step:
            if self.input_sum < 0:
                self.output_value = 0
            else:
                self.output_value = 1

    @staticmethod
    def sigmoid(x, fact):
        return 2 / (1 + e**(fact * x)) - 1
