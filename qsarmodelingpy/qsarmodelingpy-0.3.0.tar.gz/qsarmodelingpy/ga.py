"""Variable selection with Genetic Algorithm."""
import random
import json
from tqdm import tqdm
import logging

from deap import base
from deap import creator
from deap import tools
from numpy import zeros, shape, argmax
import pandas as pd
from pandas import read_csv
from qsarmodelingpy.cross_validation_class import CrossValidation


def returnIndices(individual):
    return [i for i, v in enumerate(individual) if v == 1]


def checkLen(min, max):
    def decorator(func):
        def wrapper(*args, **kargs):
            offspring = func(*args, **kargs)
            for child in offspring:
                size = sum(child)
                indices = returnIndices(child)
                indicesZeros = [i for i in list(
                    range(len(child))) if i not in indices]
                while size > max:
                    child[indices[random.randint(0, len(indices)-1)]] = 0
                    size = sum(child)
                while size < min:
                    child[indicesZeros[random.randint(
                        0, len(indicesZeros)-1)]] = 1
                    size = sum(child)
            return offspring
        return wrapper
    return decorator


def initIndividual(icls, imin, imax, size):
    indices = random.sample(range(size), random.randint(imin, imax))
    l = zeros(size)
    l[indices] = 1
    l = [int(i) for i in l.tolist()]
    ind = icls(l)
    return ind


class Ga(object):
    def __init__(self, X: pd.DataFrame, y: pd.DataFrame, nLV: int = None, scale: bool = True, min_size: int = 5, max_size: int = 25, size_population: int = 200, mig_rate: float = 0.2,
                 cxpb: float = 0.5, mutpb: float = 0.2, ngen: int = 120):
        """Variable selection with Genetic Algorithm.

        Args:
            X (DataFrame): The matrix with descriptors.
            y (DataFrame, list, array): The dependent variable vector.
            nLV (int, optional): Number of Latent Variables. Defaults to None.
            scale (bool, optional): Defaults to True.
            min_size (int, optional): Minimum number of variables in the model. Defaults to 5.
            max_size (int, optional): Maximum number of variables in the model. Defaults to 25.
            size_population (int, optional): Size of the population in each generation. Defaults to 200.
            mig_rate (float, optional): Migration rate. Defaults to 0.2.
            cxpb (float, optional): Crossover rate. Defaults to 0.5.
            mutpb (float, optional): Mutation rate. Defaults to 0.2.
            ngen (int, optional): Number of generations. Defaults to 120.
        """
        self.X = X
        self.y = y
        self.nLV = nLV
        self.scale = scale
        self.min_size = min_size
        self.max_size = max_size
        self.size_population = size_population
        self.mig_rate = mig_rate
        self.cxpb = cxpb
        self.mutpb = mutpb
        self.ngen = ngen

    def evaluate(self, individual):
        """Do some hard computing on the individual"""
        indices = [i for i, v in enumerate(individual) if v == 1]
        Xev = self.X[:, indices]
        cv = CrossValidation(Xev, self.y, min(
            self.nLV, len(indices)), self.scale)
        Q2 = max(cv.Q2())
        #yr = YRandomization(X,y,argmax(cv.Q2())+1,50)
        return (Q2,)

    def run(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        MIN_SIZE = self. min_size
        MAX_SIZE = self.max_size
        IND_SIZE = shape(self.X)[1]
        SIZE_POPULATION = self.size_population
        MIG_RATE = self.mig_rate  # migration rate
        X = self.X
        y = self.y
        nLV = self.nLV
        CXPB = self.cxpb
        MUTPB = self.mutpb
        NGEN = self.ngen

        toolbox = base.Toolbox()

        toolbox.register("individual", initIndividual, creator.Individual,
                         MIN_SIZE, MAX_SIZE, IND_SIZE)

        toolbox.register("population", tools.initRepeat,
                         list, toolbox.individual)

        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.2)
        toolbox.decorate("mate", checkLen(MIN_SIZE, MAX_SIZE))
        toolbox.decorate("mutate", checkLen(MIN_SIZE, MAX_SIZE))
        toolbox.register("select", tools.selTournament, tournsize=2)
        #toolbox.register("select", tools.selBest)
        toolbox.register("evaluate", self.evaluate)

        pop = toolbox.population(n=SIZE_POPULATION)

        # Evaluate the entire population
        fitnesses = map(toolbox.evaluate, pop)
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        logging.info("Running Genetic Algorithm...")
        progress_bar = tqdm(total=NGEN, position=1, leave=True)
        for _ in range(NGEN):
            progress_bar.update()
            # generates migrants to add to the population
            mig = toolbox.population(n=int(MIG_RATE*SIZE_POPULATION))
            fitnesses = map(toolbox.evaluate, mig)
            for ind, fit in zip(mig, fitnesses):
                ind.fitness.values = fit
            # Select the next generation individuals
            # Clone the selected individuals
            offspring = list(map(toolbox.clone, pop))
            # form the new population
            offspring += mig
            indices = random.sample(range(len(offspring)), len(offspring))
            offspring = [offspring[i] for i in indices]

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < CXPB:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < MUTPB:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # The population is replaced by best individuals in the offspring
            pop = toolbox.select(offspring, len(pop))
        progress_bar.close()
        individuals = [ind for ind in pop]
        self.Q2 = [ind.fitness.values for ind in pop]
        self.pop_selected = [returnIndices(ind) for ind in individuals]

    def saveQ2(self, file):
        """Saves Q² output to `file`.

        Args:
            file (str path, file-like, `io`): The filename to save Q² output.
        """
        with open(file, "w") as Q2_file:
            Q2_file.write(json.dumps(self.Q2))

    def savePop(self, file):
        """Saves population to `file`.

        Args:
            file (str path, file-like, `io`): The filename to save population output.
        """
        with open(file, "w") as pop_file:
            pop_file.write(json.dumps(self.pop_selected))
