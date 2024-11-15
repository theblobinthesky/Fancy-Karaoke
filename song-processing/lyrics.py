import requests
from bs4 import BeautifulSoup
from typing import List, Union

def fetch_and_save_lyrics(url: str, file: str) -> None:
    # Send a GET request to the webpage
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    # Parse the HTML content
    soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')

    # Find the element with id "lyrics-root"
    lyrics_root: Union[BeautifulSoup, None] = soup.find(id="lyrics-root")
    parts: List[str] = []

    if lyrics_root:
        # Iterate over the direct children of lyrics_root
        for lyric_part in lyrics_root.find_all(recursive=True):
            if lyric_part.get('data-lyrics-container') == "true":
                # Iterate over the child nodes of lyric_part
                part = ""
                for node in lyric_part.descendants:
                    if isinstance(node, str) and node.strip():
                        part += node
                    elif node.name == 'br':
                        part = part.strip()
                        if part != "":
                            parts.append(part)
                            part = ""

    # Join the parts with newline characters
    text: str = "\n".join(parts)

    # Get the title of the page for the filename
    title_tag = soup.find('title')
    title: str = title_tag.get_text().strip() if title_tag else "lyrics"
    filename: str = f"{title}.txt"

    # Write the text to a file
    with open(file, 'w', encoding='utf-8') as f:
        f.write(text)

def main(root: str):
    webpage_url: str = input("Enter lyrics URL: ")
    fetch_and_save_lyrics(webpage_url, f"{root}/lyrics.txt")