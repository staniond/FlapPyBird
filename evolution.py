from bird import *
from birdbrain import *


class Evolution:
    def __init__(self, population_size):
        self.generation_number = 1
        self.population_size = population_size
        self.population = [Bird() for _ in range(self.population_size)]
        self.previous_population = []

    def new_population(self):
        self.generation_number += 1

        self.population = []

        best_brain = self.pick_best_brain(self.previous_population)
        self.population.append(Bird(best_brain))

        while len(self.population) < POPULATION_SIZE:
            first_brain, second_brain = self.tournament_pick_brains(self.previous_population)

            BirdBrain.crossover(first_brain, second_brain)

            first_brain.mutate(MUTATION_PROBABILITY)
            second_brain.mutate(MUTATION_PROBABILITY)

            self.population.append(Bird(first_brain))
            self.population.append(Bird(second_brain))

        self.previous_population = []

    # tournament selection from 10% of the population
    @staticmethod
    def tournament_pick_brains(generation):
        tournament = []
        for _ in range(len(generation) // 10):
            tournament.append(generation[random.randint(0, len(generation) - 1)])
        tournament.sort(key=lambda x: x.fitness, reverse=True)
        return tournament[0].brain.clone(), tournament[1].brain.clone()

    @staticmethod
    def pick_best_brain(generation):
        return Evolution.pick_best_bird(generation).brain.clone()

    @staticmethod
    def pick_best_bird(generation):
        best_bird = max(generation, key=lambda x: x.fitness)
        return best_bird

    def show_best_bird(self):
        best_bird_brain = self.population[0].brain.clone()    # last bird is left in the population
        self.population = [Bird(best_bird_brain)]

    def print_info(self):
        print(f"Gen {self.generation_number}, best bird fitness: {self.pick_best_bird(self.previous_population).fitness}")
