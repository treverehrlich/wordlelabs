import csv

# --- Step 1: Read the text file into a list ---
with open("dictionary.txt", "r", encoding="utf-8") as f:
    words = [line.strip() for line in f]

# --- Step 2: Keep only 5-character words ---
filtered = [w for w in words if len(w) == 5]

# --- Step 3: Save to a CSV file (one word per row) ---
with open("all_5_letter_words_loose2.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for w in filtered:
        writer.writerow([w.lower()])