from typing import List, Optional
import numpy as np
import pandas as pd
from kinalite.kinetic_analysis import Result, Column, Reaction, KineticExperiment


class Experiment:
    default_orders = np.linspace(-2, 2, 201)

    def __init__(self, name: str, data: List[pd.DataFrame], substrate_index: int, product_index: int):
        self.name = name
        self.data = data
        self.substrate_column = substrate_index
        self.product_column = product_index
        self.frames = {}
        self.results: Optional[List[Result]] = None
        self.best_result: Optional[Result] = None
        self.best_order: Optional[float] = None
        self.reactions = [
            self.create_reaction(f'{name}_{i}', data[i]) for i in range(len(data))
        ]
        self.kinetic_experiment = KineticExperiment(
            comparable_experiments=self.reactions,
            substrate_index=substrate_index,
            product_index=product_index,
        )
        self.reset()

    def reset(self):
        self.frames = {}
        self.results: Optional[List[Result]] = None
        self.best_result: Optional[Result] = None
        self.best_order: Optional[float] = None

    def create_reaction(self, name: str, data: pd.DataFrame):
        filled_data = data.fillna(0)
        columns = [
            Column(name=key, values=np.array(filled_data[key])) for key in data.keys()
        ]

        return Reaction(name=name, data=columns)

    def calculate_results(self, orders = None) -> List[Result]:
        self.frames = self.kinetic_experiment.get_frames(self.default_orders if orders is None else orders)

        results = []
        # Result = namedtuple("Result", "order score curves")
        for order, score, abscissas, ordinates in zip(self.frames["Orders"], self.frames["Scores"], self.frames["Abscissas"], self.frames["Ordinates"]):
            result = Result(order, score, abscissas, ordinates)
            results.append(result)

        return results

    def calculate_best_result(self, orders = None) -> Result:
        if self.results is None:
            self.results = self.calculate_results(orders)

        if self.best_result is None:
            self.best_order = self.get_best_order(self.results)
            results = self.calculate_results([self.best_order])
            self.best_result = results[0]

        return self.best_result

    def get_best_order(self, result):
        orders = [result.order for result in result]
        scores = [result.score for result in result]
        best_index = np.argmin(scores)
        best_order = orders[best_index]
        return best_order
