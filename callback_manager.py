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
import pathlib

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
#   allList = format_list_of_words(allListRaw)

    #print("scraping used words...")
    usedListRaw = load_used_words()
    #print("finished scraping!")
    usedList = format_list_of_words(usedListRaw)

    unusedListRaw = find_unused_words(allListRaw,usedListRaw)
#    unusedList = format_list_of_words(unusedListRaw)

    best_word, best_score, worst_word, worst_score, myListDict, occurrances, weights = get_next_best_word(unusedListRaw)
    myList, best_three, worst_three = format_list_of_words_scored(myListDict)

    #print(occurrances)
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

    ip_address = get_client_ip()
    location_info = ip_location(ip_address)

    # Append text to a file
    with open("visits.txt", "a") as f:
        f.write(f"visit datetime: {dt_string}, ip address: {get_client_ip()}\n")
        f.write(f"{location_info}\n")

    return suggestBest, suggestWorst, headerWordCount, myList, chart_distro, chart_histro, usedWordleCount, \
        usedList, unusedListRaw, my_letters, enter_flag, backspace_flag, new_letter_flag, completed_word_index, 0, visit_counter


def get_client_ip():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip:
        ip = ip.split(",")[0].strip()  # first IP = client
    return ip

# wrapper to handle/catch keypresses from the physical keyboard - letters and backspace only

app.clientside_callback(
    """
    function(n, key, data, completed) {
        let enter_flag = window.dash_clientside.no_update;
        let backspace_flag = window.dash_clientside.no_update;
        let new_letter_flag = window.dash_clientside.no_update;

        if (completed === 1) {
            return [
                window.dash_clientside.no_update,
                window.dash_clientside.no_update,
                window.dash_clientside.no_update,
                window.dash_clientside.no_update
            ];
        }

        const keypressed = key.key;  // "a", "Backspace", "Enter", etc.
        console.log("Key #" + n + ": " + keypressed + ", stored strokes = " + data);

        if (keypressed.length === 1 && /^[a-zA-Z]$/.test(keypressed)) {
            data = String(data) + keypressed.toUpperCase();
            new_letter_flag = 1;
        } else if (keypressed === "Backspace") {
            if (data && data.length > 0) {
                backspace_flag = 1;
            }
        } else if (keypressed === "Enter") {
            console.log("Enter was pressed on physical keyboard");
            enter_flag = 1;
        }

        return [data, enter_flag, backspace_flag, new_letter_flag];
    }
    """,
    Output("my_letters", "data", allow_duplicate=True),
    Output("enter_flag", "data", allow_duplicate=True),
    Output("backspace_flag", "data", allow_duplicate=True),
    Output("new_letter_flag", "data", allow_duplicate=True),
    Input("key-listener", "n_keydowns"),
    Input("key-listener", "keydown"),
    State("my_letters", "data"),
    State("completed", "data"),
)


# @app.callback(
#     Output("my_letters", "data", allow_duplicate=True),
#     Output("enter_flag", "data", allow_duplicate=True),    
#     Output("backspace_flag", "data", allow_duplicate=True),   
#     Output("new_letter_flag", "data", allow_duplicate=True),              
#     Input("key-listener", "n_keydowns"),
#     Input("key-listener", "keydown"),
#     State("my_letters", "data"),    
#     State("completed", "data"),    

# )
# def on_physical_keypress(n, key, data, completed):

#     enter_flag = no_update
#     backspace_flag = no_update
#     new_letter_flag = no_update

#     if (completed == 1):
#         return no_update, no_update, no_update, no_update

#     keypressed = key['key']

#     print(f"Key #{n}: {keypressed}, stored strokes = {data}")

#     if len(keypressed) == 1 and keypressed.isalpha():
#         data = str(data) + str(keypressed.upper())
#         new_letter_flag = 1
#     elif keypressed == 'Backspace':
#         if len(data) > 0:
#             backspace_flag = 1
#     elif keypressed == 'Enter':
#         print("Enter was pressed on physical keyboard")
#         enter_flag = 1
    
#     return data, enter_flag, backspace_flag, new_letter_flag

