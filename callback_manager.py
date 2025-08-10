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

# wrapper to handle/catch keypresses from the physical keyboard
@app.callback(
    Output("my_letters", "data", allow_duplicate=True),
    Input("key-listener", "n_keydowns"),
    Input("key-listener", "keydown"),
    State("my_letters", "data"),    
)
def on_keypress(n, key, data):

    keypressed = key['key']

    print(f"Key #{n}: {keypressed}, stored strokes = {data}")

    if len(keypressed) == 1 and keypressed.isalpha():
        return str(data) + str(keypressed.upper())
    elif keypressed == 'Backspace':
        if len(data) > 0:
            return data[:-1] 
        else:
            return no_update
    return no_update

# handle input from the virtual on-screen keyboard
@app.callback(
    Output("my_letters", "data", allow_duplicate=True),
    Input({"type": "key-btn", "index": ALL}, "n_clicks"),
    State("my_letters", "data"),
    prevent_initial_call=True
)
def update_text(n_clicks_list, data):
    ctx = callback_context
    if not ctx.triggered:
        return data

    key_id = ctx.triggered[0]["prop_id"].split(".")[0]
    key_name = eval(key_id)["index"]

    if key_name == "Backspace":
        return data[:-1]
    elif key_name == "Enter":
        return data
    else:
        return data + key_name


# @app.callback(
#     Output('suggestBest', 'children'),
#     Output('suggestWorst', 'children'),
#     Output('headerWordcount', 'children'),
#     Output('remainingWordsListScored', 'children'),
#     Output('chart_distro', 'figure'),
#     Output('chart_histro', 'figure'),
#     Output('usedWordleCount', 'children'),
#     Output('usedWordleList','children'),
#     Output('my_words','data'),
#     Output('my_letters','data', allow_duplicate=True),    
#     Input("url", "pathname"),
#     prevent_initial_call=False  # allow it to run on load
# )

# def initialize_everything(url):

#     start_time = time.time()
#     allListRaw = load_all_wordle_words()
# #    allList = format_list_of_words(allListRaw)

#     print("scraping used words...")
#     usedListRaw = load_used_words()
#     print("finished scraping!")
#     usedList = format_list_of_words(usedListRaw)

#     unusedListRaw = find_unused_words(allListRaw,usedListRaw)
# #    unusedList = format_list_of_words(unusedListRaw)

#     best_word, best_score, worst_word, worst_score, myListDict, occurrances, weights = get_next_best_word(unusedListRaw)
#     myList, best_three, worst_three = format_list_of_words_scored(myListDict)

#     print(occurrances)
#     # print(len(myListRaw))     
    
#     # jsonForSession = json.dumps(myListRaw)
#     # print(jsonForSession)

#     suggestBest = f"Best three guess words: {', '.join(best_three)}"
#     suggestWorst = f"Bravest three words: {', '.join(worst_three)}"

#     headerWordCount = f"Word Count: {len(unusedListRaw)}"

#     chart_distro = distro_builder(occurrances)
#     chart_histro = histo_builder(weights)

#     usedWordleCount = f"Word Count: {len(usedListRaw)}"

#     print(f"took {time.time() - start_time} secs to initialize")

#     my_letters = ''

#     return suggestBest, suggestWorst, headerWordCount, myList, chart_distro, chart_histro, usedWordleCount, usedList, unusedListRaw, my_letters

#process what happens when people click enter on each completed word

#(id={"type" : "wordle_letter_div", "index" : f'{row}_{col}'}

# @app.callback(
#     # Output({'type': 'wordle_letter', 'index': ALL}, 'disabled',allow_duplicate=True),  
#     # Output({'type': 'wordle_letter', 'index': ALL}, 'style',allow_duplicate=True),  
#     Output('my_words', 'data',allow_duplicate=True),   
#     Output('remainingWordsListScored', 'children',allow_duplicate=True),
#     Output('headerWordcount','children',allow_duplicate=True),
    
#     Output('suggestBest', 'children', allow_duplicate=True),
#     Output('suggestWorst', 'children', allow_duplicate=True),
#     Output('chart_distro', 'figure', allow_duplicate=True),
#     Output('chart_histro', 'figure', allow_duplicate=True),

#     Input("key-listener", "keydown"),

#     #Input({'type': 'wordle_letter', 'index': ALL}, 'n_submit'),  
#     State({'type': 'wordle_letter', 'index': ALL}, 'value'),
#     State({'type': 'wordle_letter', 'index': ALL}, 'style'),
#     State('my_words', 'data'),
#     prevent_initial_call=True  # allow it to run on load

# )
# def read_all_fields(key, value, style, unusedListRaw):

#     keypressed = key['key']
#     if keypressed != 'Enter':
#         return [no_update] * len(value), [no_update] * len(value), no_update, no_update, no_update, no_update, no_update, no_update, no_update

#     print("Enter key pressed")

#     print(value)
#     print(style)

#     print(f'\n unused list raw len: {len(unusedListRaw)}')

