"""Mathematical and signal smoothing filters for jitter-free cursor tracking."""

import math
import time
from typing import Optional, Tuple


class LowPassFilter:
    """Standard 1st-order low-pass filter."""

    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
        self.y: Optional[float] = None
        self.s: Optional[float] = None

    def reset(self):
        self.y = None
        self.s = None

    def filter(self, value: float, alpha: Optional[float] = None) -> float:
        if alpha is not None:
            self.alpha = alpha
        if self.s is None:
            self.s = value
        else:
            self.s = self.alpha * value + (1.0 - self.alpha) * self.s
        self.y = self.s
        return self.y


class OneEuroFilter:
    """
    1€ Filter: Adaptive low-pass filter designed for real-time human-computer interaction.
    Dynamically balances jitter reduction when stationary with zero lag during rapid motion.
    
    References:
        Casiez, G., Roussel, N. and Vogel, D. (2012). 
        1 € filter: a simple speed-based low-pass filter for noisy input in interactive systems.
    """

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.007, d_cutoff: float = 1.0):
        """
        Args:
            min_cutoff: Minimum cutoff frequency (Hz). Lower values reduce jitter when still.
            beta: Speed coefficient. Higher values reduce lag during fast movements.
            d_cutoff: Cutoff frequency for derivative calculation (Hz).
        """
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        self.x_filter = LowPassFilter()
        self.dx_filter = LowPassFilter()
        self.last_time: Optional[float] = None

    def _alpha(self, rate: float, cutoff: float) -> float:
        tau = 1.0 / (2.0 * math.pi * cutoff)
        te = 1.0 / rate
        return 1.0 / (1.0 + tau / te)

    def reset(self):
        self.x_filter.reset()
        self.dx_filter.reset()
        self.last_time = None

    def filter(self, x: float, timestamp: Optional[float] = None) -> float:
        if timestamp is None:
            timestamp = time.perf_counter()

        if self.last_time is None:
            self.last_time = timestamp
            return self.x_filter.filter(x, 1.0)

        dt = timestamp - self.last_time
        self.last_time = timestamp

        # Clamp dt to prevent division by zero or extreme delta
        if dt <= 0.0001:
            rate = 60.0
        else:
            rate = 1.0 / dt

        # Estimate derivative (speed)
        prev_x = self.x_filter.s if self.x_filter.s is not None else x
        dx = (x - prev_x) * rate
        edx = self.dx_filter.filter(dx, self._alpha(rate, self.d_cutoff))

        # Dynamic cutoff frequency based on speed
        cutoff = self.min_cutoff + self.beta * abs(edx)
        return self.x_filter.filter(x, self._alpha(rate, cutoff))


class PointFilter2D:
    """Applies independent 1€ filters along X and Y axes for 2D screen tracking."""

    def __init__(self, min_cutoff: float = 1.2, beta: float = 0.015, d_cutoff: float = 1.0):
        self.fx = OneEuroFilter(min_cutoff=min_cutoff, beta=beta, d_cutoff=d_cutoff)
        self.fy = OneEuroFilter(min_cutoff=min_cutoff, beta=beta, d_cutoff=d_cutoff)

    def update_params(self, min_cutoff: float, beta: float):
        self.fx.min_cutoff = min_cutoff
        self.fx.beta = beta
        self.fy.min_cutoff = min_cutoff
        self.fy.beta = beta

    def reset(self):
        self.fx.reset()
        self.fy.reset()

    def filter(self, x: float, y: float, timestamp: Optional[float] = None) -> Tuple[float, float]:
        if timestamp is None:
            timestamp = time.perf_counter()
        smooth_x = self.fx.filter(x, timestamp)
        smooth_y = self.fy.filter(y, timestamp)
        return smooth_x, smooth_y
