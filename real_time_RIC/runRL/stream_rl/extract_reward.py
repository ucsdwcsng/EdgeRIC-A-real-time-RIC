import re
import csv

# Open the log file
with open('logfile.log', 'r') as log_file:
    log_data = log_file.read()

# Define a regular expression pattern to match the reward attributes
pattern = re.compile(r'\breward\b.*?\d+\.\d+')

# Use the findall method to extract all instances of the pattern from the log data
reward_matches = re.findall(pattern, log_data)

# Convert the extracted strings to floating point numbers
reward_values = [float(match.split()[-1]) for match in reward_matches]

# Write the extracted reward values to a CSV file
with open('rewards.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows([[value] for value in reward_values])