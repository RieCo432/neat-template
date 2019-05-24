from network import Network
from datetime import datetime
from os import path
import json
from copy import deepcopy
from node import Node
from connection import Connection
from random import uniform


class Population:
    # contains population

    def __init__(self, input_nodes=0, output_nodes=0, bias_node=False, init_random_connections=0, filename="None", population_size=300, num_of_bests=1):
        self.all_networks = []
        self.generation = 1
        self.best_fitness = 0
        self.max_fitness_indexs = [0]
        self.fitness_sum = 0
        self.input_nodes = input_nodes
        self.output_nodes = output_nodes
        self.bias_node = bias_node
        self.population_size = population_size
        self.max_fitnesses = [0] * num_of_bests
        self.best_networks_indexes = []
        self.num_of_bests = num_of_bests

        if filename is "None":  # set filename based on if specified or not
            date = datetime.now()
            self.filename = "population%d-%d-%d-%d-%d-%d.json" % (date.year, date.month, date.day, date.hour, date.minute, date.second)
        else:
            self.filename = filename

        if path.isfile(self.filename):  # if file exists, load from file
            with open(self.filename, "r") as fin:
                population_dict = json.load(fin)

                self.generation = population_dict["gen"]
                self.population_size = population_dict["size"]
                nets = deepcopy(population_dict["nets"])
                self.input_nodes = population_dict["input_nodes"]
                self.output_nodes = population_dict["output_nodes"]
                self.bias_node = population_dict["bias_node"] == "True"
                self.num_of_bests = population_dict["num_of_bests"]
                for net in nets:
                    import_net = Network(population_dict["input_nodes"], population_dict["output_nodes"], bias_node=population_dict["bias_node"] == "True")
                    import_nodes = []
                    for node in net["nodes"]:
                        import_node = Node()
                        import_node.layer = node["layer"]
                        import_node.connections = node["connections"]
                        import_nodes.append(import_node)
                    import_connections = []
                    for connection in net["connections"]:
                        import_connection = Connection(connection["from"], connection["to"], connection["weight"], connection["conn_num"])
                        if connection["active"] == "False":
                            import_connection.active = False
                        import_connections.append(import_connection)
                    import_net.all_connections = deepcopy(import_connections)
                    import_net.all_nodes = deepcopy(import_nodes)
                    self.all_networks.append(import_net)

        else:
            for i in range(self.population_size):
                self.all_networks.append(Network(input_nodes, output_nodes, bias_node=bias_node, init_random_connections=init_random_connections))

    def set_best_networks(self):

        self.max_fitnesses = [0] * self.num_of_bests
        self.best_networks_indexes = []

        for i in range(0, len(self.all_networks)):
            if self.all_networks[i].fitness > self.max_fitnesses[0]:
                self.max_fitnesses.append(self.all_networks[i].fitness)
                self.max_fitnesses.sort()
                self.max_fitnesses.pop(0)

        self.best_fitness = self.max_fitnesses[0]

        for i in range(0, len(self.all_networks)):
            if self.all_networks[i].fitness in self.max_fitnesses:
                self.best_networks_indexes.append(i)
                self.all_networks[i].is_best = True

    def generate_offspring(self):
        new_nets = []
        self.generation += 1

        for i in range(self.population_size):
            new_nets.append(Network(self.input_nodes, self.output_nodes, bias_node=self.bias_node))

        for i in range(self.num_of_bests):
            new_nets[i].all_nodes = deepcopy(self.all_networks[self.max_fitness_indexs[i]].all_nodes)
            new_nets[i].all_connections = deepcopy(self.all_networks[self.max_fitness_indexs[i]].all_connections)
            new_nets[i].is_best = True

        self.fitness_sum = 0
        for net in self.all_networks:
            self.fitness_sum += net.fitness

        for i in range(self.num_of_bests, self.population_size):
            parent = self.select_parent()
            new_nets[i].all_nodes = deepcopy(self.all_networks[parent].all_nodes)
            new_nets[i].all_connections = deepcopy(self.all_networks[parent].all_connections)
            new_nets[i].is_best = False

        self.all_networks = deepcopy(new_nets)

        for i in range(self.num_of_bests, self.population_size):
            self.all_networks[i].mutate()

    def select_parent(self):
        rand = uniform(0, self.fitness_sum)
        running_sum = 0
        for i in range(0, len(self.all_networks)):
            running_sum += self.all_networks[i].fitness
            if running_sum >= rand:
                return i

    def save_to_file(self):
        population_dict = {"gen": self.generation, "input_nodes": self.input_nodes, "output_nodes": self.output_nodes, "size": self.population_size, "bias_node": self.bias_node, "num_of_bests": self.num_of_bests, "nets": []}
        for net in self.all_networks:
            nodes = []
            if self.bias_node:
                last_layer = net.all_nodes[self.input_nodes + 1].layer
            else:
                last_layer = net.all_nodes[self.input_nodes].layer
            for node in net.all_nodes:
                nodes.append({"layer": node.layer, "connections": node.connections})
            connections = []
            for connection in net.all_connections:
                connections.append({"from": connection.from_node, "to": connection.to_node, "weight": connection.weight, "conn_num": connection.conn_num, "active": str(connection.active)})
            final_net_dict = {"last_layer": last_layer, "nodes": nodes, "connections": connections}
            population_dict["nets"].append(final_net_dict)

        with open(self.filename, "w") as fout:
            json.dump(population_dict, fout)
