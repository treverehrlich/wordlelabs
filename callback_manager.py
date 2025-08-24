from dash import Input, Output, State, html, dcc, ALL, MATCH, no_update, callback_context
from serving import app
from content_rendering import *
from functions import *
from constants import *
import csv
import uuid
import time
from datetime import datetime
from flask import request

def get_main_layout():
    return render_main_layout()

@app.callback(
    Output('suggestBest', 'children'),
    Output('suggestWorst', 'children'),
    Output('headerWordcount', 'children'),
    Output('remainingWordsListScored', 'children'),
    Output('chart_distro', 'figure'),
    Output('chart_histro', 'figure'),
    Output('usedWordleCount', 'children'),
    Output('usedWordleList','children'),
    Output('my_words','data'),
    Output('my_letters','data', allow_duplicate=True),  
    Output("enter_flag", "data", allow_duplicate=True),    
    Output("backspace_flag", "data", allow_duplicate=True),   
    Output("new_letter_flag", "data", allow_duplicate=True),          
    Output("completed_word_index", "data", allow_duplicate=True),            
    Output("completed", "data", allow_duplicate=True),    
    Output("visit_counter", "children", allow_duplicate=True),    
    Input("url", "pathname"),
    
    prevent_initial_call=False  # allow it to run on load
)

def initialize_everything(url):

    start_time = time.time()
    allListRaw = load_all_wordle_words()
#    allList = format_list_of_words(allListRaw)

    print("scraping used words...")
    usedListRaw = load_used_words()
    print("finished scraping!")
    usedList = format_list_of_words(usedListRaw)

    unusedListRaw = find_unused_words(allListRaw,usedListRaw)
#    unusedList = format_list_of_words(unusedListRaw)

    best_word, best_score, worst_word, worst_score, myListDict, occurrances, weights = get_next_best_word(unusedListRaw)
    myList, best_three, worst_three = format_list_of_words_scored(myListDict)

    print(occurrances)
    # print(len(myListRaw))     
    
    # jsonForSession = json.dumps(myListRaw)
    # print(jsonForSession)

    suggestBest = f"Best words: {', '.join(best_three)}"
    suggestWorst = f"Bravest words: {', '.join(worst_three)}"

    headerWordCount = f"Word Count: {len(unusedListRaw)}"

    chart_distro = distro_builder(occurrances)
    chart_histro = histo_builder(weights)

    usedWordleCount = f"Word Count: {len(usedListRaw)}"

    print(f"took {time.time() - start_time} secs to initialize")

    my_letters = ''
    enter_flag = backspace_flag = new_letter_flag = 0
    completed_word_index = -1

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")    

    with open("visits.txt", "r") as f:
        visit_counter = sum(1 for _ in f)    

    with open("feedback.txt", "r") as f:
        feedback_lines = sum(1 for _ in f)    

    feedback_estimate = int(feedback_lines/4)
    visit_counter = f'{visit_counter}:{feedback_estimate}'

    # Append text to a file
    with open("visits.txt", "a") as f:
        f.write(f"visit datetime: {dt_string}, ip address: {request.remote_addr}\n")

    return suggestBest, suggestWorst, headerWordCount, myList, chart_distro, chart_histro, usedWordleCount, \
        usedList, unusedListRaw, my_letters, enter_flag, backspace_flag, new_letter_flag, completed_word_index, 0, visit_counter


# wrapper to handle/catch keypresses from the physical keyboard - letters and backspace only
@app.callback(
    Output("my_letters", "data", allow_duplicate=True),
    Output("enter_flag", "data", allow_duplicate=True),    
    Output("backspace_flag", "data", allow_duplicate=True),   
    Output("new_letter_flag", "data", allow_duplicate=True),              
    Input("key-listener", "n_keydowns"),
    Input("key-listener", "keydown"),
    State("my_letters", "data"),    
    State("completed", "data"),    

)
def on_physical_keypress(n, key, data, completed):

    enter_flag = no_update
    backspace_flag = no_update
    new_letter_flag = no_update

    if (completed == 1):
        return no_update, no_update, no_update, no_update

    keypressed = key['key']

    print(f"Key #{n}: {keypressed}, stored strokes = {data}")

    if len(keypressed) == 1 and keypressed.isalpha():
        data = str(data) + str(keypressed.upper())
        new_letter_flag = 1
    elif keypressed == 'Backspace':
        if len(data) > 0:
            backspace_flag = 1
    elif keypressed == 'Enter':
        print("Enter was pressed on physical keyboard")
        enter_flag = 1
    
    return data, enter_flag, backspace_flag, new_letter_flag

