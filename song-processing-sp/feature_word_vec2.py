import soundfile as sf
import torch
import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2Model
from pathlib import Path

def load_model():
    # Load pre-trained Wav2Vec 2.0 model and processor
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")

    # Move model to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()  # Set model to evaluation mode
    return processor, model, device

def extract_wav2vec2_features(processor, model, device, signal: np.ndarray, sr: int) -> np.ndarray:
    # Preprocess the audio signal
    preprocessed_signal = signal

    # Use the processor to prepare the input
    inputs = processor(preprocessed_signal, sampling_rate=16000, return_tensors="pt", padding=True)

    # Move inputs to the same device as the model
    input_values = inputs['input_values'].to(device)

    # Some models may return attention_mask; handle accordingly
    attention_mask = inputs['attention_mask'].to(device) if 'attention_mask' in inputs else None

    with torch.no_grad():
        # Get the hidden states from the model
        if attention_mask is not None:
            outputs = model(input_values, attention_mask=attention_mask)
        else:
            outputs = model(input_values)
        hidden_states = outputs.last_hidden_state  # Shape: (batch_size, sequence_length, hidden_size)

    # Convert to NumPy array and detach from GPU if necessary
    features = hidden_states.cpu().numpy()[0]  # Assuming batch_size=1

    return features  # Shape: (sequence_length, hidden_size)

def load_and_save_features(we, file: str):
    print(f"Loading features of '{file}'")
    processor, model, device = we
    signal, samplerate = sf.read(file)
    features = extract_wav2vec2_features(processor, model, device, signal, samplerate)

    ft_path = Path(file).with_suffix(".ft")
    with open(ft_path, "wb") as file:
        np.save(file, features)

def main(root: str):
    we = load_model()

    audio_wav = f"{root}/audio.wav"
    load_and_save_features(we, audio_wav)

    for tts_join in Path(f"{root}/tts-joins").glob("*.wav"):
        load_and_save_features(we, str(tts_join))

if __name__ == "__main__":
    main("song")