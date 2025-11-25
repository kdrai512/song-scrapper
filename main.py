import requests
from bs4 import BeautifulSoup
import csv

# 1. The Target URL
url = "https://pagalfree.com/search/murder 2"

# 2. Fake a Browser (Headers)
# Websites often block scripts. This line makes us look like a real Chrome user.
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print(f"🚀 Fetching data from {url}...")
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status() # Stop if the webpage is down
except Exception as e:
    print(f"❌ Error fetching page: {e}")
    exit()

# 3. Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# 4. Find the Data
# We look for all images that contain 'images' in their source, 
# because on this site, every song has a cover image.
songs = []
images = soup.find_all("img")

print(f"🔍 Scanning page...")

for img in images:
    src = img.get('src', '')
    # print(src)

    if "pagalfree.com/images" in src:
        title=img.get("alt","Unkown Title")

        parent= img.find_parent('a')
        if parent:
            link = parent.get('href')
            print("link" ,link)

    # Filter: Only keep images that look like song covers
# 5. Save to CSV (Excel compatible)
if songs:
    csv_file = "pagalfree_songs.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "Link", "Image_URL"])
        writer.writeheader()
        writer.writerows(songs)
    
    print(f"\n✅ Success! Scraped {len(songs)} songs.")
    print(f"📂 Data saved to: {csv_file}")
else:
    print("⚠️ No songs found. The site structure might have changed.")