#     last_full_word_index = -1

#     # first identify if words have been completed

#     counter = 0
#     for x in value[0:30]:
#         if (len(x) == 1) & (x.isalpha()):
#             counter += 1 

#     print(f"found {counter} letters")
#     if counter % 5 > 0: # partial words, return immediately without doing anything
#         print("partial word, not continuing!")
#         return [no_update] * len(value), [no_update] * len(value), no_update, no_update, no_update, no_update, no_update, no_update, no_update


#     if all((len(x) == 1) & (x.isalpha()) for x in value[0:5]):
#         last_full_word_index = 0
    
#     if all((len(x) == 1) & (x.isalpha()) for x in value[5:10]):
#         last_full_word_index = 1
    
#     if all((len(x) == 1) & (x.isalpha()) for x in value[10:15]):
#         last_full_word_index = 2
    
#     if all((len(x) == 1) & (x.isalpha()) for x in value[15:20]):
#         last_full_word_index = 3
    
#     if all((len(x) == 1) & (x.isalpha()) for x in value[20:25]):
#         last_full_word_index = 4
    
#     if all((len(x) == 1) & (x.isalpha()) for x in value[25:30]):
#         last_full_word_index = 5
    
#     print(last_full_word_index)

#     print(f'\n{str(last_full_word_index)}')


#     # disable all rows that filled or empty; enable the current word cells

#     last_guess_word = []
#     last_guess_colors = []

#     disabled_list = []
#     style_list = []
#     for r in range(6):
#         for c in range(5):

#             if r == last_full_word_index+1: #activating the new row
#                 disabled_list.append(False) 
#                 style_list.append({'backgroundColor': '#555'})

#             else:
#                 disabled_list.append(True)

#                 if style[(r*5)+c]['backgroundColor'] == '#555': 
#                     style_list.append({'backgroundColor': '#333'})
#                 else:
#                     style_list.append({'backgroundColor': style[(r*5)+c]['backgroundColor']})

#                 # collect the values and colors of the guess
#                 if r == last_full_word_index:
#                     last_guess_word.append(value[(r*5)+c])
#                     last_guess_colors.append(style[(r*5)+c])                    
                
#     # next we update the list of remaining words, based on the previous word input (letters and colors)

#     print(f'\n{last_guess_word}, {last_guess_colors}')

#     for letter_location in range(5):

#         if last_guess_colors[letter_location]['backgroundColor'] == GREEN: # got a hit
#             print(f'\n green')
#             unusedListRaw = known_letter_location(unusedListRaw, last_guess_word[letter_location].lower(), letter_location)
#             print(f'\n new len is {len(unusedListRaw)}')
#         elif last_guess_colors[letter_location]['backgroundColor'] == YELLOW: # partial hit
#             print(f'\n yellow')
#             unusedListRaw = known_letter_unknown_location(unusedListRaw, last_guess_word[letter_location].lower(), letter_location)
#             print(f'\n new len is {len(unusedListRaw)}')
#         else: # remove letter
#             print(f'\n gray')
#             unusedListRaw = remove_letter(unusedListRaw, last_guess_word[letter_location].lower())  
#             print(f'\n new len is {len(unusedListRaw)}')

#         print(f'unused list is now {len(unusedListRaw)} words left...')

#     print(f'unused list is now {len(unusedListRaw)} words left...')       

#     best_word, best_score, worst_word, worst_score, myListDict, occurrances, weights = get_next_best_word(unusedListRaw)
#     myList, best_three, worst_three = format_list_of_words_scored(myListDict)

#     suggestBest = f"Best three guess words: {', '.join(best_three)}"
#     suggestWorst = f"Bravest three words: {', '.join(worst_three)}"    

#     chart_distro = distro_builder(occurrances)
#     chart_histro = histo_builder(weights)

#     # suggestBest = f"Suggested word: {best_word}, score of {best_score}"
#     # suggestWorst = f"Bravest word: {worst_word}, score of {worst_score}"

#     print(last_guess_word)
#     print(last_guess_colors)
#     print(len(unusedListRaw))

#     headerWordCount = f"Word Count: {len(unusedListRaw)}"

#     return disabled_list, style_list, unusedListRaw, myList, headerWordCount, suggestBest, suggestWorst, chart_distro, chart_histro

# change/toggle the color of the grid on click

@app.callback(
    Output({'type': 'wordle_letter', 'index': MATCH}, 'style',allow_duplicate=True),  
    Input({'type': 'wordle_letter_div', 'index': MATCH}, 'n_clicks'),  
    State({'type': 'wordle_letter', 'index': MATCH}, 'style'),  

)
def change_color(n_clicks, style):

    if style is None or style['backgroundColor'] == '#555':
        return {'backgroundColor' : '#E0E06C'}
    
    elif style['backgroundColor'] == "#E0E06C":

        return {'backgroundColor' : '#00AF82'}
    elif style['backgroundColor'] == '#00AF82':
        return {'backgroundColor' : '#555'}


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