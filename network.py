from config import EvolutionParams
from node import Node
from connection import Connection
from random import randint, uniform, random
from numpy.random import normal
from config import ActivationFunctions


class Network:

    # this class holds the network, its connections, nodes, etc...

    def __init__(self, input_nodes, output_nodes, bias_node=False, init_random_connections=0):

        self.input_nodes = input_nodes  # number of input nodes
        self.output_nodes = output_nodes  # number of output nodes
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

        for i in range(init_random_connections):  # generate desired amount of random connections
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
        if not self.connection_exists(from_node, to_node):
            new_connection = Connection(from_node, to_node, weight, len(self.all_connections))
            self.all_nodes[from_node].connections.append(len(self.all_connections))  # add the index of the new
            # connection
            self.all_connections.append(new_connection)  # append new connection to the list of all connections
            # to the list of outgoing connections of the from_node

    def new_random_connection(self):

        # select 2 random nodes
        from_node = randint(0, len(self.all_nodes) - 1)
        to_node = randint(0, len(self.all_nodes) - 1)

        # check that from_node is in a lower layer than to_node and that the connection does not already exist
        iterations = 0  # to limit number of random searches. In case of a fully connected network this would result
        # in an infinite loop
        while (self.all_nodes[from_node].layer >= self.all_nodes[to_node].layer or
               self.connection_exists(from_node, to_node)) and iterations <= len(self.all_nodes)**2:
            from_node = randint(0, len(self.all_nodes) - 1)
            to_node = randint(0, len(self.all_nodes) - 1)
            iterations += 1

        # add connection between specified nodes with random weight
        if iterations < len(self.all_nodes)**2:
            self.add_connection(from_node, to_node, uniform(-1, 1))

    def connection_exists(self, from_node, to_node):
        # check if a certain connection already exists by iterating over the connection coming out of from_node
        # and checking if any of them goes to to_node
        for connection_number in self.all_nodes[from_node].connections:
            if self.all_connections[connection_number].to_node == to_node:
                return True
        return False

    def feed_forward(self, activation_function=ActivationFunctions,
                     sigmoid_factor=ActivationFunctions.default_sigmoid_fact):

        if self.bias_node:
            output_layer = self.all_nodes[self.input_nodes + 1].layer  # first output node is first node after all
            # input nodes plus bias node
        else:
            output_layer = self.all_nodes[self.input_nodes].layer  # first output node is first node after all
            # input nodes

        layers = []
        # build a list of layers, each of which contains the nodes in that layer
        for i in range(output_layer + 1):
            layers.append([])  # add a list for each layer
        for i in range(len(self.all_nodes)):
            layers[self.all_nodes[i].layer].append(i)  # add each node to the corresponding layer

        for layer in layers[:output_layer]:  # iterate over nodes layer by layer, omitting the output layer
            for node_index in layer:
                node = self.all_nodes[node_index]

                if node.layer is not 0 and node.layer is not output_layer:  # don't call activate method on output nodes
                        node.activate(activation_function, sigmoid_factor)

                if node.layer is not output_layer:  # do not feedforward output nodes
                    for connection_number in node.connections:
                        # multiply output value of node by connection weight and add it to the to_node input sum
                        connection = self.all_connections[connection_number]
                        self.all_nodes[connection.to_node].input_sum += node.output_value * connection.weight

        # finish by activating output nodes
        if self.bias_node:
            for node in self.all_nodes[self.input_nodes + 1:self.input_nodes + 1 + self.output_nodes]:
                node.activate(activation_function, sigmoid_factor)
        else:
            for node in self.all_nodes[self.input_nodes:self.input_nodes + self.output_nodes]:
                node.activate(activation_function, sigmoid_factor)

    def mutate(self):

        if random() <= EvolutionParams.mutate_weight_refine_probability and len(self.all_connections) > 0:
            # probability to change a connection weight
            connection = self.all_connections[randint(0, len(self.all_connections) - 1)]
            if not connection.active:
                connection = self.all_connections[randint(0, len(self.all_connections) - 1)]
            if random() <= EvolutionParams.mutate_new_random_weight_probability:  # probability for new random weight
                connection.weight = uniform(-1, 1)
            else:  # otherwise slightly adjust weight
                connection.weight += normal() / 50
                if connection.weight > 1:
                    connection.weight = 1
                elif connection.weight < -1:
                    connection.weight = -1

        if random() <= EvolutionParams.new_random_connection_probability:  # random new connection
            self.new_random_connection()

        if random() <= EvolutionParams.new_node_probability and len(self.all_connections) > 0:
            # select a random connection to replace by a node and 2 connections
            rand_connection_index = randint(0, len(self.all_connections) - 1)
            while not self.all_connections[rand_connection_index].active:  # make sure selected connection is active
                rand_connection_index = randint(0, len(self.all_connections) - 1)
            connection = self.all_connections[rand_connection_index]  # get the connection object
            from_node = connection.from_node  # get from_node index
            to_node = connection.to_node  # get to_node index
            self.all_nodes[from_node].connections.remove(rand_connection_index)  # remove connection index from
            # from_node connections list
            connection.active = False  # deactivate connection
            self.add_node(from_layer=self.all_nodes[from_node].layer, to_layer=self.all_nodes[to_node].layer)  # add
            # new node in middle
            self.add_connection(from_node, len(self.all_nodes) - 1, uniform(-1, 1))  # link from_node to new node
            self.add_connection(len(self.all_nodes) - 1, to_node, uniform(-1, 1))  # link new node to to_node

    def calculate_fitness(self, fitness_parameters):

        self.fitness = sum(self.fitness_boosts) + sum(fitness_parameters)

    def set_inputs(self, input_values):
        for node in self.all_nodes:  # reset input sums
            node.input_sum = 0.0
        for i in range(self.input_nodes):
            self.all_nodes[i].output_value = input_values[i]

    def get_outputs(self):
        output_values = []
        if self.bias_node:
            for output_node in self.all_nodes[self.input_nodes + 1: self.input_nodes + 1 + self.output_nodes]:
                # With bias node
                output_values.append(output_node.output_value)
        else:
            for output_node in self.all_nodes[self.input_nodes: self.input_nodes + self.output_nodes]:  # No bias node
                output_values.append(output_node.output_value)

        return output_values

