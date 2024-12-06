import torch
from transformers import BertTokenizer, BertModel

def main(root: str):
    # Load pre-trained BERT model and tokenizer
    text_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    text_model = BertModel.from_pretrained("bert-base-uncased")
    text_model.eval()

    # Preprocess text
    with open(f"{root}/lyrics.txt", "r") as file:
        lyrics = file.read()

    encoded_input = text_tokenizer(lyrics, return_tensors="pt", padding=True, truncation=True)

    # Extract text features
    with torch.no_grad():
        text_features = text_model(**encoded_input).last_hidden_state  # Shape: (1, T_text, D_text)
    text_features = text_features.squeeze(0)  # Shape: (T_text, D_text)

if __name__ == "__main__":
    main("song")