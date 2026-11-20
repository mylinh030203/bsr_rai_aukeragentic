"""Deterministic analytical metrics, including purity."""

from __future__ import annotations

import inspect

from app.services import analytics


def test_change_helpers():
    assert analytics.absolute_change(10, 12.5) == 2.5
    assert analytics.percentage_change(10, 12.5) == 25.0
    assert analytics.percentage_change(0, 12.5) is None
    assert analytics.return_over([100, 101, 102, 103], 2) == round((103 - 101) / 101 * 100, 6)
    assert analytics.return_over([100], 2) is None


def test_close_to_close_returns_handles_zero_base():
    assert analytics.close_to_close_returns([100, 110, 99]) == [0.1, -0.1]
    assert analytics.close_to_close_returns([0, 5]) == [None]


def test_moving_average_has_leading_gaps():
    assert analytics.moving_average([1, 2, 3, 4], 2) == [None, 1.5, 2.5, 3.5]
    assert analytics.moving_average([5], 1) == [5]


def test_volatility_is_zero_for_a_flat_series():
    assert analytics.annualized_volatility([100, 100, 100, 100]) == 0.0
    assert analytics.annualized_volatility([100]) is None


def test_volatility_is_positive_for_moves():
    value = analytics.annualized_volatility([100, 101, 99, 102, 98])
    assert value is not None and value > 0


def test_correlation_of_identical_series_is_one():
    assert analytics.correlation([1, 2, 3], [2, 4, 6]) == 1.0
    assert analytics.correlation([1, 2], [1, 2, 3]) is None
    assert analytics.correlation([1, 1, 1], [1, 2, 3]) is None


def test_spread_is_deterministic():
    assert analytics.spread(92.1, 78.42) == 13.68
    assert analytics.spread(92.1, 78.42) == analytics.spread(92.1, 78.42)


def test_forecast_errors_state_missing_actuals():
    assert analytics.forecast_error(80, None) == {
        "absolute_error": None,
        "percentage_error": None,
        "note": "actual missing",
    }
    assert analytics.forecast_error(80, 75)["absolute_error"] == 5
    assert analytics.forecast_error(80, 75)["percentage_error"] == round(5 / 75 * 100, 6)
    assert analytics.forecast_error(80, 0)["percentage_error"] is None


def test_aggregate_error_metrics_ignore_missing_actuals():
    pairs = [(80, 75), (78, None), (90, 100)]
    assert analytics.mae(pairs) == round((5 + 10) / 2, 6)
    assert analytics.mape(pairs) == round(((5 / 75) + (10 / 100)) / 2 * 100, 6)
    assert analytics.bias(pairs) == round(((80 - 75) + (90 - 100)) / 2, 6)
    assert analytics.mae([(80, None)]) is None
    assert analytics.mape([(80, 0)]) is None


def test_analytics_module_is_pure():
    source = inspect.getsource(analytics)
    for banned in ("import datetime", "from datetime", "flask", "sqlite3", "time."):
        assert banned not in source
