from config import EvolutionParams
from node import Node
from connection import Connection
from random import randint, uniform

class Network:

    # this class holds the network, its connections, nodes, etc...

    def __init__(self, input_nodes, output_nodes, bias_node=False, init_rand_connections=0):

        self.input_nodes = input_nodes  # number of input nodes
        self.output_nodes = output_nodes  # numbe of output nodes
        self.bias_node = bias_node  # is bias node used?

        self.fitness = 0  # contains the fitness of this particular network object
        self.is_best = False  # is this the best network in the current population?
        self.fitness_boosts = []  # contains a list of values that are used to boost or decrease the fitness of a
        # network if for example it achieved a certain milestone, to enhance chance of offspring
        self.all_nodes = []  # contains list of all nodes
        self.all_connections = []  # contains list of all connections

        for i in range(self.input_nodes):  # create the desired amount of input nodes
            self.add_node(autolayer=False)
            self.all_nodes[-1].layer = 0  # set layer of new node to 0

        if self.bias_node:  # add bias node
            self.add_node(autolayer=False)
            self.all_nodes[-1].layer = 0  # bias node belongs to input nodes
            self.all_nodes[-1].output_value = 1  # bias node has a constant output value of 1

        for i in range(self.output_nodes):  # create the desired amount of output_nodes
            self.add_node(autolayer=False)
            self.all_nodes[-1].layer  = 1  # set output nodes to layer 1

        for i in range(init_rand_connections):  # generate desired amount of random connections
            self.new_random_connection()

    def add_node(self, autolayer=True, from_layer=0, to_layer=0):
        new_node = Node()  # create a new node
        if autolayer:  # if layer is chosen automatically
            if to_layer - from_layer <= 1:  # if the node is supposed to be in-between 2 adjacent layers
                for node in self.all_nodes:  # iterate over all nodes
                    if node.layer > from_layer:  # if that node is in a higher layer than new node
                        node.layer += 1  # increase its layer
            new_node.layer = from_layer + 1  # new node is positionned at a layer just above the layer from where the
            # connection it replaced originated

        self.all_nodes.append(new_node)  # append new node to the list of all nodes

    def add_connection(self, from_node, to_node, weight):
        # generate a new connection object with specified parameters (length of connections list will be index of new)
        new_connection = Connection(from_node, to_node, weight, len(self.all_connections))
        self.all_connections.append(new_connection)  # append new connection to the list of all connections
        self.all_nodes[from_node].connections.append(len(self.all_connections))  # add the index of the new connection
        # to the list of outgoing connections of the from_node

    def new_random_connection(self):

        # select 2 random nodes
        from_node = randint(0, len(self.all_nodes) - 1)
        to_node = randint(0, len(self.all_nodes) - 1)

        # check that from_node is in a lower layer than to_node and that the connection does not already exist
        while self.all_nodes[from_node].layer >= self.all_nodes[to_node].layer or self.connection_exists(from_node, to_node):
            from_node = randint(0, len(self.all_nodes) - 1)
            to_node = randint(0, len(self.all_nodes) - 1)

        # add connection between specified nodes with random weight
        self.add_connection(from_node, to_node, uniform(-1, 1))

    def connection_exists(self, from_node, to_node):
        # check if a certain connection already exists by iterating over the connection coming out of from_node
        # and checking if any of them goes to to_node
        for connection_number in self.all_nodes[from_node].connection:
            if self.all_connections[connection_number].to_node == to_node:
                return True
        return False