# handle input from the virtual on-screen keyboard - letters and backspace only
app.clientside_callback(
    """
    function(n_clicks_list, data, completed) {
        let enter_flag = window.dash_clientside.no_update;
        let backspace_flag = window.dash_clientside.no_update;
        let new_letter_flag = window.dash_clientside.no_update;

        if (completed === 1) {
            return [
                window.dash_clientside.no_update,
                window.dash_clientside.no_update,
                window.dash_clientside.no_update,
                window.dash_clientside.no_update
            ];
        }

        const ctx = dash_clientside.callback_context;
        if (!ctx.triggered || ctx.triggered.length === 0) {
            return [data, enter_flag, backspace_flag, new_letter_flag];
        }

        // ctx.triggered[0].prop_id looks like '{"type":"key-btn","index":"A"}.n_clicks'
        const key_id = ctx.triggered[0].prop_id.split(".")[0];
        const key_obj = JSON.parse(key_id);   // convert string back to object
        const key_name = key_obj.index;

        if (key_name === "Backspace") {
            backspace_flag = 1;
        } else if (key_name === "Enter") {
            console.log("Enter was clicked on on-screen keyboard");
            enter_flag = 1;
        } else {
            data = (data || "") + key_name;
            new_letter_flag = 1;
        }

        return [data, enter_flag, backspace_flag, new_letter_flag];
    }
    """,
    Output("my_letters", "data", allow_duplicate=True),
    Output("enter_flag", "data", allow_duplicate=True),
    Output("backspace_flag", "data", allow_duplicate=True),
    Output("new_letter_flag", "data", allow_duplicate=True),
    Input({"type": "key-btn", "index": ALL}, "n_clicks"),
    State("my_letters", "data"),
    State("completed", "data"),
    prevent_initial_call=True
)


# @app.callback(
#     Output("my_letters", "data", allow_duplicate=True),
#     Output("enter_flag", "data", allow_duplicate=True),    
#     Output("backspace_flag", "data", allow_duplicate=True),   
#     Output("new_letter_flag", "data", allow_duplicate=True),        
#     Input({"type": "key-btn", "index": ALL}, "n_clicks"),
#     State("my_letters", "data"),
#     State("completed", "data"),    
#     prevent_initial_call=True
# )
# def on_onscreen_keypress(n_clicks_list, data, completed):

#     enter_flag = no_update
#     backspace_flag = no_update
#     new_letter_flag = no_update

#     if (completed == 1):
#         return no_update, no_update, no_update, no_update

#     ctx = callback_context
#     if not ctx.triggered:
#         return data, enter_flag

#     key_id = ctx.triggered[0]["prop_id"].split(".")[0]
#     key_name = eval(key_id)["index"]

#     if key_name == "Backspace":
#         backspace_flag = 1
#     elif key_name == "Enter":
#         print("Enter was clicked on on-screen keyboard")
#         enter_flag = 1
#     else:
#         data = data + key_name
#         new_letter_flag = 1