# handle input from the virtual on-screen keyboard - letters and backspace only
@app.callback(
    Output("my_letters", "data", allow_duplicate=True),
    Output("enter_flag", "data", allow_duplicate=True),    
    Output("backspace_flag", "data", allow_duplicate=True),   
    Output("new_letter_flag", "data", allow_duplicate=True),        
    Input({"type": "key-btn", "index": ALL}, "n_clicks"),
    State("my_letters", "data"),
    State("completed", "data"),    
    prevent_initial_call=True
)
def on_onscreen_keypress(n_clicks_list, data, completed):

    enter_flag = no_update
    backspace_flag = no_update
    new_letter_flag = no_update

    if (completed == 1):
        return no_update, no_update, no_update, no_update

    ctx = callback_context
    if not ctx.triggered:
        return data, enter_flag

    key_id = ctx.triggered[0]["prop_id"].split(".")[0]
    key_name = eval(key_id)["index"]

    if key_name == "Backspace":
        backspace_flag = 1
    elif key_name == "Enter":
        print("Enter was clicked on on-screen keyboard")
        enter_flag = 1
    else:
        data = data + key_name
        new_letter_flag = 1

    return data, enter_flag, backspace_flag, new_letter_flag

@app.callback(

    Output({'type': 'wordle_letter', 'index': ALL}, 'children', allow_duplicate=True),  
    #Output({'type': 'wordle_letter', 'index': ALL}, 'style', allow_duplicate=True),     
    Output("new_letter_flag", "data", allow_duplicate=True),     
    Output("my_letters", "data", allow_duplicate=True),
    Input("new_letter_flag", "data"),   
    State("my_letters", "data"),    
    State({'type': 'wordle_letter', 'index': ALL}, 'id'),
    State("completed_word_index", "data"),    
    prevent_initial_call=True  # allow it to run on load

)
def pressed_letter(new_letter_flag, my_letters, ids, completed_word_index):

    print("pressed_letter callback was triggered - checking new_letter_flag")

    # nothing to update on first load
    #all_styles =  [no_update] * len(ids)
    all_children =  [no_update] * len(ids)    

    if (new_letter_flag != 1):
        print("new_letter_flag was found to be <> 1, so doing nothing")        
        new_letter_flag = 0
        return all_children, new_letter_flag, my_letters

    print("new_letter_flag was found to be 1, so do something then clear the flag")
    new_letter_flag = 0

    new_letter = my_letters[-1:]
    #print(new_letter)

    print(f'the len of my_letters = {len(my_letters)}')

    current_row = (len(my_letters)-1) // 5 # the current row
    current_row_position = (len(my_letters)-1) % 5 # position in row
    target_id = f'{current_row}_{current_row_position}'
    #print(target_id)

    if completed_word_index + 1 != current_row: # attempting to go past current word's end
        new_letter_flag = 0
        print(f"can't go past there! my_letters={my_letters}")
        my_letters = my_letters[:((completed_word_index+1)*5)+5] # truncate letters to what is allowed
        print(f"fixed that! my_letters={my_letters}")        
        return all_children, new_letter_flag, my_letters

    # find the position whose id['index'] == target and set its style
    for pos, id_dict in enumerate(ids):
        #print(f"{pos} -- {id_dict}")
        if id_dict.get('index') == target_id:
            # all_styles[pos] = {
            #     'backgroundColor': 'yellow',
            #     'border': '2px solid #000',
            # }
            all_children[pos] = new_letter

            break

    return all_children, new_letter_flag, my_letters

