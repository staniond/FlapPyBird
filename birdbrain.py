import torch
import copy
import random
import numpy as np


class BirdBrain:
    def __init__(self, input_size=6, hidden_size=8, output_size=2):
        layers = list()
        layers.append(torch.nn.Linear(input_size, hidden_size))
        layers.append(torch.nn.Sigmoid())
        layers.append(torch.nn.Linear(hidden_size, output_size))
        layers.append(torch.nn.Softmax(0))

        self.net = torch.nn.Sequential(*layers)

    def forward(self, data):
        result = self.net.forward(torch.tensor(data))
        return result[0].item(), result[1].item()

    def clone(self):
        return copy.deepcopy(self)

    def mutate(self, probability):
        with torch.no_grad():
            for tensor in self.net.parameters():
                flattened = tensor.view(-1)
                for i in range(flattened.size()[0]):
                    if random.random() < probability:
                        flattened[i] = flattened[i].item() + np.random.normal()

    def log(self):
        for tensor in list(self.net.parameters()):
            flattened = tensor.view(-1)
            print(flattened)

    @staticmethod
    def random_swap_value_crossover(brain1, brain2):
        layers1 = list(brain1.net.parameters())
        layers2 = list(brain2.net.parameters())
        for i in range(len(layers1)):
            flattened1 = layers1[i].view(-1)
            flattened2 = layers2[i].view(-1)
            for j in range(len(flattened1)):
                if random.random() < 0.5:
                    val1 = flattened1[j].item()
                    val2 = flattened2[j].item()
                    flattened1[j] = val2
                    flattened2[j] = val1

    @staticmethod
    def random_swap_layer_crossover(brain1, brain2):
        layers1 = list(brain1.net.parameters())
        layers2 = list(brain2.net.parameters())
        for i in range(len(layers1)):
            if len(layers1[i].shape) == 2:
                for j in range(len(layers1[i])):
                    if random.random() < 0.5:
                        layer1 = layers1[i][j].data
                        layer2 = layers2[i][j].data
                        layers1[i][j].data = layer2
                        layers2[i][j].data = layer1
            else:
                if random.random() < 0.5:
                    layer1 = layers1[i].data
                    layer2 = layers2[i].data
                    layers1[i].data = layer2
                    layers2[i].data = layer1

    crossover = random_swap_layer_crossover
