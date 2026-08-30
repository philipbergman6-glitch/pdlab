"""Shared fixtures for the pdlab test suite."""

from __future__ import annotations

import numpy as np
import pytest

from pdlab.game import PayoffMatrix


@pytest.fixture
def axelrod() -> PayoffMatrix:
    """Canonical (T, R, P, S) = (5, 3, 1, 0) payoffs."""
    return PayoffMatrix.axelrod()


@pytest.fixture
def rng() -> np.random.Generator:
    return np.random.default_rng(12345)
