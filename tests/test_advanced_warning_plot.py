import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create a figure and primary axis for dates
fig, ax1 = plt.subplots(figsize=(12, 6))

# Define the date range and example data
dates = pd.date_range(start="2024-01-01", end="2024-01-05", freq='D')
values = np.random.rand(len(dates))

# Plot the data with dates on the primary axis
ax1.plot(dates, values, 'o-', color='b')
ax1.set_xlabel('Date')
ax1.set_ylabel('Values')
ax1.xaxis.set_major_locator(mdates.DayLocator())
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax1.set_xlim(dates[0], dates[-1])

# Create a secondary x-axis for hours
ax2 = ax1.twiny()

# Define the start time and end time for the hours axis
start_time = datetime(2024, 1, 2, 0, 30, 32)
end_time = datetime(2024, 1, 4, 23, 59, 59)

# Generate time intervals including negative hours
hours_range = [start_time + timedelta(hours=i) for i in range(-24, int((end_time - start_time).total_seconds() // 3600) + 1)]

# Convert tick positions to hours from start_time
tick_positions_hours = [(t - start_time).total_seconds() / 3600 for t in hours_range]

# Calculate plot width in hours
xlim_hours = [tick_positions_hours[0], tick_positions_hours[-1]]
graph_width = xlim_hours[1] - xlim_hours[0]

# Determine a reasonable number of ticks (e.g., 10 to 15 ticks)
num_ticks = max(5, min(int(graph_width / 2), 15))

# Generate tick positions evenly spaced within the range
tick_positions = np.linspace(xlim_hours[0], xlim_hours[1], num_ticks)
tick_labels = [f"{int(tick)}h" for tick in tick_positions]

# Set the x-axis limits and labels for the secondary axis
ax2.set_xlim(hours_range[0], hours_range[-1])
ax2.set_xticks(tick_positions)  # Set evenly spaced ticks
ax2.set_xticklabels(tick_labels)  # Set labels for ticks
ax2.set_xlabel('Hours from Jan 02 00:30:32 UTC')

# Adjust positions to swap axes
ax2.spines['bottom'].set_position(('outward', 40))  # Move ax2 outward
ax1.spines['top'].set_position(('outward', 40))  # Move ax1 outward

# Ensure tight layout
plt.tight_layout()
plt.show()

