import pandas as pd
import string
from collections import Counter
from bs4 import BeautifulSoup
import requests

def old_main():

    wordle_list = load_all_wordle_words()

    used_list = load_used_words()

    unused_list = find_unused_words(wordle_list,used_list)

    list_knowns = []

    while(1==1):

        get_next_best_word(unused_list)

        option = input("1) remove letter 2) contains letter 3) add known location: ")

        match int(option):
            case 1:
                letter = input("ok what is the letter to remove altogether? ")
                unused_list = remove_letter(unused_list, letter)
                list_knowns.append(f"Has no '{letter}'")

            case 2:
                letter = input("ok what is the letter you know about? ")
                location = input("what is the location where the letter is NOT (0-based index? ")
                unused_list = known_letter_unknown_location(unused_list, letter, int(location))
                list_knowns.append(f"Has '{letter}' but not in loc '{location}'")

            case 3:
                letter = input("ok what is the letter you know about? ")
                location = input("what is the location of that letter in the word (0-based index? ")
                unused_list = known_letter_location(unused_list, letter, int(location))
                list_knowns.append(f"Has located '{letter}' in loc '{location}'")

        print(list_knowns)

def get_next_best_word(unused_list):

    letter_occurrences_dict = letter_count(unused_list)
    letter_position_weights = letter_position_counts(unused_list)

    print(letter_occurrences_dict)
    print(letter_position_weights)

    myListDict = {}

    best_score = 0
    worst_score = 99999

    best_word = ''
    worst_word = ''
    
    for word in unused_list:
        this_score = calculate_word_score(word, letter_occurrences_dict, letter_position_weights)
        myListDict[word] = {"score" : this_score}
        print(f"word: {word} == {this_score}")
        if this_score > best_score:
            best_score = this_score
            best_word = word

        if this_score < worst_score:
            worst_score = this_score
            worst_word = word





    print(f'{len(unused_list)} words remain')
    
    print(f'We suggest {best_word} with score {best_score}')

    return best_word, best_score, worst_word, worst_score, myListDict, letter_occurrences_dict, letter_position_weights


def letter_position_counts(word_list):
    from collections import defaultdict
    counts = defaultdict(lambda: [0, 0, 0, 0, 0])
    for word in word_list:
        if len(word) != 5:
            continue
        for i, letter in enumerate(word.lower()):
            counts[letter][i] += 1
    return dict(counts)


def has_duplicate_letters(word):
    # Count the occurrences of each letter in the word
    letter_counts = Counter(word)
    
    # Check if any letter has a count greater than 1
    for count in letter_counts.values():
        if count > 1:
            return True
    return False

def calculate_word_score(word, letter_occurrences, letter_weight_dict):
    # Convert the word to lowercase to handle case-insensitivity
    word = word.lower()
    
    # Initialize the score variable
    score = 0
    
    # Loop through each letter in the word and add its count from the dictionary to the score
    # but this is a set, which means we're not counting/scoring repeated letters
    
    position = 0
   # for letter in sorted(set(word)):
    for letter in word:
        
        letter_score = letter_occurrences.get(letter, 0)  # Default to 0 if the letter is not found
        letter_weight = get_weight(position,letter_weight_dict[letter]) # find how often this letter is in this position

        # even distribution should have a letter in each position 20% of the time

        if (letter_weight > 0.7):
            #print(f"boosting from {letter_score}")
            letter_score = letter_score * 1.3 # give it a slight boost
        elif (letter_weight > 0.5):
            #print(f"boosting from {letter_score}")
            letter_score = letter_score * 1.2 # give it a slight boost
        elif (letter_weight > 0.30):
            #print(f"boosting from {letter_score}")
            letter_score = letter_score * 1.1 # give it a slight boost
        elif (letter_weight > 0.1):
            #print(f"dampening from {letter_score}")
            letter_score = letter_score * 0.95 # give it a slight boost
        elif (letter_weight > 0.05):
            #print(f"dampening from {letter_score}")
            letter_score = letter_score * 0.9 # give it a slight boost
        elif (letter_weight > 0):
            #print(f"dampening from {letter_score}")
            letter_score = letter_score * 0.85 # give it a slight boost

        #print(f"{word}: {letter}, {letter_weight_dict[letter]}, {letter_weight} = {letter_score}")

        if (has_occurred_before(word,position)):
            pass # don't add to score for a letter that's been seen already in the word
        else:
            score += letter_score
        
        position += 1

    return int(score)

    # Example usage
    word = "apple"
    letter_occurrences = {
        'a': 5, 'b': 1, 'c': 0, 'd': 0, 'e': 2, 'f': 0, 'g': 1, 'h': 0, 
        'i': 0, 'j': 0, 'k': 0, 'l': 1, 'm': 0, 'n': 2, 'o': 0, 'p': 2, 
        'q': 0, 'r': 1, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0, 'x': 0, 
        'y': 0, 'z': 0
    }


def has_occurred_before(word, index):
    letter = word[index]
    return letter in word[:index]

def get_weight(position, values):
    total = sum(values)
    if total == 0:
        return 0  # Avoid division by zero
    
    #print(f"{values}, {position}, {values[position]}, {total}")
    return values[position] / total    

def letter_count(words):
    # Create a list of all letters in the words
    all_letters = ''.join(words).lower()
    
    # Count occurrences of each letter
    letter_counter = Counter(all_letters)
    
    # Create a dictionary with 0 count for letters not found in the words
    letter_occurrences = {letter: letter_counter.get(letter, 0) for letter in string.ascii_lowercase}
    
    return letter_occurrences

def known_letter_unknown_location(unused_list, letter, location):

    # Use a list comprehension to filter out words
    unused_list = [word for word in unused_list if letter in word and word[location] != letter]

    print(unused_list)
    print(f"added letter {letter} but not at position {location}; now {len(unused_list)} words remain")

    return unused_list

def known_letter_location(unused_list, letter, location):
    # Keep only words where the letter is at the given position
    unused_list = [word for word in unused_list if len(word) > location and word[location] == letter]

    print(unused_list)
    print(f"added letter {letter} at position {location} and now {len(unused_list)} words remain")

    return unused_list

def remove_letter(unused_list, letter):
    
    # Keep only words that do NOT contain the letter
    unused_list = [word for word in unused_list if letter not in word]

    print(unused_list)
    print(f"removed letter {letter} and now {len(unused_list)} words remain")

    return unused_list

def load_used_words():


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

    return used_words


def load_all_wordle_words():

    with open('assets/all_wordle_words.txt', 'r') as file:
        file_content = file.read().replace('\n', '')

    wordle_list = file_content.split(' ')
    wordle_list = [word.lower() for word in wordle_list]

    wordle_list = process_doubled_words(wordle_list)

    print(f"loaded all {len(wordle_list)} wordle words")

    return wordle_list

def process_doubled_words(word_list): # for when word list had two words together
    # Iterate through the list of words to find a 10-letter word
    for word in word_list:
        if len(word) == 10:
            # Split the 10-letter word into two 5-letter words
            first_half = word[:5]
            second_half = word[5:]
            
            # Remove the 10-letter word and insert the two 5-letter words
            word_list.remove(word)
            word_list.append(first_half)
            word_list.append(second_half)
    
    return word_list

def find_unused_words(all,used):

    # Find words not common to both lists
    unique_words = list(set(all).symmetric_difference(set(used)))

    # remove words found in the used list
    unique_words = [word for word in unique_words if word not in used]

    print(f"found {len(unique_words)} unused words")

    return unique_words
