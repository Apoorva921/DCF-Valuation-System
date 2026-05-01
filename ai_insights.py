def generate_insight(result, discount_rate, growth_rate):

    price = result['share_price']

    insight = f"""
Intrinsic Value: ${price:.2f} per share

Key Insights:
- Growth Rate: {growth_rate*100:.1f}%
- Discount Rate: {discount_rate*100:.1f}%

Analysis:
- Higher growth increases valuation significantly.
- Higher discount rate reduces valuation.
- Terminal value contributes heavily to final valuation.

Risk:
- Small assumption changes can cause large valuation swings.
"""

    return insight