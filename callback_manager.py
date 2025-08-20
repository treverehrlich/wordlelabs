from dash import Input, Output, State, html, dcc, ALL, MATCH, no_update, callback_context
from serving import app
from content_rendering import *
from functions import *
from constants import *
import csv
import uuid
import time

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
    Output("all_words", "data", allow_duplicate=True),      
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

    return suggestBest, suggestWorst, headerWordCount, myList, chart_distro, chart_histro, usedWordleCount, \
        usedList, unusedListRaw, my_letters, enter_flag, backspace_flag, new_letter_flag, completed_word_index, allListRaw


# wrapper to handle/catch keypresses from the physical keyboard - letters and backspace only
@app.callback(
    Output("my_letters", "data", allow_duplicate=True),
    Output("enter_flag", "data", allow_duplicate=True),    
    Output("backspace_flag", "data", allow_duplicate=True),   
    Output("new_letter_flag", "data", allow_duplicate=True),              
    Input("key-listener", "n_keydowns"),
    Input("key-listener", "keydown"),
    State("my_letters", "data"),    
)
def on_physical_keypress(n, key, data):

    enter_flag = no_update
    backspace_flag = no_update
    new_letter_flag = no_update

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
    prevent_initial_call=True
)
def on_onscreen_keypress(n_clicks_list, data):

    enter_flag = no_update
    backspace_flag = no_update
    new_letter_flag = no_update

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
    print(new_letter)

    print(f'the len of my_letters = {len(my_letters)}')

    current_row = (len(my_letters)-1) // 5 # the current row
    current_row_position = (len(my_letters)-1) % 5 # position in row
    target_id = f'{current_row}_{current_row_position}'
    print(target_id)

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

    if current_row_position >= 0: # there's letter(s) in this row, so delete one letter
        my_letters = my_letters[:-1]
        print(f"After backspace, my_letters={my_letters}")        

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
    Input("enter_flag", "data"),   
    State("my_letters", "data"),    
    State('my_words', 'data'),     
    State({'type': 'wordle_letter', 'index': ALL}, 'style'),
    State("completed_word_index", "data"),  
    State("all_words", "data"),        

    prevent_initial_call=True  # allow it to run on load

)
def pressed_enter(enter_flag, my_letters, unusedListRaw, ids, completed_word_index, all_words):

    print("pressed_enter callback was triggered - checking enter_flag")
    all_style =  [no_update] * len(ids)   

    if (enter_flag != 1):
        print("Enter flag was found to be <> 1, so doing nothing")        
        enter_flag = 0
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, ""

    enter_flag = 0

    if (len(my_letters) == 0) or (len(my_letters) % 5 != 0): # check if a word is actually fully entered
        print("Incomplete/no word found, so doing nothing")
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, ""

    # check if this completed word is a new completed word, or is still last word completed word
    new_full_word_index = int((len(my_letters) // 5)-1)
    print(new_full_word_index)
    print(completed_word_index)
    if new_full_word_index <= completed_word_index:
        print("Enter was pressed, but there's no new word")
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, ""        


    last_guess_word = my_letters[-5:]
    print(last_guess_word)

    if last_guess_word.lower() not in all_words:
        print(f"{last_guess_word} is not a word!")
        return all_style, no_update, enter_flag, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "That is not a valid word!"         

    completed_word_index += 1 # finished a word
    last_guess_colors = []

    # get current row colors
    for c in range(5):
        last_guess_colors.append(ids[(completed_word_index*5)+c]) 


    # highlight the next row to guess
    all_style = []
    for r in range(6):
        for c in range(5):
            if r == completed_word_index+1:
                all_style.append({'backgroundColor': '#555'})    
            else: 
                all_style.append(no_update)
        
    
    print(all_style)
    print(last_guess_colors)
    print(f'\n{last_guess_word}')
              
#     # next we update the list of remaining words, based on the previous word input (letters and colors)

    for letter_location in range(5):

        if last_guess_colors[letter_location]['backgroundColor'] == GREEN: # got a hit
            print(f'\n green')
            unusedListRaw = known_letter_location(unusedListRaw, last_guess_word[letter_location].lower(), letter_location)
            print(f'\n new len is {len(unusedListRaw)}')
        elif last_guess_colors[letter_location]['backgroundColor'] == YELLOW: # partial hit
            print(f'\n yellow')
            unusedListRaw = known_letter_unknown_location(unusedListRaw, last_guess_word[letter_location].lower(), letter_location)
            print(f'\n new len is {len(unusedListRaw)}')
        else: # remove letter
            print(f'\n gray')
            unusedListRaw = remove_letter(unusedListRaw, last_guess_word[letter_location].lower())  
            print(f'\n new len is {len(unusedListRaw)}')

        print(f'unused list is now {len(unusedListRaw)} words left...')

    print(f'unused list is now {len(unusedListRaw)} words left...')       

    best_word, best_score, worst_word, worst_score, myListDict, occurrances, weights = get_next_best_word(unusedListRaw)
    myList, best_three, worst_three = format_list_of_words_scored(myListDict)

    suggestBest = f"Best three guess words: {', '.join(best_three)}"
    suggestWorst = f"Bravest three words: {', '.join(worst_three)}"    

    chart_distro = distro_builder(occurrances)
    chart_histro = histo_builder(weights)

    # suggestBest = f"Suggested word: {best_word}, score of {best_score}"
    # suggestWorst = f"Bravest word: {worst_word}, score of {worst_score}"

    print(len(unusedListRaw))

    headerWordCount = f"Word Count: {len(unusedListRaw)}"

    return all_style, unusedListRaw, enter_flag, myList, headerWordCount, suggestBest, suggestWorst, chart_distro, chart_histro, completed_word_index, ""

# change/toggle the color of the grid on click

@app.callback(
    Output({'type': 'wordle_letter', 'index': MATCH}, 'style',allow_duplicate=True),  
    Input({'type': 'wordle_letter', 'index': MATCH}, 'n_clicks'),  
    State({'type': 'wordle_letter', 'index': MATCH}, 'style'),  

)
def change_color(n_clicks, style):

    if style is None or style['backgroundColor'] == '#555':
        return {'backgroundColor' : '#E0E06C'}    
    elif style['backgroundColor'] == "#E0E06C":
        return {'backgroundColor' : '#00AF82'}
    elif style['backgroundColor'] == '#00AF82':
        return {'backgroundColor' : '#555'}
    else:
        return {'backgroundColor' : '#333'}


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