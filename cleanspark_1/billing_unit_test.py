"""Unit test suite for clsk.billing."""

from math import isclose

import pytest

import billing


def test_energy_charge():  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = billing._get_data()
    # Act --------------------------------------------------------------------
    result = billing.energy_charge(data)
    # Assert -----------------------------------------------------------------
    assert isclose(result, 7429.879999999999, rel_tol=1e-4)


def test_demand_charge():  # noqa: D103
    # Arrange ----------------------------------------------------------------
    data = billing._get_data()
    # Act --------------------------------------------------------------------
    result = billing.demand_charge(data)
    # Assert -----------------------------------------------------------------
    assert isclose(result, 2240.0, rel_tol=1e-4)
