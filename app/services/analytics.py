"""Pure deterministic market analytics.

No clock, session or database access: given the same inputs these functions
always return the same values, so every number in the product is reproducible.
"""

from __future__ import annotations

import math


def absolute_change(previous: float, current: float) -> float:
    return round(current - previous, 6)


def percentage_change(previous: float, current: float) -> float | None:
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 6)


def close_to_close_returns(values: list[float]) -> list[float]:
    """Simple period-over-period returns; a zero base yields None for that step."""
    returns: list[float] = []
    for previous, current in zip(values, values[1:]):
        if previous == 0:
            returns.append(None)
        else:
            returns.append((current - previous) / previous)
    return returns


def return_over(values: list[float], sessions: int) -> float | None:
    """Percentage change across the last ``sessions`` observations."""
    if sessions <= 0 or len(values) <= sessions:
        return None
    return percentage_change(values[-1 - sessions], values[-1])


def moving_average(values: list[float], window: int) -> list[float | None]:
    if window <= 0:
        raise ValueError("window must be positive")
    out: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            out.append(None)
            continue
        chunk = values[index + 1 - window : index + 1]
        out.append(round(sum(chunk) / window, 6))
    return out


def annualized_volatility(values: list[float], periods_per_year: int = 252) -> float | None:
    """Annualized standard deviation of daily log returns, in percent."""
    if len(values) < 3:
        return None
    if any(value <= 0 for value in values):
        return None
    log_returns = [math.log(current / previous) for previous, current in zip(values, values[1:])]
    mean = sum(log_returns) / len(log_returns)
    variance = sum((value - mean) ** 2 for value in log_returns) / (len(log_returns) - 1)
    return round(math.sqrt(variance) * math.sqrt(periods_per_year) * 100, 6)


def correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    mean_left = sum(left) / len(left)
    mean_right = sum(right) / len(right)
    covariance = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right))
    variance_left = sum((a - mean_left) ** 2 for a in left)
    variance_right = sum((b - mean_right) ** 2 for b in right)
    if variance_left == 0 or variance_right == 0:
        return None
    return round(covariance / math.sqrt(variance_left * variance_right), 6)


def spread(first: float, second: float, multiplier: float = 1.0) -> float:
    return round(first - second * multiplier, 6)


def forecast_error(forecast: float, actual: float | None) -> dict:
    """Absolute and percentage error; a missing actual is stated, never zero."""
    if actual is None:
        return {"absolute_error": None, "percentage_error": None, "note": "actual missing"}
    absolute = abs(forecast - actual)
    if actual == 0:
        return {
            "absolute_error": round(absolute, 6),
            "percentage_error": None,
            "note": "actual is zero",
        }
    return {
        "absolute_error": round(absolute, 6),
        "percentage_error": round(absolute / abs(actual) * 100, 6),
        "note": None,
    }


def _paired(pairs: list[tuple[float, float | None]]) -> list[tuple[float, float]]:
    return [(forecast, actual) for forecast, actual in pairs if actual is not None]


def mae(pairs: list[tuple[float, float | None]]) -> float | None:
    usable = _paired(pairs)
    if not usable:
        return None
    return round(sum(abs(forecast - actual) for forecast, actual in usable) / len(usable), 6)


def mape(pairs: list[tuple[float, float | None]]) -> float | None:
    usable = [(forecast, actual) for forecast, actual in _paired(pairs) if actual != 0]
    if not usable:
        return None
    return round(
        sum(abs(forecast - actual) / abs(actual) for forecast, actual in usable) / len(usable) * 100,
        6,
    )


def bias(pairs: list[tuple[float, float | None]]) -> float | None:
    usable = _paired(pairs)
    if not usable:
        return None
    return round(sum(forecast - actual for forecast, actual in usable) / len(usable), 6)
