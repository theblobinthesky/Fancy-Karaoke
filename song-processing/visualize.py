import json
import numpy as np
import matplotlib.pyplot as plt

# Set the thinning factor
THINNING_FACTOR = 2000  # Adjust this value as needed

root = "song"
with open(f"{root}/tts.json", "r") as file:
    chapters = json.load(file)

for c, chapter in enumerate(chapters):
    audio_len = chapter["audio_len"]
    ft_len = chapter["ft_len"]

    time_warp = np.load(f"{root}/tts-joins/{c}.tw")
    audio_to, ft_from = time_warp.T

    # Apply thinning factor
    audio_to_thinned = audio_to[::THINNING_FACTOR]
    ft_from_thinned = ft_from[::THINNING_FACTOR]

    plt.figure(figsize=(14, 6))
    
    # Plot the audio points on the upper line (y=1)
    plt.scatter(audio_to, np.ones_like(audio_to), color='blue', alpha=0.3, label='Audio Points')
    
    # Plot the feature points on the bottom line (y=0)
    plt.scatter(ft_from, np.zeros_like(ft_from), color='red', alpha=0.3, label='Feature Points')
    
    # Draw thinned lines between the mapped points
    for a, f in zip(audio_to_thinned, ft_from_thinned):
        plt.plot([f, a], [0, 1], color='gray', alpha=0.5)
    
    # Customize the plot
    plt.xlabel('Index')
    plt.ylabel('Points')
    plt.title(f'Chapter {c}: Mapping from ft_len ({ft_len} points) to audio_len ({audio_len} points)')
    plt.yticks([0, 1], ['Feature Points', 'Audio Points'])
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()