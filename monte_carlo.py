import numpy as np
import matplotlib.pyplot as plt
from modeling.dcf import enterprise_value

def run_monte_carlo(ticker, simulations=300):

    valuations = []

    for _ in range(simulations):

        growth_rate = np.random.normal(0.10, 0.02)
        discount_rate = np.random.normal(0.08, 0.01)

        growth_rate = max(0.02, min(growth_rate, 0.20))
        discount_rate = max(0.05, min(discount_rate, 0.15))

        val = enterprise_value(
            ticker,
            10,
            discount_rate,
            growth_rate,
            0.05
        )

        valuations.append(val)

    return valuations


def plot_simulation(valuations):

    fig, ax = plt.subplots()

    ax.hist(valuations, bins=30)
    ax.set_title("Monte Carlo Valuation Distribution")
    ax.set_xlabel("Enterprise Value")
    ax.set_ylabel("Frequency")

    return fig


def get_statistics(valuations):

    valuations = np.array(valuations)

    return {
        "mean": float(valuations.mean()),
        "median": float(np.median(valuations)),
        "min": float(valuations.min()),
        "max": float(valuations.max()),
        "p10": float(np.percentile(valuations, 10)),
        "p90": float(np.percentile(valuations, 90)),
    }