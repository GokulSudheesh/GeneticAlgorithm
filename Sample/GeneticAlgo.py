import random
from operator import attrgetter

def demo_fitness(individual):
    '''
    This is just a sample function for demonstration purpose.
    Basically we are generating a target binary sequence of 11111111...
    '''
    TARGET = ""
    score = len(individual)
    for i in range(len(individual)):
        TARGET += "1"
        if individual[i] == '1':
            score -= 1
    return score


class Individual:
    @classmethod
    def generate_random_chromosome(cls, length):
        new_chromosome = ""
        for i in range(length):
            new_chromosome += str(random.randint(0,1))
        return new_chromosome

    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.fitness = self.calculate_fitness()
    
    def calculate_fitness(self):
        '''
        A fitness function which will calculate fitness of the individual.
        Change this for the ding-dong DAA assignment. - Future you.
        Before I go.. Harambe is not dead. He.. he..
        '''
        return demo_fitness(self.chromosome)
    
    def mutate(self):
        pos = []
        pos_len = random.randint(1, len(self.chromosome))
        probability = random.randint(0, 1) # To get 50-50 probability
        #probability=0
        new_chromosome = ""
        if probability == 0: # mutating first few bits
            print("First", pos_len, "bit(s)")
            for i in (range(pos_len)):
                #print(gene, i)
                mutated_bit = "1"
                if (self.chromosome[i]=="1"):
                    mutated_bit = "0"
                new_chromosome += mutated_bit
                print(self.chromosome[i], " mutated to ", mutated_bit)
            for i in range(pos_len, len(self.chromosome)):
                new_chromosome += self.chromosome[i]
        else: # mutating last few bits
            print("Last", pos_len, "bit(s)")
            for i in range(0, len(self.chromosome)-pos_len):
                new_chromosome += self.chromosome[i]
            for i in range(len(self.chromosome)-pos_len,len(self.chromosome)):
                #print(gene, i)
                mutated_bit = "1"
                if (self.chromosome[i]=="1"):
                    mutated_bit = "0"
                new_chromosome += mutated_bit
                print(self.chromosome[i], " mutated to ", mutated_bit)
        
        return new_chromosome

    def bit_flip_mutation(self):
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
    population = []
    bits = 10
    population_size = 20 # try to keep multiples of 10
    for i in range(population_size):
        ind = Individual(Individual.generate_random_chromosome(bits))
        population.append(ind)
    while(generation <= 20):
        population.sort(key=attrgetter('fitness'))
        for i in range(population_size):
            print(population[i].chromosome, population[i].fitness)
        print("Generation: ", generation)
        print("Best Fitness: ", population[0].chromosome, population[0].fitness)
        print("Population length: ", len(population))
        print("==============================================================")

        #del (population[len(population) - 2:len(population)]) # Delete last 2 individuals in a population
        new_population = []
        # Crossover operation for first 80% individuals in the population
        for i in range(int((0.8*population_size)/4)):
            p = Individual(population[i].one_point_crossover(population[i+1]))
            new_population.append(p)
            p = Individual(population[i].uniform_crossover(population[i+1]))
            new_population.append(p)
            p = Individual(population[i+1].uniform_crossover(population[i]))
            new_population.append(p)
            p = Individual(population[i+1].one_point_crossover(population[i]))
            new_population.append(p)
        # Mutation operation for last 20% individuals in the population
        for i in range (int((0.8*population_size)/4)+1, int((0.8*population_size)/4)+1+int(0.2*population_size)):
            p = Individual(population[i].bit_flip_mutation())
            new_population.append(p)
        population = new_population
        generation += 1