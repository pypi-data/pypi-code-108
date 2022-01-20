#
#    (C) Quantum Computing Inc., 2020.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder. 
#    The contents of this file may not be disclosed to third parties, copied 
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
import base64
from io import BytesIO

import numpy as np
import scipy.sparse as sp
import networkx as nx


def encode_data(data):
    if isinstance(data, sp.spmatrix):
        data = sp.coo_matrix(data, dtype=float)
        return encode_sparse_array(data)

    elif isinstance(data, dict):
        return encode_dict(data)

    elif isinstance(data, np.ndarray):
        return encode_ndarray(data)

    elif isinstance(data, nx.Graph):
        return encode_graph(data)

    else:
        raise TypeError(
            "Input data must be NetworkX graph, dictionary, np.ndarray, or scipy.spmatrix"
        )


def encode_dict(data):
    qubo_str = str(data).encode('utf-8')
    return base64.b64encode(qubo_str).decode('utf-8')


def encode_ndarray(qubo: np.ndarray) -> bytes:
    fbytes = BytesIO()
    #######
    # To extract:
    # arrdata = np.load('fname.npz')['data']
    np.savez_compressed(fbytes, data=qubo)
    return fbytes.getvalue()


def encode_graph(graph: nx.Graph) -> bytes:
    fbytes = BytesIO()
    #######
    # To extract:
    # arrdata = np.load('fname.npz')['data']
    nx.write_gpickle(graph, fbytes)
    return fbytes.getvalue()


def encode_sparse_array(qubo: sp.spmatrix) -> bytes:
    fbytes = BytesIO()
    ########
    # To extract:
    #   arrdata = sp.load_npz('fname.npz')
    sp.save_npz(fbytes, qubo, compressed=True)
    return fbytes.getvalue()
