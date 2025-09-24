import requests
from bs4 import BeautifulSoup
import csv

base_url = "https://quotes.toscrape.com/page/{}/"
all_data = []

# Lặp qua nhiều trang (trang cuối là /page/10/)
for page in range(1, 11):
    url = base_url.format(page)
    res = requests.get(url)
    if res.status_code != 200:
        break  # dừng nếu hết trang
    soup = BeautifulSoup(res.text, "html.parser")
    
    # Tìm tất cả các block quote
    quotes = soup.find_all("div", class_="quote")
    if not quotes:
        break

    for q in quotes:
        text = q.find("span", class_="text").get_text(strip=True)
        author = q.find("small", class_="author").get_text(strip=True)
        all_data.append([text, author])

# Lưu ra CSV
with open("quotes_authors.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Quote", "Author"])
    writer.writerows(all_data)

print(f"✅ Đã lưu {len(all_data)} quote kèm tác giả vào quotes_authors.csv")
