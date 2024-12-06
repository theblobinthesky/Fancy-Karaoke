from transformers import Wav2Vec2Model, Wav2Vec2Processor
import torch, librosa

def main(root: str):
    # Load pre-trained Wav2Vec 2.0 model and processor
    audio_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    audio_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
    audio_model.eval()

    # Preprocess audio
    waveform, sample_rate = librosa.load(f"{root}/audio.wav", sr=16000)
    input_values = audio_processor(waveform, sampling_rate=sample_rate, return_tensors="pt").input_values

    # Extract audio features
    with torch.no_grad():
        audio_features = audio_model(input_values).last_hidden_state  # Shape: (1, T_audio, D_audio)
    audio_features = audio_features.squeeze(0)  # Shape: (T_audio, D_audio)

if __name__ == "__main__":
    main("song")