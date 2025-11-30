import csv
import os
import time
from typing import TypedDict

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# Firefox Imports
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Define type for songs list


class SongData(TypedDict):
    Title: str
    Link: str
    Download_Link: str


# 2. Fake a Browser (Headers)
# Websites often block scripts. This line makes us look like a real Chrome user.
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
# Setup Firefox
print("🔧 Setting up Firefox browser...")
firefox_options = Options()
# firefox_options.add_argument("--headless")

service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=firefox_options)

extension_path = os.path.abspath("uBlock0_1.68.0.firefox.xpi")
driver.install_addon(extension_path, temporary=True)


def get_final_link(song_page_url):
    try:
        print("Visiting song page...")
        driver.get(song_page_url)
        time.sleep(3)
        page_html = driver.page_source

        page_soup = BeautifulSoup(page_html, "html.parser")

        audio_link = page_soup.find_all("a", class_="btn-download")
        best_link = "Not Found"
        for a in audio_link:
            link = a.get("href")
            if isinstance(link, str) and link.endswith(".mp3"):
                if "320" in link:
                    return link
                best_link = link

        return best_link

    except Exception as e:
        return f"❌ Error fetching page: {e}"


# 1. The Target URL
# album_name = input("Enter  album name: ")
# url = f"https://pagalfree.com/search/{album_name}"
url = "https://pagalfree.com/search/murder 2"

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

print(f"Found {len(song_items)} potential items.")

for item in song_items:
    img = item.find("img")

    if img:
        src = img.get("src")

        if isinstance(src, str) and "pagalfree.com/images" in src:
            title = img.get("alt", "Unkown title")

            parent = img.find_parent("a")
            if parent:
                link = parent.get("href")
                output = get_final_link(link)

                if isinstance(link, str):
                    song_data: SongData = {
                        "Title": "song",
                        "Link": link,
                        "Download_Link": output,
                    }
                time.sleep(1)
                if isinstance(link, str):
                    songs.append(
                        {
                            "Title": "song",
                            "Link": link,
                            "Download_Link": output,
                        }
                    )
                time.sleep(1)
                print("!found", output)


# 5. Save to CSV (Excel compatible)
if songs:
    csv_file = "pagalfree_songs.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Title",
                "Link",
                "Download_Link",
            ],
        )
        writer.writeheader()
        writer.writerows(songs)

    print(f"\n✅ Success! Scraped {len(songs)} songs.")
    print(f"📂 Data saved to: {csv_file}")
else:
    print("⚠️ No songs found. The site structure might have changed.")
