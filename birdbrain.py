import torch
import copy
import random
import numpy as np


class BirdBrain:
    def __init__(self, input_size=5, hidden_size=8, output_size=1):
        layers = list()
        layers.append(torch.nn.Linear(input_size, hidden_size))
        layers.append(torch.nn.Sigmoid())
        layers.append(torch.nn.Linear(hidden_size, output_size))
        layers.append(torch.nn.Sigmoid())

        self.net = torch.nn.Sequential(*layers)

    def forward(self, data):
        return self.net.forward(torch.tensor(data)).item()

    def clone(self):
        return copy.deepcopy(self)

    def mutate(self, probability):
        for tensor in self.net.parameters():
            flattened = tensor.view(-1)
            for i in range(flattened.size()[0]):
                if random.random() < probability:
                    flattened[i] = flattened[i].item() + np.random.normal(0)

    @staticmethod
    def crossover(brain1, brain2):
        # TODO
        return brain1, brain2
