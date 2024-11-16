import pygame
import json
import time
import threading
import os

def load_lyrics(lyrics_file):
    """
    Load and parse the lyrics JSON file.
    
    Args:
        lyrics_file (str): Path to the lyrics JSON file.
        
    Returns:
        List of tuples containing (timestamp, word).
    """
    with open(lyrics_file, 'r') as f:
        lyrics_data = json.load(f)
    
    words_with_timestamps = []
    
    for line in lyrics_data:
        line_offset = line["offset"]
        words = line["words_begin"]
        words_text = line["line"].split(" ")
        
        for word_time, word_text in zip(words, words_text):
            absolute_time = line_offset + word_time
            words_with_timestamps.append( (absolute_time, word_text) )
    
    # Sort the words by their absolute time
    words_with_timestamps.sort(key=lambda x: x[0])
    
    return words_with_timestamps

def play_audio(audio_file):
    """
    Initialize pygame mixer and play the audio file.
    
    Args:
        audio_file (str): Path to the audio file.
    """
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

def display_words(words_with_timestamps, start_time, stop_event):
    """
    Display words at their corresponding timestamps.
    
    Args:
        words_with_timestamps (list): List of tuples containing (timestamp, word).
        start_time (float): The time when audio playback started.
        stop_event (threading.Event): Event to signal when to stop the thread.
    """
    for timestamp, word in words_with_timestamps:
        current_time = time.time() - start_time
        wait_time = timestamp - current_time
        if wait_time > 0:
            if stop_event.wait(wait_time):
                break  # Stop event is set, exit the thread
        print(word)
    # Optionally, signal that all words have been displayed
    stop_event.set()

def main():
    # Paths to the audio and lyrics files
    audio_file = os.path.join("song", "audio.wav")
    lyrics_file = os.path.join("song", "syncs.json")
    
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return
    if not os.path.exists(lyrics_file):
        print(f"Lyrics file not found: {lyrics_file}")
        return
    
    # Load and sort the lyrics
    words_with_timestamps = load_lyrics(lyrics_file)
    
    # Initialize stop event
    stop_event = threading.Event()
    
    # Start playing audio
    play_audio(audio_file)
    
    # Record the start time
    start_time = time.time()
    
    # Start a thread to display words
    display_thread = threading.Thread(target=display_words, args=(words_with_timestamps, start_time, stop_event))
    display_thread.start()
    
    try:
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nPlayback interrupted by user.")
    finally:
        # Signal the display thread to stop
        stop_event.set()
        display_thread.join()
        pygame.mixer.music.stop()
        pygame.mixer.quit()

if __name__ == "__main__":
    main()