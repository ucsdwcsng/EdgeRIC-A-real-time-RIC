import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a DataFrame
df = pd.read_csv('training_curve.csv')

# Plotting the training curve for 'reward_mean'
plt.figure(figsize=(10, 5))  # Set the figure size
plt.plot(df['train_step'], df['reward_mean'], label='Reward Mean', color='blue', marker='o')
plt.title('Training Curve for Reward Mean')  # Title of the plot
plt.xlabel('Train Step')  # X-axis label
plt.ylabel('Reward Mean')  # Y-axis label
plt.grid(True)  # Enable grid for better readability
plt.legend()  # Show legend
plt.show()  # Display the plot
