import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

# Create a date range
start_date = "2023-01-01"
end_date = "2023-01-10"
dates = pd.date_range(start=start_date, end=end_date, freq="D")
y = np.sin(np.linspace(0, 10, len(dates)))

# Desired pixels per tick (e.g., 100 pixels between each tick)
desired_pixel_distance = 100

# Calculate figure size
dpi = 100  # Dots per inch for the figure
num_ticks = len(dates)  # Number of ticks equals the number of dates in the range
figure_width_in_pixels = num_ticks * desired_pixel_distance
figure_width_in_inches = figure_width_in_pixels / dpi

# Create the figure and axis
fig, ax = plt.subplots(figsize=(figure_width_in_inches, 10), dpi=dpi)

# Plot the data
ax.plot(dates, y)

# Set major ticks to be one day apart using a DayLocator
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))

# Format the ticks as dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

# Optionally, rotate and align the tick labels
plt.xticks(rotation=45, ha="right")

plt.xlim([min(dates), max(dates)])




# Adjust layout to ensure labels fit
plt.tight_layout()

ax.set_position([0.5, 0.6, 0.5, 0.6])


# Display the plot
plt.savefig('test.jpg')
