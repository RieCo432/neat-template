import json
from time import sleep
from datetime import datetime

import pygame
from os import environ
from sys import argv
from math import ceil

environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (1210, 30)
pygame.init()
width = 700
height = 1000
screen = pygame.display.set_mode((width, height))
screen.fill(0)


def load(old_nets):
    try:
        with open(argv[1], "r") as fin:
            nets_dict = json.load(fin)

            nets = nets_dict["nets"]
    except json.decoder.JSONDecodeError:
        nets = old_nets

    return nets


def draw_net(num, nets):

    net = nets[num]
    last_layer = net["last_layer"]

    nodes_per_layer = [0] * (last_layer + 1)
    for node in net["nodes"]:
        nodes_per_layer[node["layer"]] += 1

    nodes_in_layer = []
    for layer_num in range(last_layer + 1):
        nodes_in_layer.append([])
        for node_num in range(len(net["nodes"])):
            if net["nodes"][node_num]["layer"] == layer_num:
                nodes_in_layer[layer_num].append(node_num)

    nodes_drawn = [0] * (last_layer + 1)

    for node in net["nodes"]:
        x = int(round(((node["layer"] + 1) / (last_layer + 2)) * width))
        y = int(round(((nodes_drawn[node["layer"]] + 1) / ((nodes_per_layer[node["layer"]]) + 1)) * height))
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 6)
        nodes_drawn[node["layer"]] += 1

    for node in net["nodes"]:
        for conn_num in node["connections"]:
            connection = net["connections"][conn_num]
            from_node = connection["from"]
            from_layer = net["nodes"][from_node]["layer"]
            to_node = connection["to"]
            to_layer = net["nodes"][to_node]["layer"]
            weight = connection["weight"]

            x1 = int(round(((from_layer + 1) / (last_layer + 2)) * width))
            y1 = int(round(((nodes_in_layer[from_layer].index(from_node) + 1) / (nodes_per_layer[from_layer] + 1) *
                            height)))

            x2 = int(round(((to_layer + 1) / (last_layer + 2)) * width))
            y2 = int(round(((nodes_in_layer[to_layer].index(to_node) + 1) / (nodes_per_layer[to_layer] + 1) * height)))

            if weight < 0.0:
                pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), int(ceil(-weight * 8)))
            elif weight > 0.0:
                pygame.draw.line(screen, (0, 255, 0), (x1, y1), (x2, y2), int(ceil(weight * 8)))

    pygame.display.set_caption("View Network %d" % num)
    pygame.display.flip()
    screen.fill(0)


nets = load([])
draw_net(0, nets)

curr_net = 0
last_refresh = datetime.now()

while True:

    if (datetime.now() - last_refresh).total_seconds() >= 2:
        nets = load(nets)
        last_refresh = datetime.now()

    draw_net(curr_net, nets)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                nets = load(nets)
                curr_net -= 1
                curr_net %= len(nets)
            elif event.key == pygame.K_3:
                nets = load(nets)
                curr_net += 1
                curr_net %= len(nets)
            elif event.key == pygame.K_RETURN:
                nets = load(nets)

    sleep(0.033)
