"""Unit tests for OneEuroFilter and PointFilter2D."""

import time
import pytest
from utils.filter import LowPassFilter, OneEuroFilter, PointFilter2D


def test_low_pass_filter():
    lpf = LowPassFilter(alpha=0.5)
    assert lpf.filter(10.0) == 10.0
    val2 = lpf.filter(20.0)
    assert val2 == 15.0  # 0.5 * 20 + 0.5 * 10
    lpf.reset()
    assert lpf.s is None


def test_one_euro_filter_stationary():
    """Stationary input should filter jitter smoothly without drift."""
    f = OneEuroFilter(min_cutoff=1.0, beta=0.01)
    base_time = 1000.0

    # Initial value
    v0 = f.filter(100.0, timestamp=base_time)
    assert v0 == 100.0

    # Tiny jitter fluctuations around 100.0
    outputs = []
    for i in range(1, 20):
        t = base_time + i * 0.033  # ~30 FPS
        noisy_val = 100.0 + (0.5 if i % 2 == 0 else -0.5)
        filtered = f.filter(noisy_val, timestamp=t)
        outputs.append(filtered)

    # Filtered output should remain very close to 100
    for out in outputs:
        assert abs(out - 100.0) < 0.6


def test_one_euro_filter_fast_motion():
    """Rapid motion should increase cutoff and track fast without excessive lag."""
    f = OneEuroFilter(min_cutoff=1.0, beta=0.05)
    base_time = 1000.0
    f.filter(0.0, timestamp=base_time)

    # Big jump after 33ms
    v_jump = f.filter(500.0, timestamp=base_time + 0.033)
    # Because beta is active, it should jump significantly towards 500
    assert v_jump > 150.0


def test_point_filter_2d():
    pf = PointFilter2D(min_cutoff=1.2, beta=0.02)
    t0 = 100.0
    x, y = pf.filter(50.0, 80.0, timestamp=t0)
    assert x == 50.0
    assert y == 80.0

    x2, y2 = pf.filter(52.0, 82.0, timestamp=t0 + 0.033)
    assert abs(x2 - 51.0) < 2.0
    assert abs(y2 - 81.0) < 2.0

    pf.reset()
    assert pf.fx.last_time is None