#     return data, enter_flag, backspace_flag, new_letter_flag

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

    #print("pressed_letter callback was triggered - checking new_letter_flag")

    # nothing to update on first load
    #all_styles =  [no_update] * len(ids)
    all_children =  [no_update] * len(ids)    

    if (new_letter_flag != 1):
        #print("new_letter_flag was found to be <> 1, so doing nothing")        
        new_letter_flag = 0
        return all_children, new_letter_flag, my_letters

    #print("new_letter_flag was found to be 1, so do something then clear the flag")
    new_letter_flag = 0

    new_letter = my_letters[-1:]
    #print(new_letter)

    #print(f'the len of my_letters = {len(my_letters)}')

    current_row = (len(my_letters)-1) // 5 # the current row
    current_row_position = (len(my_letters)-1) % 5 # position in row
    target_id = f'{current_row}_{current_row_position}'
    #print(target_id)

    if completed_word_index + 1 != current_row: # attempting to go past current word's end
        new_letter_flag = 0
        #print(f"can't go past there! my_letters={my_letters}")
        my_letters = my_letters[:((completed_word_index+1)*5)+5] # truncate letters to what is allowed
        #print(f"fixed that! my_letters={my_letters}")        
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

    #print("pressed_backspace callback was triggered - checking backspace_flag")
    all_children =  [no_update] * len(ids)   

    if (backspace_flag != 1):
        #print("Backspace flag was found to be <> 1, so doing nothing")        
        backspace_flag = 0
        return all_children, backspace_flag, my_letters

    #print("Enter flag was found to be 1, so do something then clear the flag")
    backspace_flag = 0

    #print(f'the len of my_letters = {len(my_letters)}')

    current_row = (len(my_letters)-1) // 5 # the current row
    current_row_position = (len(my_letters)-1) % 5 # position in row
    target_id = f'{current_row}_{current_row_position}'

    if (current_row_position >= 0) and (completed_word_index+1 == current_row): # there's letter(s) in this row, so delete one letter
        my_letters = my_letters[:-1]
        #print(f"After backspace, my_letters={my_letters}")        
    else:
        return all_children, backspace_flag,my_letters

    #print(f'removing from {target_id}')

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
    Output("modal", "is_open"), 
    Output("modal_body", "children"),
    Input("enter_flag", "data"),   
    State("my_letters", "data"),    
    State('my_words', 'data'),     
    State({'type': 'wordle_letter', 'index': ALL}, 'style'),
    State("completed_word_index", "data"),    

    prevent_initial_call=True  # allow it to run on load

)
def pressed_enter(enter_flag, my_letters, unusedListRaw, ids, completed_word_index):

    #print("pressed_enter callback was triggered - checking enter_flag")
    all_style =  [no_update] * len(ids)   

    if (enter_flag != 1):
        #print("Enter flag was found to be <> 1, so doing nothing")        
        enter_flag = 0
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "", no_update, False, no_update

    enter_flag = 0

    if (len(my_letters) == 0) or (len(my_letters) % 5 != 0): # check if a word is actually fully entered
        #print("Incomplete/no word found, so doing nothing")
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "", no_update, False, no_update

    # check if this completed word is a new completed word, or is still last word completed word
    new_full_word_index = int((len(my_letters) // 5)-1)
    #print(new_full_word_index)
    #print(completed_word_index)
    if new_full_word_index <= completed_word_index:
        #print("Enter was pressed, but there's no new word")
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "", no_update, False, no_update       

    last_guess_word = my_letters[-5:]
    # print(last_guess_word)

    with open("assets/all_5_letter_words_loose.csv", newline="", encoding="utf-8") as csvfile:
        all_words_loose = csvfile.read().splitlines()

    # print(all_words_loose)
    # print(last_guess_word.lower())

    if last_guess_word.lower() == 'zffff': #show feedback

        FILE_PATH = pathlib.Path("feedback.txt").expanduser()

        feedback = ''
        try:
            feedback = FILE_PATH.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"Error opening file: {e}")

        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "", no_update, True, feedback   

    if last_guess_word.lower() == 'zvvvv': #show visits

        FILE_PATH = pathlib.Path("visits.txt").expanduser()

        visits = ''
        try:
            visits = FILE_PATH.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"Error opening file: {e}")

        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "", no_update, True, visits   



    if last_guess_word.lower() not in all_words_loose:
        #print(f"{last_guess_word} is probably not even a word!")
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "That is not a word!", no_update, False, no_update         

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
            #print(f'\n green')           
            green_counter += 1
            unusedListRaw = known_letter_location(unusedListRaw, last_guess_word[letter_location].lower(), letter_location)
            #print(f'\n new len is {len(unusedListRaw)}')
        elif last_guess_colors[letter_location]['backgroundColor'] == YELLOW: # partial hit
            #print(f'\n yellow')
            unusedListRaw = known_letter_unknown_location(unusedListRaw, last_guess_word[letter_location].lower(), letter_location)
            #print(f'\n new len is {len(unusedListRaw)}')
        else:
            pass

    # the word was correct, don't go any further
    if green_counter == 5:
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "You found it! (Refresh to restart)", 1, False, no_update         
        
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

    #print(f'unused list is now {len(unusedListRaw)} words left...')       

    best_word, best_score, worst_word, worst_score, myListDict, occurrances, weights = get_next_best_word(unusedListRaw)
    myList, best_three, worst_three = format_list_of_words_scored(myListDict)

    suggestBest = f"Best words: {', '.join(best_three)}"
    suggestWorst = f"Bravest words: {', '.join(worst_three)}"    

    chart_distro = distro_builder(occurrances)
    chart_histro = histo_builder(weights)

    # suggestBest = f"Suggested word: {best_word}, score of {best_score}"
    # suggestWorst = f"Bravest word: {worst_word}, score of {worst_score}"

    #print(len(unusedListRaw))

    headerWordCount = f"Word Count: {len(unusedListRaw)}"

    return all_style, unusedListRaw, enter_flag, myList, headerWordCount, suggestBest, suggestWorst, chart_distro, chart_histro, completed_word_index, "", no_update, False, no_update