@app.callback(

    Output({'type': 'wordle_letter', 'index': ALL}, 'children', allow_duplicate=True),  
    #Output({'type': 'wordle_letter', 'index': ALL}, 'style',allow_duplicate=True),  
    Output("backspace_flag", "data", allow_duplicate=True),  
    Output("my_letters", "data", allow_duplicate=True),

    Input("backspace_flag", "data"),   
    State("my_letters", "data"),  
    State({'type': 'wordle_letter', 'index': ALL}, 'id'),
    State("completed_word_index", "data"),     

    prevent_initial_call=True  # allow it to run on load

)
def pressed_backspace(backspace_flag, my_letters, ids, completed_word_index):

    print("pressed_backspace callback was triggered - checking backspace_flag")
    all_children =  [no_update] * len(ids)   

    if (backspace_flag != 1):
        print("Backspace flag was found to be <> 1, so doing nothing")        
        backspace_flag = 0
        return all_children, backspace_flag, my_letters

    print("Enter flag was found to be 1, so do something then clear the flag")
    backspace_flag = 0

    print(f'the len of my_letters = {len(my_letters)}')

    current_row = (len(my_letters)-1) // 5 # the current row
    current_row_position = (len(my_letters)-1) % 5 # position in row
    target_id = f'{current_row}_{current_row_position}'

    if (current_row_position >= 0) and (completed_word_index+1 == current_row): # there's letter(s) in this row, so delete one letter
        my_letters = my_letters[:-1]
        print(f"After backspace, my_letters={my_letters}")        
    else:
        return all_children, backspace_flag,my_letters

    print(f'removing from {target_id}')

    # find the position whose id['index'] == target and set its style
    for pos, id_dict in enumerate(ids):
        #print(f"{pos} -- {id_dict}")
        if id_dict.get('index') == target_id:
            # all_styles[pos] = {
            #     'backgroundColor': 'yellow',
            #     'border': '2px solid #000',
            # }
            all_children[pos] = None

            break

    return all_children, backspace_flag, my_letters

#process what happens when people click enter on each completed word

#(id={"type" : "wordle_letter_div", "index" : f'{row}_{col}'}

