import matplotlib.pyplot as plt
import csv
import random

# Set global font size for plots
plt.rcParams.update({'font.size': 14})

class User:
    def __init__(self, uid, user_type, initial_balance=1000):
        self.uid = uid
        self.type = user_type
        self.balance = initial_balance
        self.balance_history = [initial_balance]
        
        # Configure behavior based on type
        if user_type == 'Rich':
            # Sends frequently, rarely relays
            self.msg_prob = 0.8 # Probability to send per minute
            self.relay_uptime = 0.1 # 10% chance to be online for relaying
            self.privacy_pref = {'H': 5, 'B': 4} # High cost
        else: # Student/Poor
            # Sends rarely, always relays
            self.msg_prob = 0.05 
            self.relay_uptime = 0.95
            self.privacy_pref = {'H': 3, 'B': 2} # Low cost

    def step(self):
        # 1. Spending (Sending)
        spent = 0
        if random.random() < self.msg_prob:
            # Calculate Cost: Cost = Total Packets Generated
            # Because you pay for the burden you put on network
            h = self.privacy_pref['H']
            b = self.privacy_pref['B']
            cost = b ** h
            
            # Can I afford it?
            if self.balance >= cost:
                self.balance -= cost
                spent = cost
        
        # 2. Earning (Relaying)
        # Simplified: If I am online, I might get picked to relay.
        # Probability depends on network demand.
        earned = 0
        if random.random() < self.relay_uptime:
            # Assume constant network background noise
            # I get picked X times per minute.
            # Let's say average relay load is 10 packets/min
            msgs_relayed = random.randint(5, 20)
            reward_per_msg = 1
            earned = msgs_relayed * reward_per_msg
            self.balance += earned
            
        self.balance_history.append(self.balance)
        return spent, earned

def run_economics_experiment():
    print("Starting Experiment E: Economic Viability...")
    
    num_minutes = 60 * 24 # 24 Hours
    
    # Create Population
    rich_user = User(1, 'Rich', initial_balance=5000)
    student_user = User(2, 'Student', initial_balance=100)
    
    print(f"Simulating {num_minutes} minutes...")
    
    for t in range(num_minutes):
        rich_user.step()
        student_user.step()
        
    # Plotting
    time_axis = range(num_minutes + 1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(time_axis, rich_user.balance_history, label='Rich User (High Spend, Low Relay)', color='red', linewidth=2)
    plt.plot(time_axis, student_user.balance_history, label='Student User (Low Spend, High Relay)', color='green', linewidth=2)
    
    plt.xlabel('Time (Minutes)')
    plt.ylabel('Token Balance')
    plt.title('24-Hour Economic Simulation: Sustainability')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('Private Messenger/figures/results_economics.png')
    
    # Analyze Survival
    rich_final = rich_user.balance_history[-1]
    student_final = student_user.balance_history[-1]
    
    print(f"Rich User Final Balance: {rich_final}")
    print(f"Student User Final Balance: {student_final}")
    
    # Save CSV
    with open('results/results_economics.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time', 'RichBalance', 'StudentBalance'])
        for t in range(len(time_axis)):
            writer.writerow([t, rich_user.balance_history[t], student_user.balance_history[t]])
            
    print("Experiment E Complete.")

if __name__ == "__main__":
    run_economics_experiment()
