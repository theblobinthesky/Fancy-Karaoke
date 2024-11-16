import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_features(file_path):
    """Load features from a .ft file."""
    print(f"Loading features from '{file_path}'")
    with open(file_path, "rb") as f:
        features = np.load(f)
    return features

def visualize_features(features, title=None, save_path=None):
    """Visualize the features as a heatmap."""
    plt.figure(figsize=(10, 4))
    plt.imshow(features.T, aspect='auto', origin='lower', interpolation='none', cmap='viridis')
    plt.xlabel('Frame')
    plt.ylabel('Coefficient')
    if title:
        plt.title(title)
    plt.colorbar(label='Feature Value')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
        print(f"Feature plot saved to '{save_path}'")
    else:
        plt.show()

def main(root):
    """Load and visualize features from .ft files in the specified directory."""
    output_dir = Path(root) / "feature_plots"
    output_dir.mkdir(exist_ok=True)

    # Visualize features from the main audio file
    ft_file = Path(root) / "audio.ft"
    if ft_file.exists():
        features = load_features(ft_file)
        save_path = output_dir / "audio.png"
        visualize_features(features, title="Audio Features", save_path=save_path)
    else:
        print(f"No feature file found at '{ft_file}'")

    # Visualize features from the 'tts-joins' directory
    tts_joins_dir = Path(root) / "tts-joins"
    if tts_joins_dir.exists():
        for ft_file in tts_joins_dir.glob("*.ft"):
            features = load_features(ft_file)
            save_path = output_dir / (ft_file.stem + ".png")
            visualize_features(features, title=ft_file.stem, save_path=save_path)
    else:
        print(f"No 'tts-joins' directory found at '{tts_joins_dir}'")

if __name__ == "__main__":
    main("song")