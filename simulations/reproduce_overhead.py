import matplotlib.pyplot as plt
import numpy as np

# Set global font size for plots
plt.rcParams.update({'font.size': 14})

def generate_overhead_plot():
    H_values = np.array([2, 3, 4, 5, 6])
    B_values = [2, 3, 4, 5]
    
    plt.figure(figsize=(10, 6))
    
    for B in B_values:
        overhead = B ** H_values
        plt.plot(H_values, overhead, marker='o', label=f'Branching Factor B={B}', linewidth=2)
        
    plt.xlabel('Hop Depth (H)')
    plt.ylabel('Overhead (Packets per Message)')
    plt.yscale('log')
    plt.title('Communication Overhead vs. Privacy Parameters')
    plt.grid(True, which="both", ls="-")
    plt.legend()
    plt.tight_layout()
    
    # Save to the specific file used in the paper
    output_path = 'Private Messenger/figures/overhead_vs_privacy_improved.png'
    plt.savefig(output_path)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_overhead_plot()
