import csv
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# --- CONFIGURATION ---
search_query = "murder 2"
url = f"https://pagalfree.com/search/{search_query.replace(' ', '+')}"

# --- SETUP FIREFOX (HEADLESS) ---
print("🔧 Setting up Firefox (Background Mode)...")
options = Options()
# options.add_argument("--headless")  # <--- THIS MAKES IT INVISIBLE

service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

extension_path = os.path.abspath("uBlock0_1.68.0.firefox.xpi")
driver.install_addon(extension_path, temporary=True)

print(f"🚀 Fetching search results from: {url}")
songs_data = []

try:
    driver.get(url)
    time.sleep(2)  # Wait for page to load

    # Parse search results
    soup = BeautifulSoup(driver.page_source, "html.parser")
    song_items = soup.find_all("div", id="category_content")
    print(f"🔍 Found {len(song_items)} items.")

    for item in song_items:  # Limit to 3 for testing
        img = item.find("img")
        if img:
            title = img.get("alt", "Unknown")
            parent_a = item.find("a")

            if parent_a:
                song_link = parent_a.get("href")
                print(f"   🎵 Visiting: {title}")

                # Visit the song page
                driver.get(song_link)
                time.sleep(2)  # Wait for JS to generate download link

                # Find the MP3 link
                page_soup = BeautifulSoup(driver.page_source, "html.parser")
                links = page_soup.find_all("a", href=True)

                mp3_url = "Not Found"
                for link in links:
                    href = link["href"]
                    if href.endswith(".mp3"):
                        if "320" in href:
                            mp3_url = href
                            break
                        mp3_url = href

                songs_data.append({"Title": title, "Download": mp3_url})

    # Save to CSV
    if songs_data:
        with open("pagalfree_final.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Title", "Download"])
            writer.writeheader()
            writer.writerows(songs_data)
        print("✅ Done! Saved to pagalfree_final.csv")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    driver.quit()