# change/toggle the color of the grid on click
# removing this in favor of the client-side callback below this
# @app.callback(
#     Output({'type': 'wordle_letter', 'index': MATCH}, 'style', allow_duplicate=True),  
#     Input({'type': 'wordle_letter', 'index': MATCH}, 'n_clicks'),  
#     State({'type': 'wordle_letter', 'index': MATCH}, 'style'),  
#     State("completed_word_index", "data"),  
#     State("completed", "data"),     
# )
# def change_color(n_clicks, style, completed_word_index, completed):

#     ctx = callback_context  # or use ctx = dash.callback_context.triggered_id (in Dash >= 2.9)
#     triggered_id = ctx.triggered_id  # this is already a dict
#     index = triggered_id["index"]
  
#     index_row = index[0]
#     # print(f'index_row: {index_row}')
#     # print(f'completed_word_index: {completed_word_index}')

#     if (completed == 1): # the puzzle is solved, don't allow updates
#         return no_update

#     if (completed_word_index+1 != int(index_row)):
#         # some other row was clicked, so don't allow that
#         return no_update

#     if style is None or style['backgroundColor'] == '#555':
#         return {'backgroundColor' : YELLOW}    
#     elif style['backgroundColor'] == YELLOW:
#         return {'backgroundColor' : GREEN}
#     elif style['backgroundColor'] == GREEN:
#         return {'backgroundColor' : '#555'}
#     else:
#         return {'backgroundColor' : '#333'}


app.clientside_callback(
    """
    function(clicked,id,style,completed_word_index,completed,my_letters) {
        
        const YELLOW = "#b59f3b";
        const GREEN = "#00AF82";
        const row = id.index.charAt(0);  
              
        // puzzle solved → no update
        if (completed === 1) {
            return window.dash_clientside.no_update;
        }

        // wrong row clicked → no update
        if (completed_word_index + 1 !== parseInt(row)) {
            return window.dash_clientside.no_update;
        }

        // style might be null/undefined the first time
        if (!style || style.backgroundColor === "#555") {
            return {backgroundColor: YELLOW};
        } else if (style.backgroundColor === YELLOW) {
            return {backgroundColor: GREEN};
        } else if (style.backgroundColor === GREEN) {
            return {backgroundColor: "#555"};
        } else {
            return {backgroundColor: "#333"};
        }

    }
    """,
    Output({'type': 'wordle_letter', 'index': MATCH}, 'style', allow_duplicate=True),  
    Input({'type': 'wordle_letter', 'index': MATCH}, 'n_clicks'),  
    Input({'type': 'wordle_letter', 'index': MATCH}, 'id'),  
    State({'type': 'wordle_letter', 'index': MATCH}, 'style'),  
    State("completed_word_index", "data"),  
    State("completed", "data"),     
    State("my_letters", "data"),     
)



