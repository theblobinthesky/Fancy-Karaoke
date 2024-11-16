import json
import numpy as np
import matplotlib.pyplot as plt

# Set the thinning factor
NUM_LINES = 500  # Adjust this value as needed

root = "song"
with open(f"{root}/tts.json", "r") as file:
    chapters = json.load(file)

for c, chapter in enumerate(chapters):
    audio_len = chapter["audio_len"]
    ft_len = chapter["ft_len"]

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
    
    # Draw thinned lines between the mapped points
    for a, f in zip(audio_to_thinned, ft_from_thinned):
        plt.plot([f, a], [1, 0], color='gray', alpha=0.5)
    
    # Customize the plot
    plt.xlabel('Index')
    plt.ylabel('Points')
    plt.title(f'Chapter {c}: Mapping from ft_len ({ft_len} points) to audio_len ({audio_len} points)')
    plt.yticks([1, 0], ['Feature Points', 'Audio Points'])
    plt.grid(True)
    plt.tight_layout()
    plt.show()