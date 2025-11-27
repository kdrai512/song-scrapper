import csv
from typing import TypedDict

import requests
from bs4 import BeautifulSoup

# 1. The Target URL
# album_name = input("Enter  album name: ")
# url = f"https://pagalfree.com/search/{album_name}"
url = "https://pagalfree.com/search/murder 2"

# Define type for songs list


class SongData(TypedDict):
    Title: str
    Image_Url: str
    Link: str


# 2. Fake a Browser (Headers)
# Websites often block scripts. This line makes us look like a real Chrome user.
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print(f"🚀 Fetching data from {url}...")
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Stop if the webpage is down
except Exception as e:
    print(f"❌ Error fetching page: {e}")
    exit()

# 3. Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# 4. Find the Data
# We look for all images that contain 'images' in their source,
# because on this site, every song has a cover image.
songs: list[SongData] = []
song_items = soup.find_all("div", id="category_content")

print("🔍 Scanning page...")

for item in song_items:
    img = item.find("img")
    src = None
    if img:
        src = img.get("src")

        if isinstance(src, str) and "pagalfree.com/images" in src:
            title = "Unknown title"

            parent = img.find_parent("a")
            if parent:
                link = parent.get("href")

                if isinstance(link, str):
                    song_data: SongData = {
                        "Title": "song",
                        "Image_Url": src,
                        "Link": link,
                    }
                    # songs.append(song_data)
                    print("!found", song_data)

    # Filter: Only keep images that look like song covers
# 5. Save to CSV (Excel compatible)
if songs:
    csv_file = "pagalfree_songs.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "Link", "Image_Url"])
        writer.writeheader()
        writer.writerows(songs)

    print(f"\n✅ Success! Scraped {len(songs)} songs.")
    print(f"📂 Data saved to: {csv_file}")
else:
    print("⚠️ No songs found. The site structure might have changed.")
