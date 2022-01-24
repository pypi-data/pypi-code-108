import os
import logging
from numpy.random import shuffle, choice
import numpy as np
from matplotlib import pyplot as plt
from clease.tools import (aic, aicc, bic)
from .regression import LinearRegression

logger = logging.getLogger(__name__)

workers = None

__all__ = ('SaturatedPopulationError', 'GAFit')


class SaturatedPopulationError(Exception):
    """A given population is saturated"""


# pylint: disable=too-many-instance-attributes
class GAFit:
    """
    Genetic Algorithm for selecting relevant clusters.

    Parameters:

    cf_matrix: np.ndarray
        Design matrix of the linear regression (nxm) where n is the number of
        data points and m is the number of features

    e_dft: list
        Array of length n with DFT energies

    elitism: int
        Number of best structures that will be passed unaltered on to the next
        generation

    fname: str
        File name used to backup the population. If this file exists, the next
        run will load the population from the file and start from there.
        Another file named 'fname'_cf_names.txt is created to store the
        names of selected clusters.

    num_individuals: int or str
        Integer with the number of inidivuals or it is equal to "auto",
        in which case 10 times the number of candidate clusters is used

    max_num_in_init_pool: int
        If given the maximum clusters included in the initial population
        is given by this number. If max_num_in_init_pool=150, then
        solution with maximum 150 will be present in the initial pool.

    cost_func: str
        Use the inverse as fitness measure.
        Possible cost functions:
        bic - Bayes Information Criterion
        aic - Afaike Information Criterion
        aicc - Modified Afaikes Information Criterion
        (tend to avoid overfitting better than aic)
    """

    def __init__(self,
                 cf_matrix,
                 e_dft,
                 mutation_prob=0.001,
                 elitism=1,
                 fname="ga_fit.csv",
                 num_individuals="auto",
                 max_num_in_init_pool=None,
                 cost_func="aicc"):
        allowed_cost_funcs = {"bic": bic, "aic": aic, "aicc": aicc}

        if cost_func not in allowed_cost_funcs:
            raise ValueError(f"Cost func has to be one of {allowed_cost_funcs.keys()}")

        self.cost_func = allowed_cost_funcs[cost_func]

        # Read required attributes from evaluate
        self.cf_matrix = cf_matrix
        self.e_dft = e_dft
        self.fname = fname
        self.fname_cf_names = fname.rpartition(".")[0] + "_cf_names.txt"

        if num_individuals == "auto":
            self.pop_size = 10 * self.cf_matrix.shape[1]
        else:
            self.pop_size = int(num_individuals)

        # Make sure that the population size is an even number
        if self.pop_size % 2 == 1:
            self.pop_size += 1
        self.num_genes = self.cf_matrix.shape[1]
        self.individuals = self._initialize_individuals(max_num_in_init_pool)
        self.fitness = np.zeros(len(self.individuals))
        self.regression = LinearRegression()
        self.elitism = elitism
        self.mutation_prob = mutation_prob
        self.statistics = {"best_score": [], "worst_score": []}
        self.evaluate_fitness()
        self.check_valid()

    def _initialize_individuals(self, max_num):
        """Initialize a random population."""
        individuals = []
        if os.path.exists(str(self.fname)):
            individuals = self._init_from_file()
        else:
            max_num = max_num or self.num_genes
            indices = list(range(self.num_genes))
            num_non_zero = np.array(list(range(0, self.pop_size)))
            num_non_zero %= max_num
            num_non_zero[num_non_zero < 3] = 3
            for i in range(self.pop_size):
                shuffle(indices)
                individual = np.zeros(self.num_genes, dtype=np.uint8)
                indx = indices[:num_non_zero[i]]
                individual[np.array(indx)] = 1
                individuals.append(self.make_valid(individual))
        return individuals

    def _init_from_file(self):
        """Initialize the population from file."""
        logger.info("Initializing population from %s", self.fname)
        individuals = []
        with open(self.fname, 'r') as infile:
            for line in infile:
                individual = np.zeros(self.num_genes, dtype=np.uint8)
                indices = np.array([int(x.strip()) for x in line.split(",")])
                individual[indices] = 1
                individuals.append(individual)
        return individuals

    def get_eci(self, individual):
        """Calculate the LOOCV for the current individual."""
        X = self.design_matrix(individual)
        y = self.e_dft
        return self.regression.fit(X, y)

    def design_matrix(self, individual):
        """Return the corresponding design matrix."""
        return self.cf_matrix[:, individual == 1]

    def fit_individual(self, individual):
        coeff = self.get_eci(individual)
        X = self.design_matrix(individual)
        e_pred = X.dot(coeff)
        delta_e = self.e_dft - e_pred

        info_measure = None
        n_selected = np.sum(individual)
        mse = np.sum(delta_e**2) / self.num_data
        info_measure = self.cost_func(mse, n_selected, self.num_data)
        return coeff, -info_measure

    def evaluate_fitness(self):
        """Evaluate fitness of all species."""
        for i, ind in enumerate(self.individuals):
            _, fit = self.fit_individual(ind)
            self.fitness[i] = fit

    @staticmethod
    def flip_one_mutation(individual):
        """Apply mutation where one bit flips."""
        indx_sel = list(np.argwhere(individual.T == 1).T[0])
        ns = list(np.argwhere(individual.T == 0).T[0])

        assert len(indx_sel) != 0 or len(ns) != 0
        if len(ns) == 0:
            ns = indx_sel
        elif len(indx_sel) == 0:
            indx_sel = ns

        # Flip included or not included cluster with equal
        # probability
        if np.random.rand() < 0.5:
            indx = choice(indx_sel)
        else:
            indx = choice(ns)
        individual[indx] = (individual[indx] + 1) % 2
        return individual

    @staticmethod
    def make_valid(individual):
        """Make sure that there is at least two active ECIs."""
        if np.sum(individual) < 2:
            while np.sum(individual) < 2:
                indx = np.random.randint(low=0, high=len(individual))
                individual[indx] = 1
        return individual

    def create_new_generation(self):
        """Create a new generation."""
        # pylint: disable=too-many-statements
        new_generation = []
        srt_indx = np.argsort(self.fitness)[::-1]

        assert self.fitness[srt_indx[0]] >= self.fitness[srt_indx[1]]

        # Pass the fittest to the next generation
        num_transfered = 0
        counter = 0
        while num_transfered < self.elitism and counter < len(srt_indx):
            indx = srt_indx[counter]

            individual = self.individuals[indx].copy()

            # Transfer the best
            new_generation.append(individual)

            # Transfer the best individual with a mutation
            new_ind = self.flip_one_mutation(individual.copy())
            new_ind = self.make_valid(new_ind)
            while self._is_in_population(new_ind, new_generation):
                new_ind = self.flip_one_mutation(individual.copy())
                new_ind = self.make_valid(new_ind)

            new_generation.append(new_ind)
            num_transfered += 1
            counter += 1

        if counter >= len(srt_indx):
            self.save_population()
            raise SaturatedPopulationError("The entire population has been saturated!")

        only_positive = self.fitness - np.min(self.fitness)
        cumulative_sum = np.cumsum(only_positive)
        cumulative_sum /= cumulative_sum[-1]
        num_inserted = len(new_generation)

        max_attempts = 100 * self.pop_size
        # Create new generation by mergin existing
        for _ in range(num_inserted, int(self.pop_size / 2) + 1):
            rand_num = np.random.rand()
            p1 = np.argmax(cumulative_sum > rand_num)
            p2 = p1
            while p2 == p1:
                rand_num = np.random.rand()
                p2 = np.argmax(cumulative_sum > rand_num)

            new_individual = self.individuals[p1].copy()
            new_individual2 = self.individuals[p2].copy()

            mask = np.random.randint(0, high=2, size=len(new_individual))
            mask = mask.astype(np.uint8)
            new_individual[mask] = self.individuals[p2][mask]
            new_individual2[mask] = self.individuals[p1][mask]
            new_individual = self.make_valid(new_individual)
            new_individual2 = self.make_valid(new_individual2)

            # Check if there are any equal individuals in
            # the population
            counter = 0
            while (self._is_in_population(new_individual, new_generation) and
                   counter < max_attempts):
                new_individual = self.flip_one_mutation(new_individual)
                new_individual = self.make_valid(new_individual)
                counter += 1

            if counter >= max_attempts:
                self.save_population()
                raise SaturatedPopulationError("Popluation is saturated!")
            new_generation.append(new_individual)

            counter = 0
            while (self._is_in_population(new_individual2, new_generation) and
                   counter < max_attempts):
                new_individual2 = self.flip_one_mutation(new_individual2)
                new_individual2 = self.make_valid(new_individual2)
                counter += 1

            if counter >= max_attempts:
                self.save_population()
                raise SaturatedPopulationError("Popluation is saturated!")

            new_generation.append(new_individual2)

        if len(new_generation) != len(self.individuals):
            raise RuntimeError(f"Size of generation changed! Original size: "
                               f"{len(self.individuals)}. New size: "
                               f"{len(new_generation)}")
        self.individuals = new_generation

    @staticmethod
    def _is_in_population(ind, pop):
        """Check if the individual is already in the population."""
        return any(np.all(ind == x) for x in pop)

    def mutate(self):
        """Introduce mutations."""
        avg_f = np.mean(np.abs(self.fitness))
        best_indx = np.argmax(self.fitness)
        for i in range(len(self.individuals)):  # pylint: disable=consider-using-enumerate
            if i == best_indx:
                # Do not mutate the best individual
                continue

            mut_prob = self.mutation_prob

            # Increase the probability of introducing mutations
            # to the least fit individuals
            if abs(self.fitness[i]) > avg_f:
                mut_prob *= abs(self.fitness[i]) / avg_f

            mut_prob = min(mut_prob, 1.0)

            ind = self.individuals[i].copy()
            mutated = False
            assert mut_prob >= 0.0
            if np.random.rand() < mut_prob:
                ind = self.flip_one_mutation(ind)
                mutated = True

            if mutated:
                self.individuals[i] = self.make_valid(ind)
                _, fit = self.fit_individual(self.individuals[i])
                self.fitness[i] = fit

    def population_diversity(self):
        """Check the diversity of the population."""
        std = np.std(self.individuals)
        return np.mean(std)

    @property
    def best_individual(self):
        best_indx = np.argmax(self.fitness)
        individual = self.individuals[best_indx]
        return individual

    @property
    def num_data(self):
        return self.cf_matrix.shape[0]

    @property
    def best_individual_indx(self):
        best_indx = np.argmax(self.fitness)
        return best_indx

    def index_of_selected_clusters(self, individual):
        """Return the indices of the selected clusters

        Parameters:

        individual: int
            Index of the individual
        """
        return list(np.nonzero(self.individuals[individual])[0])

    def save_population(self):
        # Save population
        self.check_valid()
        with open(self.fname, 'w') as out:
            for i in range(len(self.individuals)):
                out.write(",".join(str(x) for x in self.index_of_selected_clusters(i)))
                out.write("\n")
        logger.info("Population written to %s.", self.fname)

    def plot_evolution(self):
        """Create a plot of the evolution."""
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self.statistics["best_score"], label="best")
        ax.plot(self.statistics["worst_score"], label="worst")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Score")
        plt.show()

    def run(self, gen_without_change=100, min_change=0.01, save_interval=100):
        """Run the genetic algorithm.

        Return a list consisting of the names of selected clusters at the end
        of the run.

        Parameters:

        gen_without_change: int
            Terminate if gen_without_change are created without sufficient
            improvement

        min_change: float
            Changes a larger than this value is considered "sufficient"
            improvement

        save_interval: int
            Rate at which all the populations are backed up in a file
        """
        num_gen_without_change = 0
        current_best = 0.0
        gen = 0
        while True:
            self.evaluate_fitness()

            best_indx = np.argmax(self.fitness)

            num_eci = np.sum(self.individuals[best_indx])
            diversity = self.population_diversity()
            self.statistics["best_score"].append(np.max(self.fitness))
            self.statistics["worst_score"].append(np.min(self.fitness))

            best3 = np.abs(np.sort(self.fitness)[::-1][:3])
            loocv_msg = ""

            logger.info(("Generation: %s. Top 3 scores %.2e (-)%.2e (-)%.2e."
                         " Num ECI: %d. Pop. div: %.2f. %s"), gen, best3[0], best3[0] - best3[1],
                        best3[0] - best3[2], num_eci, diversity, loocv_msg)
            self.mutate()
            self.create_new_generation()
            if abs(current_best - self.fitness[best_indx]) > min_change:
                num_gen_without_change = 0
            else:
                num_gen_without_change += 1
            current_best = self.fitness[best_indx]

            if gen % save_interval == 0:
                self.save_population()

            if num_gen_without_change >= gen_without_change:
                logger.info('Reached %d generations without sufficient improvement.',
                            gen_without_change)
                break
            gen += 1

        self.save_population()
        return self.best_individual

    def check_valid(self):
        """Check that the current population is valid."""
        for ind in self.individuals:
            valid = self.make_valid(ind.copy())
            if np.any(valid != ind):
                raise ValueError("Individual violate constraints!")
