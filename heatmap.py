import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from modeling.dcf import enterprise_value

def generate_heatmap(ticker):

    discount_rates = np.linspace(0.06, 0.12, 5)
    growth_rates = np.linspace(0.05, 0.15, 5)

    values = np.zeros((len(growth_rates), len(discount_rates)))

    for i, g in enumerate(growth_rates):
        for j, d in enumerate(discount_rates):

            val = enterprise_value(
                ticker,
                10,
                d,
                g,
                0.05
            )

            values[i, j] = val / 1e12

    fig, ax = plt.subplots()

    sns.heatmap(
        values,
        xticklabels=[f"{d:.2f}" for d in discount_rates],
        yticklabels=[f"{g:.2f}" for g in growth_rates],
        annot=True
    )

    ax.set_xlabel("Discount Rate")
    ax.set_ylabel("Growth Rate")
    ax.set_title("DCF Sensitivity Heatmap (Trillions)")

    return fig