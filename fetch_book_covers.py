import requests
import os
import re
import json

# Constants
BOOKS_YAML = "content/books.md"  # Your YAML file with book data
OUTPUT_FOLDER = "static/images"  # Folder to save book covers
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

# Function to format the title for saving files
def format_title(title):
    return re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')

# Function to fetch book cover
def fetch_book_cover(title, author):
    try:
        # Search query for Google Books API
        params = {"q": f"intitle:{title} inauthor:{author}", "maxResults": 1}
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        response.raise_for_status()  # Raise error for bad responses
        
        # Parse JSON response
        data = response.json()
        if "items" not in data or not data["items"]:
            print(f"Cover not found for: {title} by {author}")
            return None

        isbn = data["items"][0]["volumeInfo"].get("industryIdentifiers", [])[0].get("identifier")
        print(f"ISBN for {title} by {author}: {isbn}")
        book_cover_url = f"https://bookcover.longitood.com/bookcover/{isbn}"

        # Get 'url' param after querying the above url
        cover_url = requests.get(book_cover_url).json().get("url")

        if not cover_url:
            print(f"Cover not found for: {title} by {author}")
            return None

        return cover_url
        
    except Exception as e:
        print(f"Error fetching cover for {title} by {author}: {e}")
        return None

# Function to download and save image
def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Saved cover to: {save_path}")
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")

# Main function to process books
def process_books(books):
    # Ensure output folder exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for book in books:
        title = book.get("title")
        author = book.get("author")
        if not title or not author:
            print("Skipping book with missing title or author")
            continue
        
        formatted_title = format_title(title)
        save_path = os.path.join(OUTPUT_FOLDER, f"{formatted_title}.jpg")
        
        # Skip if already downloaded
        if os.path.exists(save_path):
            print(f"Cover already exists: {save_path}")
            continue
        
        # Fetch and save cover
        cover_url = fetch_book_cover(title, author)
        if cover_url:
            download_image(cover_url, save_path)

# Read YAML file
def load_books_from_yaml(file_path):
    import yaml
    with open(file_path, "r") as file:
        content = file.read()
        # Match YAML front matter (delimited by "---")
        match = re.match(r"---\n(.*?)\n---", content, re.DOTALL)
        if match:
            front_matter = match.group(1)
            return yaml.safe_load(front_matter).get("Books", [])  # Parse YAML
        else:
            raise ValueError("No front matter found in the Markdown file.")     

# Run the script
if __name__ == "__main__":
    books = load_books_from_yaml(BOOKS_YAML)
    process_books(books)

