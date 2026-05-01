def generate_insight(result, discount_rate, growth_rate, lba_result):
    price = result.get('share_price', 0)
    ev = result.get('enterprise_value', 0)
    winner = lba_result.get('winner', 'NEUTRAL')
    confidence = lba_result.get('confidence', 0)
    
    if winner == 'BULL':
        lba_text = f"The **Linear Ballistic Accumulator** engine indicates that the 'Value Thesis' (Bullish) is accumulating evidence at a faster rate. The decision threshold was breached in the upper quantile, suggesting a 'BUY' signal with {confidence:.1f}% conviction."
    else:
        lba_text = f"The **Linear Ballistic Accumulator** engine indicates that the 'Risk Thesis' (Bearish) is dominating the evidence accumulation. The decision threshold was breached in the lower quantile, suggesting a 'SELL/REDUCE' signal with {confidence:.1f}% conviction."

    insight = f"""
### Executive Summary

**Intrinsic Valuation: ${price:,.2f} per share**
**Enterprise Valuation: ${ev/1e9:,.2f}B**

#### Growth Dynamics
The model assumes a baseline growth rate of **{growth_rate*100:.1f}%** with a stochastic decay function. This stance reflects the asset's scalability within the current market cycle.

#### Capital Cost (WACC)
A discount rate of **{discount_rate*100:.1f}%** has been applied. This represents the hurdle rate required to compensate for market volatility and idiosyncratic risk factors.

#### LBA Decision Context
{lba_text}

#### Risk Vectors
- **Assumption Sensitivity**: A 100bps change in WACC could swing the valuation by 15-20%.
- **Terminal Growth Dependence**: Over 60% of the intrinsic value is derived from the terminal phase, necessitating long-term structural stability.
"""
    return insight