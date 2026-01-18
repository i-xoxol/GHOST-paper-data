import numpy as np
import matplotlib.pyplot as plt
import csv

# Set global font size for plots
plt.rcParams.update({'font.size': 14})

# --- Experiment C: Latency vs. Entropy Trade-off ---

def run_latency_experiment():
    print("Starting Experiment C: Latency vs. Entropy...")
    
    # Parameters
    # From previous experiment, we know Entropy corresponds roughly to H and B.
    # Let's map H to typical Latency.
    # Assumption: Internet latency between arbitrary P2P nodes is ~50-150ms.
    # Let's assume Mean Hop Latency = 100ms.
    # Processing delay (decryption/routing) = 10ms.
    
    mean_hop_latency = 100 # ms
    std_hop_latency = 30
    proc_delay = 10
    
    configs = [
        {'H': 3, 'B': 2, 'Entropy': 9.17},
        {'H': 3, 'B': 4, 'Entropy': 9.91},
        {'H': 4, 'B': 2, 'Entropy': 9.63},
        {'H': 4, 'B': 4, 'Entropy': 9.96},
        {'H': 5, 'B': 3, 'Entropy': 9.96}, 
        {'H': 5, 'B': 4, 'Entropy': 9.97},
    ]
    
    results = []
    
    for config in configs:
        H = config['H']
        
        # Monte Carlo simulation of Latency
        # Path length is exactly H.
        # Total Latency = Sum of H hops + H processing steps
        
        num_trials = 1000
        latencies = []
        for _ in range(num_trials):
            # Generate H random hop latencies
            hops = np.random.normal(mean_hop_latency, std_hop_latency, H)
            # Ensure no negative latency
            hops = np.maximum(hops, 10) 
            
            total_time = np.sum(hops) + (H * proc_delay)
            latencies.append(total_time)
            
        avg_latency = np.mean(latencies)
        p99_latency = np.percentile(latencies, 99)
        
        results.append({
            'H': H,
            'B': config['B'],
            'Entropy': config['Entropy'],
            'AvgLatency': avg_latency,
            'P99Latency': p99_latency
        })
        
        print(f"H={H}, B={config['B']} -> Avg Latency: {avg_latency:.2f}ms")

    # Save Results
    with open('results/results_latency.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['H', 'B', 'Entropy', 'AvgLatency', 'P99Latency'])
        writer.writeheader()
        writer.writerows(results)
        
    # Plot Entropy vs Latency
    entropies = [r['Entropy'] for r in results]
    latencies = [r['AvgLatency'] for r in results]
    
    plt.figure(figsize=(10, 6)) # Increased size
    plt.scatter(entropies, latencies, c='red', s=150) # Increased marker size
    
    # Label points
    for i, txt in enumerate(results):
        label = f"H{txt['H']}B{txt['B']}"
        plt.annotate(label, (entropies[i], latencies[i]), xytext=(5, 5), textcoords='offset points', fontsize=12)
        
    plt.xlabel('Anonymity (Shannon Entropy in Bits)')
    plt.ylabel('End-to-End Latency (ms)')
    plt.title('Trade-off: Privacy vs. Latency')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('Private Messenger/figures/results_latency_tradeoff.png')
    print("Experiment C Complete.")

# --- Experiment D: Network Saturation (Stress Test) ---

def run_saturation_experiment():
    print("\nStarting Experiment D: Network Saturation...")
    
    # Model:
    # A single bottleneck router or average node bandwidth.
    # Capacity: 5000 packets / second (P2P node)
    
    node_capacity_pps = 5000 
    
    # Scenario:
    # 1000 Users active.
    # Users send 1 message / second.
    # We vary the "Privacy Settings" (H, B) which changes overhead multiplier.
    
    num_users = 1000
    msg_rate = 1.0 # msg/sec
    
    # Test range of branching factors B (fixed H=4 for simplicity)
    # or just test different configs directly.
    
    configs = [
        {'H': 3, 'B': 2}, # Overhead = 2^3 = 8 pkts
        {'H': 3, 'B': 3}, # 27
        {'H': 4, 'B': 2}, # 16
        {'H': 4, 'B': 3}, # 81
        {'H': 5, 'B': 2}, # 32
        {'H': 5, 'B': 3}, # 243
        {'H': 4, 'B': 4}, # 256
        {'H': 5, 'B': 4}, # 1024 packets per msg!
    ]
    
    load_results = []
    
    for config in configs:
        H = config['H']
        B = config['B']
        
        # Calculate Packets Per Message (Overhead)
        # O = B^H (Approx)
        packets_per_msg = B ** H
        
        # Total Network Load (PPS) = Users * Rate * O
        total_load_pps = num_users * msg_rate * packets_per_msg
        
        # Drop Rate Calculation
        # Simple Queue Model: If Load > Capacity, Drop = (Load - Cap) / Load
        # In a P2P network, total capacity scales with users, BUT
        # specific links saturate. Let's model "Average Node Load".
        # In G.H.O.S.T, every user is a relay.
        # So Total Capacity = Num_Users * Node_Capacity.
        # Wait, if I am a user, I relay for others.
        # Total Network Capacity = 1000 users * 5000 pps = 5,000,000 pps.
        # Total Load = 1000 * 1 * 1024 = 1,024,000 pps.
        # It handles it easily?
        
        # Reviewer Comment: "Packet size would exponentially explode... overhead analysis misleading."
        # Actually, if Load is distributed perfectly, it scales.
        # BUT, the sender's uplink is the bottleneck.
        # Sender must upload B^H packets?
        # NO. Sender uploads B packets. Each of those sends B packets.
        # So Sender Load = B packets.
        # Relay Load = B packets.
        # Everyone sends B packets.
        # Total Packets in Flight = B^H.
        # Total Relays involved = (B^H - 1) / (B-1).
        
        # Bottleneck: The total number of hops consumed.
        # Let's model "Average Bandwidth Required per User" (in Mbps).
        # Packet size = 1KB (padded).
        # 1 pps = 8 Kbps.
        
        avg_bandwidth_mbps = (total_load_pps * 8 * 1024) / (num_users * 1000000) 
        # (Total Pkts * 8 bits * 1024 bytes) / Users / 1Mb
        
        # Wait, total_load_pps is total network traffic.
        # Divide by num_users to get "Average Relay Load" per user.
        
        avg_load_pps_per_user = total_load_pps / num_users
        
        # Drop Logic: If a user has 10 Mbps upload (~1250 pps of 1KB), do they saturate?
        limit_mbps = 10.0 # Typical upload speed
        limit_pps = (limit_mbps * 1000000) / (8 * 1024)
        
        drop_rate = 0.0
        if avg_load_pps_per_user > limit_pps:
            drop_rate = (avg_load_pps_per_user - limit_pps) / avg_load_pps_per_user
            
        print(f"Config H={H}, B={B} -> Load/User: {avg_load_pps_per_user:.1f} pps ({avg_bandwidth_mbps:.2f} Mbps). Drop: {drop_rate*100:.1f}%")
        
        load_results.append({
            'H': H, 'B': B, 
            'PPS': avg_load_pps_per_user,
            'Mbps': avg_bandwidth_mbps,
            'DropRate': drop_rate * 100
        })

    # Save Results
    with open('results/results_saturation.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['H', 'B', 'PPS', 'Mbps', 'DropRate'])
        writer.writeheader()
        writer.writerows(load_results)
        
    # Plot
    labels = [f"H{r['H']}B{r['B']}" for r in load_results]
    mbps = [r['Mbps'] for r in load_results]
    drops = [r['DropRate'] for r in load_results]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = 'tab:blue'
    ax1.set_xlabel('Configuration')
    ax1.set_ylabel('Bandwidth Req (Mbps)', color=color)
    ax1.bar(labels, mbps, color=color, alpha=0.6)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axhline(y=10, color='r', linestyle='--', label='10 Mbps Limit')
    
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Packet Drop Rate (%)', color=color)
    ax2.plot(labels, drops, color=color, marker='o', linewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0, 100)
    
    plt.title('Network Stress Test: Bandwidth vs. Drop Rate')
    fig.tight_layout()
    plt.savefig('Private Messenger/figures/results_saturation.png')
    print("Experiment D Complete.")

if __name__ == "__main__":
    run_latency_experiment()
    run_saturation_experiment()
