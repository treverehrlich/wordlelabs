import pandas as pd
import string
from collections import Counter
from bs4 import BeautifulSoup
import requests
import csv

# URL to scrape
url = "https://www.rockpapershotgun.com/wordle-past-answers"
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
}

# Fetch the page
response = requests.get(url, headers=headers)
response.raise_for_status()  # Raises an error if request failed

# Parse with BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Step 1: Find the <h2> that says "All Wordle answers"
h2_element = soup.find("h2", string="All Wordle answers")

answers = []
# Step 2: Find the next <ul> after that <h2>
if h2_element:
    ul_element = h2_element.find_next("ul")
    if ul_element:
        # Step 3: Get all <li> inside that <ul>
        li_elements = ul_element.find_all("li")
        # Step 4: Extract text from each <li>
        answers = [li.get_text(strip=True) for li in li_elements]
        #print(answers)
    else:
        print("No <ul> found after the <h2>.")
else:
    print("No <h2> with 'All Wordle answers' found.")

used_words = [word.lower() for word in answers]

print(f"loaded {len(used_words)} used words")

with open('assets/scraped.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    for item in used_words:
        writer.writerow([item])  # Wrap in list to write one item per row