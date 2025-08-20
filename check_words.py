import enchant
import csv

# Initialize English dictionary
d = enchant.Dict("en_US")

# Input/output file paths
input_csv = "assets/all_wordle_words.csv"
output_csv = "assets/valid_words.csv"

with open(input_csv, newline="", encoding="utf-8") as infile, \
     open(output_csv, "w", newline="", encoding="utf-8") as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        if not row:  # skip empty rows
            continue
        
        word = row[0].strip()
        
        if d.check(word):  # check if it's a valid word
            print(f"accepted: {word}")
            writer.writerow([word])
        else:
            print(f"rejected: {word}")

print(f"Valid words written to {output_csv}")