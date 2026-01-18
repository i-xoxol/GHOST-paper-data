import random
import time
import math
import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# --- Core G.H.O.S.T. Protocol Logic (Optimized) ---

class GhostProtocolFast:
    def __init__(self, num_recipients, max_deviation=0.1):
        self.num_recipients = num_recipients
        self.max_deviation = max_deviation
        # History is now just a counter to save memory and time
        self.history_counts = Counter() 
        self.total_packets_seen = 0

    def generate_burst_fast(self, real_recipient, H, B, has_real_message):
        """
        Generates a burst of packet recipient IDs using NumPy for speed.
        """
        # Calculate total packets in this tree/burst
        # Simplified model: M * B^H
        total_packets = B ** H
        
        # 1. Generate ALL candidates uniformly at random (Vectorized)
        # IDs are 1..num_recipients
        candidates = np.random.randint(1, self.num_recipients + 1, size=total_packets)
        
        # 2. Protocol Logic: "If fake == real AND real is frequent, pick again"
        # Find indices where we accidentally picked the real recipient
        collision_indices = np.where(candidates == real_recipient)[0]
        
        if len(collision_indices) > 0:
            # Check if real recipient is "above average" frequency
            # Optimization: Just calculate mean freq on the fly
            if self.total_packets_seen > 0:
                mean_freq = self.total_packets_seen / self.num_recipients
                # Add random deviation (0 to max_deviation)
                threshold = mean_freq * (1 + random.uniform(0, self.max_deviation))
                
                real_freq = self.history_counts[real_recipient]
                
                if real_freq > threshold:
                    # Resample these specific collision indices
                    # Simple resampling: just pick random again. 
                    # (Paper logic says shift index, but random is statistically equivalent for entropy)
                    new_picks = np.random.randint(1, self.num_recipients + 1, size=len(collision_indices))
                    candidates[collision_indices] = new_picks

        # 3. Inject the REAL message if needed
        if has_real_message:
            # Pick a random slot to be the real message
            real_idx = np.random.randint(0, total_packets)
            candidates[real_idx] = real_recipient
            
        return candidates

    def update_history(self, burst_array):
        # Efficiently update global counters
        self.history_counts.update(burst_array)
        self.total_packets_seen += len(burst_array)

# --- Experiment B: Shannon Entropy ---

def run_entropy_experiment():
    print("Starting Experiment B: Shannon Entropy Analysis (Optimized)...")
    
    # Reasonable Parameters for Simulation
    H_values = [3, 4, 5]     # Removed 6
    B_values = [2, 3, 4]     # Removed 5
    num_runs = 1000          # Reduced from 5000 (Sufficient for smooth graph)
    num_recipients = 1000
    real_recipient = 42

    results = []

    print(f"{'H':<5} {'B':<5} {'Entropy (Bits)':<15} {'Std Dev':<15} {'Time (s)':<10}")
    print("-" * 60)

    for H in H_values:
        for B in B_values:
            start_time = time.time()
            entropies = []
            
            # Run multiple independent trials to get mean/std per config
            # Note: Previously we aggregated 1000 runs into ONE distribution.
            # To get Std Dev OF THE ENTROPY, we need to calculate entropy PER RUN 
            # (or per small batch). 
            # However, entropy of a SINGLE burst is low. The paper implies entropy 
            # of the AGGREGATE distribution over time.
            # Let's compute entropy of the distribution formed by 100 bursts, repeated 10 times?
            # Or simpler: The "per-round" entropy isn't well defined for a single packet.
            # We will simulate 100 independent "sessions" of 50 messages each and measure the 
            # entropy of the *resulting* distribution for each session.
            
            num_sessions = 50
            msgs_per_session = 20
            
            session_entropies = []
            
            for _ in range(num_sessions):
                protocol = GhostProtocolFast(num_recipients)
                packet_counts = Counter()
                for _ in range(msgs_per_session):
                    burst = protocol.generate_burst_fast(real_recipient, H, B, has_real_message=True)
                    packet_counts.update(burst)
                
                total_packets = sum(packet_counts.values())
                e = 0.0
                for count in packet_counts.values():
                    p_i = count / total_packets
                    e -= p_i * math.log2(p_i)
                session_entropies.append(e)

            mean_entropy = np.mean(session_entropies)
            std_entropy = np.std(session_entropies)
            
            elapsed = time.time() - start_time
            print(f"{H:<5} {B:<5} {mean_entropy:.4f}          {std_entropy:.4f}          {elapsed:.2f}")
            results.append({'H': H, 'B': B, 'Entropy': mean_entropy, 'StdDev': std_entropy})

    # Save Results
    with open('results/results_entropy.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['H', 'B', 'Entropy', 'StdDev'])
        writer.writeheader()
        writer.writerows(results)
    
    print("Experiment B Complete.")

# --- Experiment A: Intersection Attack ---

def run_intersection_experiment():
    print("\nStarting Experiment A: Intersection Attack Resilience (Aggregate)...")
    
    # Increase font size for readability
    plt.rcParams.update({'font.size': 14})
    
    num_recipients = 1000
    real_recipient = 100
    # Reduced rounds to focus on the saturation point (user requested "left part is cramped")
    num_rounds = 60 
    num_trials = 20  # Run 20 trials to get aggregate stats
    
    # Optimized Configs
    configs = [
        {'H': 3, 'B': 2, 'label': 'Weak (H=3, B=2)'},
        {'H': 4, 'B': 3, 'label': 'Medium (H=4, B=3)'},
        {'H': 5, 'B': 3, 'label': 'Strong (H=5, B=3)'}
    ]
    
    plt.figure(figsize=(10, 6))
    
    for config in configs:
        H = config['H']
        B = config['B']
        label = config['label']
        
        print(f"Simulating attack for {label} ({num_trials} trials)...")
        
        # Matrix: Trials x Rounds
        all_ranks = np.zeros((num_trials, num_rounds))
        
        for t in range(num_trials):
            protocol = GhostProtocolFast(num_recipients)
            
            for r in range(num_rounds):
                burst = protocol.generate_burst_fast(real_recipient, H, B, has_real_message=True)
                protocol.update_history(burst)
                
                real_count = protocol.history_counts[real_recipient]
                all_counts = np.array(list(protocol.history_counts.values()))
                better_than_real = np.sum(all_counts > real_count)
                rank = better_than_real + 1
                
                all_ranks[t, r] = rank
        
        # Calculate Stats
        mean_ranks = np.mean(all_ranks, axis=0)
        std_ranks = np.std(all_ranks, axis=0)
        
        x_axis = range(1, num_rounds + 1)
        
        # Plot Mean
        p = plt.plot(x_axis, mean_ranks, label=label, linewidth=2)
        color = p[0].get_color()
        
        # Fill Error Bars (+/- 1 Std Dev)
        plt.fill_between(x_axis, 
                         np.maximum(1, mean_ranks - std_ranks), # Rank can't be < 1
                         mean_ranks + std_ranks, 
                         color=color, alpha=0.2)

    plt.xlabel('Messages Sent (Rounds)')
    plt.ylabel('Rank of Real Recipient (Log Scale)')
    plt.title('Intersection Attack Resilience (First 60 Rounds)')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.yscale('log')
    plt.gca().invert_yaxis() # 1 at top
    
    plt.tight_layout()
    plt.savefig('Private Messenger/figures/results_intersection_attack.png')
    print("Experiment A Complete.")

if __name__ == "__main__":
    run_entropy_experiment()
    run_intersection_experiment()