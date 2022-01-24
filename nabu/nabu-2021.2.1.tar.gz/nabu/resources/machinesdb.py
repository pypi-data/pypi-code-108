"""
Database for describing standard servers
"""

ESRF_HPC_legacy_gpu = {
    "memory_GB": 128.,
    "gpus": [
        {
            "type": "cuda",
            "name": "Tesla K20m",
            "memory_GB": 4.9,
            "compute_capability": (3, 5),
        },
        {
            "type": "cuda",
            "name": "Tesla K20m",
            "memory_GB": 4.9,
            "compute_capability": (3, 5),
        },
    ],
    "cpu": {
        "name": "Intel(R) Xeon(R) CPU E5-2670 0",
        "threads": 16,
        "sockets": 2,
        "threads_per_core": 1,
    },
}

ESRF_HPC_legacy_cpu = {
    "memory_GB": 256.,
    "gpus": [],
    "cpu": {
        "name": "Intel(R) Xeon(R) CPU E5-2680 v4",
        "threads": 28,
        "sockets": 2,
        "threads_per_core": 1,
    },
}


IBM_AC922 = {
    "memory_GB": 616.0,
    "gpus": [
        {
            "type": "cuda",
            "name": "Tesla V100-SXM2-32GB",
            "memory_GB": 33.8,
            "compute_capability": (7, 0),
        },
        {
            "type": "cuda",
            "name": "Tesla V100-SXM2-32GB",
            "memory_GB": 33.8,
            "compute_capability": (7, 0),
        },
    ],
    "cpu": {
        "name": "POWER9",
        "threads": 128,
        "sockets": 2,
        "threads_per_core": 4,
    },
}

ESRF_LBS191 = {
    "memory_GB": 540.0,
    "gpus": [
        {
            "type": "cuda",
            "name": "GeForce GTX 1080 Ti",
            "memory_GB": 11.7,
            "compute_capability": (6, 1),
        },
    ],
    "cpu": {
        "name": "Intel(R) Xeon(R) CPU E5-2697 v3",
        "threads": 56,
        "sockets": 2,
        "threads_per_core": 2,
    },
}

DGX1 = {
    "memory_GB": 540.,
    "gpus": [
        {
            "type": "cuda",
            "name": "Tesla V100-SXM2-32GB",
            "memory_GB": 33.8,
            "compute_capability": (7, 0),
        },
        {
            "type": "cuda",
            "name": "Tesla V100-SXM2-32GB",
            "memory_GB": 33.8,
            "compute_capability": (7, 0),
        },
        {
            "type": "cuda",
            "name": "Tesla V100-SXM2-32GB",
            "memory_GB": 33.8,
            "compute_capability": (7, 0),
        },
        {
            "type": "cuda",
            "name": "Tesla V100-SXM2-32GB",
            "memory_GB": 33.8,
            "compute_capability": (7, 0),
        },
        {
            "type": "cuda",
            "name": "Tesla V100-SXM2-32GB",
            "memory_GB": 33.8,
            "compute_capability": (7, 0),
        },
        {
            "type": "cuda",
            "name": "Tesla V100-SXM2-32GB",
            "memory_GB": 33.8,
            "compute_capability": (7, 0),
        },
        {
            "type": "cuda",
            "name": "Tesla V100-SXM2-32GB",
            "memory_GB": 33.8,
            "compute_capability": (7, 0),
        },
        {
            "type": "cuda",
            "name": "Tesla V100-SXM2-32GB",
            "memory_GB": 33.8,
            "compute_capability": (7, 0),
        },
    ],
    "cpu": {
        "name": "Intel(R) Xeon(R) CPU E5-2698 v4",
        "threads": 80,
        "sockets": 2,
        "threads_per_core": 2,
    },
}
