import numpy as np
from modeling.dcf import enterprise_value

def run_monte_carlo(ticker, simulations=500, growth_mean=0.12, growth_std=0.03, wacc_mean=0.08, wacc_std=0.01):
    """
    Institutional Grade Monte Carlo Simulation.
    Models growth and WACC as stochastic variables to generate a valuation distribution.
    """
    valuations = []

    # Vectorized simulation for performance
    growth_rates = np.random.normal(growth_mean, growth_std, simulations)
    discount_rates = np.random.normal(wacc_mean, wacc_std, simulations)
    
    # Clipped to realistic bounds
    growth_rates = np.clip(growth_rates, 0.01, 0.30)
    discount_rates = np.clip(discount_rates, 0.04, 0.20)

    for i in range(simulations):
        val = enterprise_value(
            ticker,
            10,
            discount_rates[i],
            growth_rates[i],
            0.03 # Terminal growth
        )
        valuations.append(val)

    return np.array(valuations)

def get_statistics(valuations):
    """
    Calculates institutional risk metrics.
    """
    if len(valuations) == 0:
        return {}
        
    return {
        "mean": float(np.mean(valuations)),
        "median": float(np.median(valuations)),
        "std": float(np.std(valuations)),
        "min": float(np.min(valuations)),
        "max": float(np.max(valuations)),
        "p10": float(np.percentile(valuations, 10)),
        "p90": float(np.percentile(valuations, 90)),
        "var_95": float(np.percentile(valuations, 5)), # Value at Risk
        "upside_prob": float(np.mean(valuations > np.median(valuations))) # Probability of upside
    }