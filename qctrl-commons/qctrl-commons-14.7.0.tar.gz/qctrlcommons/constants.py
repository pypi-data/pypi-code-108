# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#      https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""Constants for testing."""
from enum import Enum

import numpy as np

PAULI_X = np.array([[0.0, 1.0], [1.0, 0.0]])

PAULI_Y = np.array([[0.0 + 0.0j, -0.0 - 1.0j], [0.0 + 1.0j, 0.0 + 0.0j]])

PAULI_Z = np.array([[1.0, 0.0], [0.0, -1.0]])

PAULI_I = np.array([[1.0, 0.0], [0.0, 1.0]])


SIGMA_MINUS = (PAULI_X + 1j * PAULI_Y) / 2
SIGMA_PLUS = (PAULI_X - 1j * PAULI_Y) / 2

HERMITIAN_OPERATOR = np.array(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, -1.0, 0.0, -0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, -0.0, 0.0, -1.0],
    ]
)

NON_HERMITIAN_OPERATOR = np.array(
    [
        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
        [1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
        [0.0 + 0.0j, 1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
    ]
)

UNITARY_OPERATOR = np.array([[0.0, 1.0], [np.exp(0.25j * np.pi), 0.0]])
NON_UNITARY_OPERATOR = np.array([[1.0, 0.0], [1.0, 1.0]])

SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
SIGMA_M = np.array([[0.0, 1.0], [0.0, 0.0]], dtype=complex)
SIGMA_P = np.array([[0.0, 0.0], [1.0, 0.0]], dtype=complex)

IDENTITY = np.array([[1, 0], [0, 1]])
Y = np.array([[0, -1j], [1j, 0]])


class WorkflowApi(Enum):
    """Available workflow APIs in jobs."""

    BOULDER = "boulder"
    FIRE = "fire"
    EXPERIMENTAL = "experimental"
