import json
import numpy as np
import matplotlib.pyplot as plt

# Set the thinning factor
NUM_LINES = 500  # Adjust this value as needed

root = "song"
with open(f"{root}/tts.json", "r") as file:
    chapters = json.load(file)

for c, chapter in enumerate(chapters):
    # audio_len = chapter["audio_len"]
    # ft_len = chapter["ft_len"]

    time_warp = np.load(f"{root}/tts-joins/{c}.tw")
    time_warp = np.random.permutation(time_warp)

    audio_to, ft_from = time_warp.T

    # Apply thinning factor
    audio_to_thinned = audio_to[:NUM_LINES]
    ft_from_thinned = ft_from[:NUM_LINES]

    plt.figure(figsize=(14, 6))
    
    # Plot the audio points on the upper line (y=1)
    plt.scatter(audio_to, np.zeros_like(audio_to), color='blue', alpha=0.3, label='Audio Points')
    
    # Plot the feature points on the bottom line (y=0)
    plt.scatter(ft_from, np.ones_like(ft_from), color='red', alpha=0.3, label='Feature Points')
    
    # Calculate local density of audio_to_thinned
    num_bins = 100  # Adjust as needed
    hist, bin_edges = np.histogram(audio_to_thinned, bins=num_bins)
    bin_indices = np.digitize(audio_to_thinned, bins=bin_edges) - 1  # bins are 0-based

    # Ensure bin indices are within valid range
    bin_indices = np.clip(bin_indices, 0, num_bins - 1)
    bin_counts = hist[bin_indices]

    max_count = bin_counts.max()
    min_count = bin_counts.min()

    # Avoid division by zero
    if max_count == min_count:
        alphas = np.full_like(bin_counts, 0.45)  # Use a constant alpha
    else:
        normalized_counts = (bin_counts - min_count) / (max_count - min_count)
        inverted_counts = 1 - normalized_counts
        min_alpha = 0.1
        max_alpha = 0.8
        alphas = min_alpha + inverted_counts * (max_alpha - min_alpha)

    # Draw thinned lines between the mapped points with variable transparency
    for a, f, alpha in zip(audio_to_thinned, ft_from_thinned, alphas):
        plt.plot([f, a], [1, 0], color='gray', alpha=alpha)
    
    # Customize the plot
    plt.xlabel('Index')
    plt.ylabel('Points')
    plt.yticks([0, 1], ["Audio Points", "Feature Points"])
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()