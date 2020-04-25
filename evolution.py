from bird import *
from birdbrain import *


class Evolution:
    def __init__(self, population_size):
        self.generation_number = 1
        self.population_size = population_size
        self.mutation_probability = MUTATION_PROBABILITY
        self.crossover_probability = CROSSOVER_PROBABILITY
        self.population = [Bird() for _ in range(self.population_size)]
        self.best_brain = self.population[0].brain
        self.best_fitness = 0
        self.previous_population = []

        print(f"Population size: {self.population_size} birds",
              f"mutation probability: {self.mutation_probability * 100}%",
              f"crossover probability: {self.crossover_probability * 100}%\n", sep='\n')

    def new_population(self):
        # some bird maybe didn't die
        self.previous_population = self.previous_population + self.population
        self.population = []

        self.generation_number += 1

        prev_best_bird = self.pick_best_bird(self.previous_population)
        if prev_best_bird.fitness > self.best_fitness:
            self.best_fitness = prev_best_bird.fitness
            self.best_brain = prev_best_bird.brain.clone()
        self.population.append(Bird(self.best_brain.clone()))

        print(f"Gen {self.generation_number}, "
              f"best bird fitness: {self.pick_best_bird(self.previous_population).fitness}, "
              f"overall best bird fitness: {self.best_fitness}")

        while len(self.population) < POPULATION_SIZE:
            first_brain, second_brain = self.pick_brains(self.previous_population)

            if random.random() < self.crossover_probability:
                BirdBrain.crossover(first_brain, second_brain)

            first_brain.mutate(self.mutation_probability)
            second_brain.mutate(self.mutation_probability)

            self.population.append(Bird(first_brain))
            self.population.append(Bird(second_brain))

        self.previous_population = []

    # tournament selection from 20% of the population
    @staticmethod
    def tournament_pick_brains(generation):
        tournament = []
        for _ in range(len(generation) // 5):
            tournament.append(generation[random.randint(0, len(generation) - 1)])
        tournament.sort(key=lambda x: x.fitness, reverse=True)
        return tournament[0].brain.clone(), tournament[1].brain.clone()

    @staticmethod
    def roulette_pick_brain(generation):
        max_fitness = sum((x.fitness for x in generation))
        winners = []
        for _ in range(2):
            pick_probability = random.uniform(0, max_fitness)
            current_probability = 0
            for bird in generation:
                current_probability += bird.fitness
                if current_probability > pick_probability:
                    winners.append(bird.brain.clone())
                    break
        return winners

    pick_brains = tournament_pick_brains

    @staticmethod
    def pick_best_bird(generation):
        best_bird = max(generation, key=lambda x: x.fitness)
        return best_bird