@app.callback (
    Output("feedback", "value", allow_duplicate=True),            
    Output("feedback", "placeholder", allow_duplicate=True),            
    Input("submit_btn", 'n_clicks'),  
    State("feedback", "value"),            
)
def send_feedback(click, feedback):

    #print("got feedback")

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")    

    ip_address = get_client_ip()
    location_info = ip_location(ip_address)

    # Append text to a file
    with open("feedback.txt", "a") as f:
        f.write(f"visit datetime: {dt_string}:\n")
        f.write(f"ip address: {ip_address}\n")
        f.write(f"{location_info}\n")
        f.write(f"{feedback}\n\n")

    return "", "Thanks!"


def ip_location(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = resp.json()

        if data.get("status") == "success":
            return f"{data['query']} - {data['country']}, {data['regionName']}, {data['city']}"
        else:
            return f"{ip} - Location lookup failed"
    except Exception as e:
        return f"{ip} - Error: {e}"
    
# # This JS will capture keydown events on the page and write them to a store
# app.clientside_callback(
#     """
#     function(n_clicks) {
#         document.addEventListener('keydown', function(event) {
#             const keyPressed = event.key;
#             const store = document.querySelector('[data-dash-is-loading="false"][id="my_letters"]');
#             if (store) {
#                 store.setAttribute('data-dash-data', JSON.stringify(keyPressed));
#                 store.dispatchEvent(new Event('input', { bubbles: true }));
#             }
#         }, { once: true });
#         return null;
#     }
#     """,
#     Output('my_letters', 'data'),
#     Input('dummy_input', 'value')  # dummy trigger to load the script
# )

# # Client-side callback: write pressed keys to dcc.Store
# app.clientside_callback(
#     """
#     function(n_clicks) {

#         alert('got here!');
#         if (!window.keyCaptureInitialized) {
#             window.keyCaptureInitialized = true;

#             window.loggedKeys = "";

#             window.addEventListener("keydown", function(e) {
#                 const key = e.key;
#                 const printable = key.length === 1 ? key : "[" + key + "]";
#                 window.loggedKeys += printable;

#                 const store = document.querySelector('[data-dash-is-loading="false"][id="key_log_store"]');
#                 if (store) {
#                     store.setAttribute('data-dash-store', window.loggedKeys);
#                     store.dispatchEvent(new Event('input', { bubbles: true }));
#                 }
#             });
#         }
#         return "";
#     }
#     """,
#     Output("script-container", "children"),
#     Input("script-container", "n_clicks"),  # Just to trigger once
#     prevent_initial_call=False
# )


# @app.callback(
#     Output("output_div", "children",allow_duplicate=True),
#     Input("keyboard_listener", "event"),
#     prevent_initial_call = True
# )
# def capture_keypress(event):

#     print(event)
#     return str(event)


# # below is an inelegant way to move focus between the respective cells
# app.clientside_callback(
#     """
#     function(v0, v1, v2, v3, v4) {

#         v0 = JSON.stringify(v0, Object.keys(v0).sort());
#         v1 = JSON.stringify(v1, Object.keys(v1).sort());
#         v2 = JSON.stringify(v2, Object.keys(v2).sort());
#         v3 = JSON.stringify(v3, Object.keys(v3).sort());
#         v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
#         let ids = ['{"index":"0_0","type":"wordle_letter"}','{"index":"0_1","type":"wordle_letter"}','{"index":"0_2","type":"wordle_letter"}','{"index":"0_3","type":"wordle_letter"}','{"index":"0_4","type":"wordle_letter"}' ];
#         let values = [v0, v1, v2, v3, v4];
#         for (let i = 0; i < values.length; i++) {

#             this_value = values[i][1];
            
#             if (this_value && this_value.length === 1) { 
#                 const next = document.getElementById(ids[i + 1]);
#                 if (next && document.activeElement.id === ids[i]) {
#                     setTimeout(() => next.focus(), 0);
#                 }
#             }
#         }
#         return null;
#     }
#     """,
#     Output('output_div', 'children', allow_duplicate=True),
#     Input({"index":"0_0","type":"wordle_letter"}, 'value'),
#     Input({"index":"0_1","type":"wordle_letter"}, 'value'),
#     Input({"index":"0_2","type":"wordle_letter"}, 'value'),
#     Input({"index":"0_3","type":"wordle_letter"}, 'value'),
#     Input({"index":"0_4","type":"wordle_letter"}, 'value'),        
# )

# app.clientside_callback(
#     """
#     function(v0, v1, v2, v3, v4) {

#         v0 = JSON.stringify(v0, Object.keys(v0).sort());
#         v1 = JSON.stringify(v1, Object.keys(v1).sort());
#         v2 = JSON.stringify(v2, Object.keys(v2).sort());
#         v3 = JSON.stringify(v3, Object.keys(v3).sort());
#         v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
#         let ids = ['{"index":"1_0","type":"wordle_letter"}','{"index":"1_1","type":"wordle_letter"}','{"index":"1_2","type":"wordle_letter"}','{"index":"1_3","type":"wordle_letter"}','{"index":"1_4","type":"wordle_letter"}' ];
#         let values = [v0, v1, v2, v3, v4];
#         for (let i = 0; i < values.length; i++) {

#             this_value = values[i][1];
            
#             if (this_value && this_value.length === 1) { 
#                 const next = document.getElementById(ids[i + 1]);
#                 if (next && document.activeElement.id === ids[i]) {
#                     setTimeout(() => next.focus(), 0);
#                 }
#             }
#         }
#         return null;
#     }
#     """,
#     Output('output_div', 'children', allow_duplicate=True),
#     Input({"index":"1_0","type":"wordle_letter"}, 'value'),
#     Input({"index":"1_1","type":"wordle_letter"}, 'value'),
#     Input({"index":"1_2","type":"wordle_letter"}, 'value'),
#     Input({"index":"1_3","type":"wordle_letter"}, 'value'),
#     Input({"index":"1_4","type":"wordle_letter"}, 'value'),        
# )

# app.clientside_callback(
#     """
#     function(v0, v1, v2, v3, v4) {

#         v0 = JSON.stringify(v0, Object.keys(v0).sort());
#         v1 = JSON.stringify(v1, Object.keys(v1).sort());
#         v2 = JSON.stringify(v2, Object.keys(v2).sort());
#         v3 = JSON.stringify(v3, Object.keys(v3).sort());
#         v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
#         let ids = ['{"index":"2_0","type":"wordle_letter"}','{"index":"2_1","type":"wordle_letter"}','{"index":"2_2","type":"wordle_letter"}','{"index":"2_3","type":"wordle_letter"}','{"index":"2_4","type":"wordle_letter"}' ];
#         let values = [v0, v1, v2, v3, v4];
#         for (let i = 0; i < values.length; i++) {

#             this_value = values[i][1];
            
#             if (this_value && this_value.length === 1) { 
#                 const next = document.getElementById(ids[i + 1]);
#                 if (next && document.activeElement.id === ids[i]) {
#                     setTimeout(() => next.focus(), 0);
#                 }
#             }
#         }
#         return null;
#     }
#     """,
#     Output('output_div', 'children', allow_duplicate=True),
#     Input({"index":"2_0","type":"wordle_letter"}, 'value'),
#     Input({"index":"2_1","type":"wordle_letter"}, 'value'),
#     Input({"index":"2_2","type":"wordle_letter"}, 'value'),
#     Input({"index":"2_3","type":"wordle_letter"}, 'value'),
#     Input({"index":"2_4","type":"wordle_letter"}, 'value'),        
# )

# app.clientside_callback(
#     """
#     function(v0, v1, v2, v3, v4) {

#         v0 = JSON.stringify(v0, Object.keys(v0).sort());
#         v1 = JSON.stringify(v1, Object.keys(v1).sort());
#         v2 = JSON.stringify(v2, Object.keys(v2).sort());
#         v3 = JSON.stringify(v3, Object.keys(v3).sort());
#         v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
#         let ids = ['{"index":"3_0","type":"wordle_letter"}','{"index":"3_1","type":"wordle_letter"}','{"index":"3_2","type":"wordle_letter"}','{"index":"3_3","type":"wordle_letter"}','{"index":"3_4","type":"wordle_letter"}' ];
#         let values = [v0, v1, v2, v3, v4];
#         for (let i = 0; i < values.length; i++) {

#             this_value = values[i][1];
            
#             if (this_value && this_value.length === 1) { 
#                 const next = document.getElementById(ids[i + 1]);
#                 if (next && document.activeElement.id === ids[i]) {
#                     setTimeout(() => next.focus(), 0);
#                 }
#             }
#         }
#         return null;
#     }
#     """,
#     Output('output_div', 'children', allow_duplicate=True),
#     Input({"index":"3_0","type":"wordle_letter"}, 'value'),
#     Input({"index":"3_1","type":"wordle_letter"}, 'value'),
#     Input({"index":"3_2","type":"wordle_letter"}, 'value'),
#     Input({"index":"3_3","type":"wordle_letter"}, 'value'),
#     Input({"index":"3_4","type":"wordle_letter"}, 'value'),        
# )

# app.clientside_callback(
#     """
#     function(v0, v1, v2, v3, v4) {

#         v0 = JSON.stringify(v0, Object.keys(v0).sort());
#         v1 = JSON.stringify(v1, Object.keys(v1).sort());
#         v2 = JSON.stringify(v2, Object.keys(v2).sort());
#         v3 = JSON.stringify(v3, Object.keys(v3).sort());
#         v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
#         let ids = ['{"index":"4_0","type":"wordle_letter"}','{"index":"4_1","type":"wordle_letter"}','{"index":"4_2","type":"wordle_letter"}','{"index":"4_3","type":"wordle_letter"}','{"index":"4_4","type":"wordle_letter"}' ];
#         let values = [v0, v1, v2, v3, v4];
#         for (let i = 0; i < values.length; i++) {

#             this_value = values[i][1];
            
#             if (this_value && this_value.length === 1) { 
#                 const next = document.getElementById(ids[i + 1]);
#                 if (next && document.activeElement.id === ids[i]) {
#                     setTimeout(() => next.focus(), 0);
#                 }
#             }
#         }
#         return null;
#     }
#     """,
#     Output('output_div', 'children', allow_duplicate=True),
#     Input({"index":"4_0","type":"wordle_letter"}, 'value'),
#     Input({"index":"4_1","type":"wordle_letter"}, 'value'),
#     Input({"index":"4_2","type":"wordle_letter"}, 'value'),
#     Input({"index":"4_3","type":"wordle_letter"}, 'value'),
#     Input({"index":"4_4","type":"wordle_letter"}, 'value'),        
# )

# app.clientside_callback(
#     """
#     function(v0, v1, v2, v3, v4) {

#         v0 = JSON.stringify(v0, Object.keys(v0).sort());
#         v1 = JSON.stringify(v1, Object.keys(v1).sort());
#         v2 = JSON.stringify(v2, Object.keys(v2).sort());
#         v3 = JSON.stringify(v3, Object.keys(v3).sort());
#         v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
#         let ids = ['{"index":"5_0","type":"wordle_letter"}','{"index":"5_1","type":"wordle_letter"}','{"index":"5_2","type":"wordle_letter"}','{"index":"5_3","type":"wordle_letter"}','{"index":"5_4","type":"wordle_letter"}' ];
#         let values = [v0, v1, v2, v3, v4];
#         for (let i = 0; i < values.length; i++) {

#             this_value = values[i][1];
            
#             if (this_value && this_value.length === 1) { 
#                 const next = document.getElementById(ids[i + 1]);
#                 if (next && document.activeElement.id === ids[i]) {
#                     setTimeout(() => next.focus(), 0);
#                 }
#             }
#         }
#         return null;
#     }
#     """,
#     Output('output_div', 'children', allow_duplicate=True),
#     Input({"index":"5_0","type":"wordle_letter"}, 'value'),
#     Input({"index":"5_1","type":"wordle_letter"}, 'value'),
#     Input({"index":"5_2","type":"wordle_letter"}, 'value'),
#     Input({"index":"5_3","type":"wordle_letter"}, 'value'),
#     Input({"index":"5_4","type":"wordle_letter"}, 'value'),        
# )