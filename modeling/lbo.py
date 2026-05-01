import numpy as np

class LBOEngine:
    """
    Institutional Leveraged Buyout (LBO) Model Engine.
    Calculates IRR, MOIC, and debt paydown dynamics.
    """
    
    def __init__(self, entry_multiple=10.0, exit_multiple=10.0, leverage_ratio=4.0, interest_rate=0.06):
        self.entry_multiple = entry_multiple
        self.exit_multiple = exit_multiple
        self.leverage_ratio = leverage_ratio
        self.interest_rate = interest_rate

    def run_lbo(self, ebitda, revenue, growth_rate, margin, exit_multiple=None, tax_rate=0.25, capex_pct=0.05, nwc_pct=0.02, years=5):
        # 1. Transaction Summary
        entry_enterprise_value = ebitda * self.entry_multiple
        total_debt = ebitda * self.leverage_ratio
        sponsor_equity = entry_enterprise_value - total_debt
        
        # 2. Operating Projections
        current_ebitda = ebitda
        current_rev = revenue
        debt_balance = total_debt
        
        ebitda_projections = []
        debt_projections = [debt_balance]
        fcf_projections = []
        
        for yr in range(1, years + 1):
            current_rev *= (1 + growth_rate)
            current_ebitda = current_rev * margin
            ebitda_projections.append(current_ebitda)
            
            # Interest Expense
            interest = debt_balance * self.interest_rate
            
            # Simplified FCF for Debt Paydown
            # FCF = EBITDA - Interest - Taxes - CapEx - Delta NWC
            taxable_income = current_ebitda - interest
            taxes = max(0, taxable_income * tax_rate)
            capex = current_rev * capex_pct
            nwc_change = (current_rev * growth_rate) * nwc_pct
            
            fcf_for_debt = current_ebitda - interest - taxes - capex - nwc_change
            
            # Pay down debt
            repayment = min(debt_balance, max(0, fcf_for_debt))
            debt_balance -= repayment
            debt_projections.append(debt_balance)
            fcf_projections.append(fcf_for_debt)
            
        # 3. Exit Summary
        final_exit_multiple = exit_multiple if exit_multiple is not None else self.exit_multiple
        exit_ebitda = ebitda_projections[-1]
        exit_enterprise_value = exit_ebitda * final_exit_multiple
        exit_equity_value = exit_enterprise_value - debt_projections[-1]
        
        # 4. Returns Analysis
        moic = exit_equity_value / sponsor_equity
        
        # Handle negative MOIC to avoid complex numbers in IRR calculation
        if moic > 0:
            irr = (moic ** (1 / years)) - 1
        else:
            irr = -1.0 # Total loss
        
        return {
            "entry_ev": entry_enterprise_value,
            "entry_equity": sponsor_equity,
            "exit_ev": exit_enterprise_value,
            "exit_equity": exit_equity_value,
            "moic": moic,
            "irr": irr * 100,
            "ebitda_path": ebitda_projections,
            "debt_path": debt_projections,
            "fcf_path": fcf_projections
        }

def simulate_lbo_monte_carlo(ebitda, revenue, growth_mean, growth_std, iterations=1000):
    """
    Monte Carlo simulation for LBO returns.
    """
    irrs = []
    moics = []
    
    engine = LBOEngine()
    
    for _ in range(iterations):
        growth = np.random.normal(growth_mean, growth_std)
        exit_mult = np.random.normal(10.0, 1.5)
        
        res = engine.run_lbo(ebitda, revenue, growth, margin=0.20, exit_multiple=exit_mult)
        irrs.append(res['irr'])
        moics.append(res['moic'])
        
    return {
        "irrs": irrs,
        "moics": moics,
        "mean_irr": np.mean(irrs),
        "mean_moic": np.mean(moics),
        "std_irr": np.std(irrs)
    }
