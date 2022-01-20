#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
from typing import Dict, Any, Union
import numpy as np
import scipy.sparse as sp
import pandas as pd
import networkx as nx
from abc import ABC, abstractmethod


class ABCResult(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()

    @abstractmethod
    def _get_name(self):
        pass

    @abstractmethod
    def get_num_samples(self):
        pass

    @abstractmethod
    def get_samples(self):
        pass

    @abstractmethod
    def to_json_response(self):
        pass


class Result(ABCResult):

    def __init__(self,
                 samples: Any,
                 energies: Any,
                 counts: Any,
                 is_feasible: Any = None,
                 time: dict = None,
                 jobinfo: dict = None,
                 properties: dict = None):
        """
        Result is the base class containing method for access and analyzing
        the samples, energies, and counts returned by QatalystCore.

        Args:
            samples: iterable, such as list[dict sample]
            energies: iterable of float energies
            counts: iterable of int counts
            time: dict (optional), table of timing information related to setup and execution of the sampler
            jobinfo: dict (optional), info about the qatalyst job used to submit the problem and receive the response
            properties: dict (optional), Container for additional information.
                Must be json-serializable if planning to use to_json_response later.
        """
        super().__init__()
        self.samples = samples
        self.energies = energies
        self.counts = counts
        self.is_feasible = is_feasible
        self.time = time
        self.jobinfo = jobinfo
        self.properties = properties

    @classmethod
    def from_dict_response(cls, resp):
        try:
            if resp.get('is_feasible'):
                is_feasible_response = np.asarray(resp.get('is_feasible')).astype(bool)
            else:
                is_feasible_response = None

            return cls(
                samples=np.asarray(resp.get('samples')),
                energies=np.asarray(resp['energies']),
                counts=np.asarray(resp['counts']),
                is_feasible=is_feasible_response,
                time=resp.get('time', {}),
                jobinfo=resp.get('jobinfo', {}),
                properties=resp.get('properties', {})
            )

        except KeyError:
            # error is str from quoir service is_error rabbit mq messages
            print(resp["Error"])

    @classmethod
    def filter_feasible_solutions(cls, resp, constraints: Union[np.ndarray, sp.spmatrix]):
        # assumes samples[i] np.array
        # Initialize empty container for samples that meet constraints
        meet_constraints_samples = []
        meet_constraints_energies = []
        meet_constraints_counts = []
        b = - constraints[:, -1]
        A = constraints[:, :-1]
        for i, sample in enumerate(resp.samples):
            if np.all(np.matmul(A, resp.samples[i].T) == b):
                meet_constraints_samples.append(resp.samples[i])
                meet_constraints_energies.append(resp.energies[i])
                meet_constraints_counts.append(resp.counts[i])
        return cls(np.asarray(meet_constraints_samples),
                   np.asarray(meet_constraints_energies),
                   np.asarray(meet_constraints_counts))

    def _get_name(self):
        return "Result"

    def __repr__(self) -> str:
        repr = [self._get_name()]
        for name, data in zip(['samples', 'energies', 'counts'],
                              [self.samples, self.energies, self.counts]):
            repr.append('\n{}\n{}'.format(name, data[:10]))
        try:
            if self.jobinfo is not None:
                for key in self.jobinfo:
                    repr.append('\n{}\n{}'.format(key, self.jobinfo[key]))
            if self.properties is not None:
                for key in self.properties:
                    repr.append('\n{}\n{}'.format(key, self.properties[key]))
        except AttributeError:
            pass
        return ''.join(repr)

    def get_num_samples(self) -> int:
        return len(self.samples)

    def get_samples(self) -> Any:
        """
        Returns:
            array-like, samples
        """
        return self.samples

    def to_pandas_response(self) -> Any:
        """
        Construct a Pandas DataFrame using samples, energies, and counts attributes

        :return: pandas DataFrame
        """
        d = {"samples": list(self.samples),
             "energies": self.energies,
             "counts": self.counts}
        return pd.DataFrame(data=d)

    def to_json_response(self) -> Dict:
        """
        :return: dict
        """
        return {'samples': self.samples,
                'energies': self.energies,
                'counts': self.counts,
                'is_feasible': self.is_feasible,
                'time': self.time,
                'jobinfo': self.jobinfo,
                'properties': self.properties}


class GraphResult(Result):

    def __init__(self,
                 samples: Any,
                 encoded_samples: Any,
                 energies: Any,
                 counts: Any,
                 is_feasible: Any = None,
                 time: dict = None,
                 jobinfo: dict = None,
                 properties: dict = None):
        """
        GraphResult contains methods for accessing and analyzing the samples, energies,
        and counts returned by QGraph-QatalystCore for graph problems. The `samples` attribute contains mappings from graph
        nodes to their computed classes. The `encoded_samples` attribute holds an equivalent array
        of one-hot encoded samples.

        Args:
            samples: List[dict], [list encoded samples]
            encoded_samples: nd.array, bit vectors of samples corresponding to one-hot encoding of solutions
            energies: iterable of float energies
            counts: iterable of int counts
            time: dict (optional), table of timing information related to setup and execution of the sampler
            jobinfo: dict (optional), info about the qatalyst job used to submit the problem and receive the response
            properties: dict (optional), Container for additional information.
                Must be json-serializable if planning to use to_json_response later.
        """
        super().__init__(
            samples=samples,
            energies=energies,
            counts=counts,
            is_feasible=is_feasible,
            time=time,
            jobinfo=jobinfo,
            properties=properties
        )

        self.encoded_samples = encoded_samples

    @classmethod
    def from_dict_response(cls, resp):
        # TODO: temporary. We may want to make sure that that samples holds the original bit vectors
        # print(resp)
        try:
            if resp.get('is_feasible'):
                is_feasible_response = np.asarray(resp.get('is_feasible')).astype(bool)
            else:
                is_feasible_response = None

            return cls(samples=resp['samples'],
                       encoded_samples=resp['encoded_samples'],
                       energies=np.asarray(resp['energies']),
                       counts=np.asarray(resp['counts']),
                       is_feasible=is_feasible_response,
                       time=resp['time'],
                       jobinfo=resp['jobinfo'],
                       properties=resp['properties'])
        except KeyError:
            # this error should me the same as the message sent for is_error messages from Quoir Service
            print(resp["Error"])

    def to_json_response(self) -> Dict:
        """
        Returns:
            dict
        """
        return {'samples': self.samples,
                'encoded_samples': self.encoded_samples,
                'energies': self.energies,
                'counts': self.counts,
                'is_feasible': self.is_feasible,
                'time': self.time,
                'jobinfo': self.jobinfo,
                'properties': self.properties}

    def from_dict_to_array(self, data):
        return list(data.values())

    def _get_name(self):
        return "GraphResult"

    def map_sample_to_graph(self, G: Union[nx.Graph, np.ndarray, sp.spmatrix], sample_num: int = 0) -> nx.Graph:
        """
        Map input sample to node attributes of input graph, G.

        Args:
            :param G: networkx graph, numpy ndarray or scipy spmatrix. Undirected, with possible edge weights.
            :param sampl_num: int, index of sample for which to map labels onto nodes of G.

        returns: nx.Graph. Node attributes set with key 'label'.
        """
        # Convert to networkx graph structure if input graph is in dense or sparse matrix representation
        if isinstance(G, np.ndarray):
            G_copy = nx.from_numpy_array(G)
        elif isinstance(G, sp.spmatrix):
            G_copy = nx.from_scipy_sparse_matrix(G)
        else:
            G_copy = G.copy()
        # Set attribute label of graph nodes
        sample = {int(k): v for k, v in self.samples[sample_num].items()}
        nx.set_node_attributes(G_copy, sample, 'label')
        return G_copy
