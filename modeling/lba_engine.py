import numpy as np

class LBAEngine:
    """
    Linear Ballistic Accumulator (LBA) Engine for Financial Decision Intelligence.
    Models the 'race' between Bullish and Bearish evidence accumulators.
    """
    
    def __init__(self, threshold=100, noise=2.0):
        self.threshold = threshold
        self.noise = noise
        
    def simulate_decision(self, bullish_drift, bearish_drift, iterations=500):
        """
        Simulates the decision process.
        bullish_drift: Mean evidence for 'Buy' (biased by DCF Upside)
        bearish_drift: Mean evidence for 'Sell' (biased by Risk/Overvaluation)
        """
        
        times = []
        winners = []
        bull_paths = []
        bear_paths = []
        
        for _ in range(iterations):
            # Sample drift rates for this specific trial (stochasticity)
            v_bull = np.random.normal(bullish_drift, self.noise)
            v_bear = np.random.normal(bearish_drift, self.noise)
            
            # Start points (random bias)
            start_bull = np.random.uniform(0, 20)
            start_bear = np.random.uniform(0, 20)
            
            # Time to hit threshold: (threshold - start) / drift
            # Must be positive
            t_bull = (self.threshold - start_bull) / max(0.01, v_bull)
            t_bear = (self.threshold - start_bear) / max(0.01, v_bear)
            
            if t_bull < t_bear:
                times.append(t_bull)
                winners.append("BULL")
            else:
                times.append(t_bear)
                winners.append("BEAR")
                
            # Store some sample paths for visualization (first 5)
            if _ < 5:
                steps = 50
                t_max = min(t_bull, t_bear) * 1.2
                time_steps = np.linspace(0, t_max, steps)
                bull_paths.append(start_bull + v_bull * time_steps)
                bear_paths.append(start_bear + v_bear * time_steps)
        
        # Calculate Confidence Score
        bull_wins = winners.count("BULL")
        confidence = (bull_wins / iterations) * 100
        
        return {
            "winner": "BULL" if confidence > 50 else "BEAR",
            "confidence": confidence if confidence > 50 else (100 - confidence),
            "mean_latency": np.mean(times),
            "paths": {"bull": bull_paths, "bear": bear_paths},
            "raw_data": {"times": times, "winners": winners}
        }

def run_lba_analysis(upside_pct, volatility):
    """
    Maps DCF upside and market volatility to LBA drift rates.
    """
    # High upside = High bullish drift
    # High volatility = High noise in decision
    
    bull_drift = 5.0 + (upside_pct / 10.0)
    bear_drift = 5.0 - (upside_pct / 20.0)
    
    engine = LBAEngine(threshold=150, noise=volatility * 10)
    return engine.simulate_decision(bull_drift, bear_drift)
