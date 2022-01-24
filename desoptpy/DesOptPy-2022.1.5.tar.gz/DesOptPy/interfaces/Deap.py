"""
GA
GP
ES
PSO

https://deap.readthedocs.io/en/master/tutorials/advanced/constraints.html
https://deap.readthedocs.io/en/master/examples/index.html
"""
import deap


def OptNlOpt(self, x0, xL, xU, SysEq):
    def evalFct(individual):
        """Evaluation function for the individual."""
        x = individual[0]
        return ((x - 5) ** 2 * sin(x) * (x / 3),)

    def feasible(individual):
        """Feasibility function for the individual. Returns True if feasible False
        otherwise."""
        if 3 < individual[0] < 7:
            return True
        return False

    def distance(individual):
        """A distance function to the feasibility region."""
        return (individual[0] - 5.0) ** 2
