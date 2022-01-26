"""Multilayer perceptron."""

import jax
import jax.numpy as jnp


SEED = 123


def relu(x):
    """Rectified linear unit activation function."""
    return jnp.maximum(0, x)


def random_layer_params(m, n, key, scale=1e-2):
    w_key, b_key = jax.random.split(key)
    return (
        scale * jax.random.normal(w_key, (n, m)),
        scale * jax.random.normal(b_key, (n,)),
    )


def init_network_params(sizes, key):
    """Initialize all layers."""
    keys = jax.random.split(key, len(sizes))
    return [
        random_layer_params(m, n, k) for m, n, k in zip(sizes[:-1], sizes[1:], keys)
    ]


sizes = [100, 100, 1]
key = jax.random.PRNGKey(0)
params = init_network_params(sizes, key)


def init_network_params(layer_sizes, key):
    """Initialize a fully-connected neural network.
    
    Parameters
    ----------
    sizes : list    
        List of integers defining the network layer sizes.
    key : jaxlib.xla_extension.DeviceArray
        Key for random number generation.

    Returns
    -------
    list
    """

    def random_layer_params(m, n, key, scale=1e-2):
        """Helper function for initializing network layer weights and biases."""
        w_key, b_key = jax.random.split(key)
        return (
            scale * jax.random.normal(w_key, (n, m)),
            scale * jax.random.normal(b_key, (n,)),
        )

    keys = jax.random.split(key, len(layer_sizes))
    params = [
        random_layer_params(m, n, k)
        for m, n, k in zip(layer_sizes[:-1], layer_sizes[1:], keys)
    ]
    return params
