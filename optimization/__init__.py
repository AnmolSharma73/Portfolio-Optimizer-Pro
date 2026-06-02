"""
Portfolio Optimization Engine
=============================

This package provides a comprehensive suite of portfolio optimization tools:
- MarkowitzOptimizer: Classic mean-variance optimization (max Sharpe, min vol, target return/risk)
- EfficientFrontierCalculator: Compute and visualize the efficient frontier
- MonteCarloSimulator: Monte Carlo portfolio simulation and future price projection
- RiskParityOptimizer: Equal risk contribution portfolio construction
- BlackLittermanOptimizer: Black-Litterman model with investor views
"""

from .markowitz import MarkowitzOptimizer
from .efficient_frontier import EfficientFrontierCalculator
from .monte_carlo import MonteCarloSimulator
from .risk_parity import RiskParityOptimizer
from .black_litterman import BlackLittermanOptimizer

__all__ = [
    "MarkowitzOptimizer",
    "EfficientFrontierCalculator",
    "MonteCarloSimulator",
    "RiskParityOptimizer",
    "BlackLittermanOptimizer",
]