@app.callback(

    Output({'type': 'wordle_letter', 'index': ALL}, 'style',allow_duplicate=True),  
    Output('my_words', 'data', allow_duplicate=True),   
    Output("enter_flag", "data", allow_duplicate=True),     
    Output('remainingWordsListScored', 'children',allow_duplicate=True),
    Output('headerWordcount','children',allow_duplicate=True),   
    Output('suggestBest', 'children', allow_duplicate=True),
    Output('suggestWorst', 'children', allow_duplicate=True),
    Output('chart_distro', 'figure', allow_duplicate=True),
    Output('chart_histro', 'figure', allow_duplicate=True),
    Output("completed_word_index", "data"),   
    Output("status_output", "children", allow_duplicate=True),  
    Output("completed", "data"),    
    Input("enter_flag", "data"),   
    State("my_letters", "data"),    
    State('my_words', 'data'),     
    State({'type': 'wordle_letter', 'index': ALL}, 'style'),
    State("completed_word_index", "data"),    

    prevent_initial_call=True  # allow it to run on load

)
def pressed_enter(enter_flag, my_letters, unusedListRaw, ids, completed_word_index):

    print("pressed_enter callback was triggered - checking enter_flag")
    all_style =  [no_update] * len(ids)   

    if (enter_flag != 1):
        print("Enter flag was found to be <> 1, so doing nothing")        
        enter_flag = 0
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "", no_update

    enter_flag = 0

    if (len(my_letters) == 0) or (len(my_letters) % 5 != 0): # check if a word is actually fully entered
        print("Incomplete/no word found, so doing nothing")
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "", no_update

    # check if this completed word is a new completed word, or is still last word completed word
    new_full_word_index = int((len(my_letters) // 5)-1)
    #print(new_full_word_index)
    #print(completed_word_index)
    if new_full_word_index <= completed_word_index:
        print("Enter was pressed, but there's no new word")
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "", no_update       

    last_guess_word = my_letters[-5:]
    # print(last_guess_word)

    with open("assets/all_5_letter_words_loose.csv", newline="", encoding="utf-8") as csvfile:
        all_words_loose = csvfile.read().splitlines()

    # print(all_words_loose)
    # print(last_guess_word.lower())

    if last_guess_word.lower() not in all_words_loose:
        print(f"{last_guess_word} is probably not even a word!")
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "That is not a word!", no_update         

    completed_word_index += 1 # finished a word
    last_guess_colors = []

    # get current row colors
    for c in range(5):
        last_guess_colors.append(ids[(completed_word_index*5)+c]) 

#     # next we update the list of remaining words, based on the previous word input (letters and colors)

    # use a dict to keep track of number of occurrances of a letter in the word
    alphabet_dict = {} #{chr(c): 0 for c in range(ord('a'), ord('z') + 1)}
    #print(alphabet_dict)

    green_counter = 0
    for letter_location in range(5):

        if last_guess_colors[letter_location]['backgroundColor'] == GREEN: # got a hit
            print(f'\n green')           
            green_counter += 1
            unusedListRaw = known_letter_location(unusedListRaw, last_guess_word[letter_location].lower(), letter_location)
            print(f'\n new len is {len(unusedListRaw)}')
        elif last_guess_colors[letter_location]['backgroundColor'] == YELLOW: # partial hit
            print(f'\n yellow')
            unusedListRaw = known_letter_unknown_location(unusedListRaw, last_guess_word[letter_location].lower(), letter_location)
            print(f'\n new len is {len(unusedListRaw)}')
        else:
            pass

    # the word was correct, don't go any further
    if green_counter == 5:
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "You found it! (Refresh to restart)", 1         
        
    # highlight the next row to guess
    all_style = []
    for r in range(6):
        for c in range(5):
            if r == completed_word_index+1:
                all_style.append({'backgroundColor': '#555'})    
            else: 
                all_style.append(no_update)
        
    
    #print(all_style)
    #print(last_guess_colors)
    #print(f'\n{last_guess_word}')

    # now, build a dict that keeps track of how many times each guess letter appears, based on the coloring
    # this way we can properly filter for multiple letter occurrances
    for letter_location in range(5):

        if last_guess_colors[letter_location]['backgroundColor'] in [GREEN,YELLOW]:   

            if last_guess_word[letter_location].lower() in alphabet_dict:
                alphabet_dict[last_guess_word[letter_location].lower()] += 1
            else:
                alphabet_dict[last_guess_word[letter_location].lower()] = 1

        else:

            if last_guess_word[letter_location].lower() in alphabet_dict:
                pass # do nothing, since we might already be incrementing that
            else:
                alphabet_dict[last_guess_word[letter_location].lower()] = 0            


    #print(alphabet_dict)
    unusedListRaw = letter_occurrances(unusedListRaw,alphabet_dict)

    # print(char_counts)



        # else: # remove letter
        #     print(f'\n gray')
        #     unusedListRaw = remove_letter(unusedListRaw, last_guess_word[letter_location].lower())  
        #     print(f'\n new len is {len(unusedListRaw)}')

    print(f'unused list is now {len(unusedListRaw)} words left...')       

    best_word, best_score, worst_word, worst_score, myListDict, occurrances, weights = get_next_best_word(unusedListRaw)
    myList, best_three, worst_three = format_list_of_words_scored(myListDict)

    suggestBest = f"Best words: {', '.join(best_three)}"
    suggestWorst = f"Bravest words: {', '.join(worst_three)}"    

    chart_distro = distro_builder(occurrances)
    chart_histro = histo_builder(weights)

    # suggestBest = f"Suggested word: {best_word}, score of {best_score}"
    # suggestWorst = f"Bravest word: {worst_word}, score of {worst_score}"

    print(len(unusedListRaw))

    headerWordCount = f"Word Count: {len(unusedListRaw)}"

    return all_style, unusedListRaw, enter_flag, myList, headerWordCount, suggestBest, suggestWorst, chart_distro, chart_histro, completed_word_index, "", no_update

# change/toggle the color of the grid on click

@app.callback(
    Output({'type': 'wordle_letter', 'index': MATCH}, 'style',allow_duplicate=True),  
    Input({'type': 'wordle_letter', 'index': MATCH}, 'n_clicks'),  
    State({'type': 'wordle_letter', 'index': MATCH}, 'style'),  
    State("completed_word_index", "data"),  
    State("completed", "data"),     
)
def change_color(n_clicks, style, completed_word_index, completed):

    ctx = callback_context  # or use ctx = dash.callback_context.triggered_id (in Dash >= 2.9)
    triggered_id = ctx.triggered_id  # this is already a dict
    index = triggered_id["index"]
  
    index_row = index[0]
    # print(f'index_row: {index_row}')
    # print(f'completed_word_index: {completed_word_index}')

    if (completed == 1): # the puzzle is solved, don't allow updates
        return no_update

    if (completed_word_index+1 != int(index_row)):
        # some other row was clicked, so don't allow that
        return no_update

    if style is None or style['backgroundColor'] == '#555':
        return {'backgroundColor' : YELLOW}    
    elif style['backgroundColor'] == YELLOW:
        return {'backgroundColor' : GREEN}
    elif style['backgroundColor'] == GREEN:
        return {'backgroundColor' : '#555'}
    else:
        return {'backgroundColor' : '#333'}


@app.callback (
    Output("feedback", "value", allow_duplicate=True),            
    Output("feedback", "placeholder", allow_duplicate=True),            
    Input("submit_btn", 'n_clicks'),  
    State("feedback", "value"),            
)
def send_feedback(click, feedback):

    print("got feedback")

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")    

    # Append text to a file
    with open("feedback.txt", "a") as f:
        f.write(f"visit datetime: {dt_string}:\n")
        f.write(f"ip address: {request.remote_addr}\n")
        f.write(f"{feedback}\n\n")

    return "", "Thanks!"