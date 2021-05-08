import random
from operator import attrgetter
import time
from datetime import timedelta
import matplotlib.pyplot as plt
import statistics

items = 10
capacity = 25
WEIGHTS = [4, 5, 7, 4, 3, 3, 7, 2, 8, 9]
PROFIT = [3, 1, 12, 6, 5, 11, 15, 6, 9, 4]
x=[]
y_best_fitness=[]
y_mean_fitness=[]
y_median_fitness=[]
y_variance_fitness=[]


def plot(x, y, x_label, y_label):
    plt.plot(x, y)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()
    
def get_random_population(population_size):
    '''
    This function generates random population after the unfit individuals are removed.
    This is done so that the population size remains constant every generation.
    :param population_size:
    :return: a list of population
    '''
    population = []
    i = 0
    while i < population_size:
        ind = Individual(Individual.generate_random_chromosome(items))
        if (ind.total_weight > capacity or ind.chromosome in population):
            i -= 1
        else:
            population.append(ind)
        i += 1
    return population

class Individual:
    @classmethod
    def generate_random_chromosome(cls, length):
        '''
        This is a class method: means no need to create object
        to call this function.

        :param length:
        :return: an individual with random 0s and 1s
        '''
        new_chromosome = ""
        for i in range(length):
            new_chromosome += str(random.randint(0,1))
        return new_chromosome

    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.total_weight = self.calculate_capacity()
        self.fitness = self.calculate_fitness()

    def calculate_capacity(self):
        # Calculates capacity of the individual. Checks for 1s and sunms the weights
        # of that element.
        individual_weight = 0
        for i in range(len(self.chromosome)):
            if self.chromosome[i] == "1":
                individual_weight += WEIGHTS[i]
        return individual_weight
    
    def calculate_fitness(self):
        '''
        A fitness function which will calculate fitness of the individual.
        It just returns the profit of the 0-1 knapsack.
        '''        
        fitness_score = 0
        for i in range(len(self.chromosome)):
            if self.chromosome[i] == "1":
                fitness_score += PROFIT[i]
        return fitness_score

    def bit_flip_mutation(self):
        # Bit flip mutation is a type of mutation.
        pos = []
        pos_len = random.randint(1, len(self.chromosome))
        new_chromosome = self.chromosome
        for i in range(pos_len):
            p = random.randint(0, len(self.chromosome)-1)
            while(p in pos):
                p = random.randint(0, len(self.chromosome)-1)
            pos.append(p)
        for i in pos:
            mutated_bit = "1"
            if (self.chromosome[i] == "1"):
                mutated_bit = "0"
            #print("Pos:", i, " mutated to ", mutated_bit)
            new_chromosome = new_chromosome[0:i]+mutated_bit+new_chromosome[i+1:len(self.chromosome)]
        return new_chromosome

    def one_point_crossover(self, parent2):
        pos = random.randint(1, len(self.chromosome)-1)
        new_chromosome = ""
        new_chromosome += self.chromosome[0:pos]
        new_chromosome += parent2.chromosome[pos:len(self.chromosome)]
        return new_chromosome

    def uniform_crossover(self, parent2):
        new_chromosome = self.chromosome
        for i in range(len(self.chromosome)):
            probability = random.randint(0, 1)  # To get 50-50 probability
            if (probability == 0):
                new_chromosome = new_chromosome[0:i]+parent2.chromosome[i]+new_chromosome[i+1:len(self.chromosome)]
        return new_chromosome

if __name__ == '__main__':
    generation = 0
    bits = items
    population_size = 100
    population = get_random_population(population_size)
    while(generation <= 15):
        x.append(generation)
        # Removing individuals that exceeds the capacity.
        new_population = []
        for i in range(len(population)):
            if population[i].total_weight <= capacity:
                new_population.append(population[i])
        population = new_population
        # Adding random individuals if population size changed:
        if (len(population) != population_size):
            for i in range(population_size - len(population)):
                new_pop = Individual(Individual.generate_random_chromosome(bits))
                while(new_pop.total_weight > capacity):
                    new_pop = Individual(Individual.generate_random_chromosome(bits))
                population.append(new_pop)

        population.sort(key=attrgetter('fitness'))
        population.reverse()
         
        fitnesses = []
        for i in range(population_size):
            print(population[i].chromosome, population[i].total_weight, population[i].fitness)
            fitnesses.append(population[i].fitness)          
            
        print("Generation: ", generation)
        print("Best Fitness: ", population[0].chromosome, population[0].fitness)
        y_best_fitness.append(population[0].fitness)
        y_mean_fitness.append(statistics.mean(fitnesses))
        y_median_fitness.append(statistics.median(fitnesses))
        y_variance_fitness.append(statistics.variance(fitnesses))
        #print("Capacity: ", population[0].total_weight)
        #print("Population length: ", len(population))
        print("==============================================================")

        #del (population[len(population) - 2:len(population)]) # Delete last 2 individuals in a population
        new_population = []
        # Crossover operation for first 80% individuals in the population
        for i in range(int((0.8 * population_size) / 4)):
            p = Individual(population[i].one_point_crossover(population[i+1]))
            new_population.append(p)
            p = Individual(population[i].uniform_crossover(population[i+1]))
            new_population.append(p)
            p = Individual(population[i+1].uniform_crossover(population[i]))
            new_population.append(p)
            p = Individual(population[i+1].one_point_crossover(population[i]))
            new_population.append(p)
        # Mutation operation for last 20% individuals in the population
        for i in range(int((0.8 * population_size) / 4) + 1, int((0.8 * population_size) / 4) + 1 + int(0.2 * population_size)):
            p = Individual(population[i].bit_flip_mutation())
            new_population.append(p)
        population = new_population
        generation += 1
    plot(x, y_best_fitness, "Generation", "Fitness")
    plot(x, y_mean_fitness, "Generation", "Mean Fitness")
    plot(x, y_median_fitness, "Generation", "Median Fitness")
    plot(x, y_variance_fitness, "Generation", "Variance Fitness")