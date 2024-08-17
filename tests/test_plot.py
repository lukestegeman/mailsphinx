import matplotlib.pyplot as plt
import numpy as np

def plot_forecast_time_series(histogram=False):
    # Example data
    np.random.seed(42)
    time = np.arange(0, 100, 1)  # Time series data (e.g., could be datetime)
    values = np.sin(time / 10) + np.random.normal(scale=0.5, size=time.size)  # Corresponding values

    # Create figure and subplots with shared y-axis
    fig, ax = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [3, 1], 'wspace': 0}, sharey=True)

    # Left subplot: Time series scatter plot
    ax[0].scatter(time, values, color='b')
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Values')
    ax[0].set_title('Time Series Scatter Plot')
    ax[0].grid(True)  # Add grid

    # Right subplot: Histogram of values, rotated 90 degrees clockwise
    ax[1].hist(values, bins=bins, orientation='horizontal', color='orange')
    ax[1].set_xlabel('Frequency')
    ax[1].set_title('Histogram of Values')
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].grid(True)  # Add grid

    # Adjust the aspect ratio to match the Values axis on both plots
    ax[0].set_aspect(aspect='auto')
    ax[1].set_aspect(aspect='auto')

    # Ensure both subplots have the same Y-axis limits
    ax[1].set_ylim(ax[0].get_ylim())

    # Minimize space between plots
    plt.subplots_adjust(wspace=0)

    # Make the line between the graphs bold
    for spine in ax[0].spines.values():
        spine.set_linewidth(4)
    for spine in ax[1].spines.values():
        spine.set_linewidth(4)
    #ax[1].spines['left'].set_linewidth(4)





    # Adjust layout
    plt.tight_layout(pad=1.0)
    plt.savefig('test.jpg')


# Function to create the plot with specified width
def create_categorical_scatter_plot(plot_width):
    # Example data
    np.random.seed(42)
    categories = ['Hit', 'Miss', 'False Alarm', 'Correct Negative', 'Invalid']
    num_points = 1000  # Adjust the number of points as needed

    # Generate sample datetime range and random categories
    time_dates = pd.date_range(start='2024-01-01', periods=num_points, freq='H')
    values = np.random.choice(categories, size=num_points)

    # Define a color for each category
    category_colors = {
        'Hit': 'green',
        'Miss': 'red',
        'False Alarm': 'orange',
        'Correct Negative': 'blue',
        'Invalid': 'gray'
    }

    # Calculate counts for each category
    category_counts = {category: np.sum(np.array(values) == category) for category in categories}

    # Convert categorical values to numerical indices for plotting
    category_map = {category: idx for idx, category in enumerate(categories)}
    numeric_values = np.array([category_map[value] for value in values])
    colors = np.array([category_colors[value] for value in values])

    # Create figure and axis with specified width and a default height
    fig, ax = plt.subplots(figsize=(plot_width, 6))

    # Scatter plot with colors
    scatter = ax.scatter(time_dates, numeric_values, c=colors, s=10, alpha=0.7)

    # Set labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Categories')
    ax.set_title('Categorical Scatter Plot')

    # Reverse the order of the categories
    reversed_categories = list(reversed(categories))
    reverse_category_map = {category: idx for idx, category in enumerate(reversed_categories)}
    reverse_numeric_values = np.array([reverse_category_map[value] for value in values])

    # Set vertical ticks to be the reversed categories
    ax.set_yticks(range(len(reversed_categories)))
    ax.set_yticklabels(reversed_categories)

    # Format the x-axis to show datetime
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()  # Rotate dates for better readability

    # Add grid
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Create a legend
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=category_colors[cat], markersize=10, label=cat) for cat in categories]
    #ax.legend(handles=handles, title='Categories')

    # Add category counts to the right of the plot
    count_x_position = time_dates[-1] + pd.DateOffset(hours=1)  # Position text just to the right of the plot
    for idx, category in enumerate(reversed_categories):
        ax.text(count_x_position, idx, f'{category_counts[category]}', fontsize=12, verticalalignment='center')

    plt.tight_layout()
    plt.show()

# Example usage with a specified plot width
create_categorical_scatter_plot(plot_width=10)









