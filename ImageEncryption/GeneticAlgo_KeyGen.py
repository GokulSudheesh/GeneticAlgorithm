import random
from operator import attrgetter
from skimage.metrics import structural_similarity as ssim
import cv2
import LogisticChaos
import matplotlib.pyplot as plt

def plot(x, y, x_label, y_label):
    plt.plot(x, y)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

class Individual:
    @classmethod
    def generate_random_chromosome(cls, length):
        new_chromosome = ""
        for _ in range(length):
            new_chromosome += str(random.randint(0,1))
        return new_chromosome

    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.fitness = self.calculate_fitness()
        print("Fitness: ", self.fitness)
    
    def calculate_fitness(self):
        print("Calculating fitness for", self.chromosome)
        LogisticChaos.LogisticEncryption_Binary(image_name+extension, self.chromosome)
        im1 = cv2.imread(image_name + extension, 0)
        im2 = cv2.imread(image_name + "_Encryption" + ".png", 0)
        return(ssim(im1, im2))
    
    '''def mutate(self):
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
        
        return new_chromosome'''

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

image_name = "images/mona"
extension = ".jpg"
x=[]
y_best_fitness=[]

if __name__ == '__main__':
    generation = 0
    generations = 20
    population = []
    bits = 104
    population_size = 20
    best_fit_keys = []
    print("[INFO] Creating a random population of size:", population_size)
    for i in range(population_size):
        ind = Individual(Individual.generate_random_chromosome(bits))
        population.append(ind)
    print("[INFO] Done.")
    while(generation <= generations):
        x.append(generation)
        population.sort(key=attrgetter('fitness'))
        best_fit_keys.append(population[0])

        print("Generation: ", generation)
        print("Best Fit Key & Fitness: ", population[0].chromosome, population[0].fitness)
        y_best_fitness.append(population[0].fitness)
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
    best_fit_keys.sort(key=attrgetter('fitness'))
    print("Best fit key: ", best_fit_keys[0].chromosome)
    print("Fitness: ", best_fit_keys[0].fitness)
    LogisticChaos.LogisticEncryption_Binary(image_name+extension, best_fit_keys[0].chromosome)