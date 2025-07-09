from dash import Input, Output, State, html, dcc, ALL, MATCH
from serving import app
from content_rendering import *
from functions import *


def get_main_layout():
    return render_main_layout()

@app.callback(
    Output('output_div', 'children',allow_duplicate=True),
    Output({'type': 'wordle_letter', 'index': ALL}, 'disabled',allow_duplicate=True),  
    Output({'type': 'wordle_letter', 'index': ALL}, 'style',allow_duplicate=True),  
    Input({'type': 'wordle_letter', 'index': ALL}, 'n_submit'),  
    State({'type': 'wordle_letter', 'index': ALL}, 'value'),
    State({'type': 'wordle_letter', 'index': ALL}, 'style')
)
def read_all_fields(n_clicks, value, style):

    print(n_clicks)
    print(value)
    print(style)

    last_full_word_index = -1

    if all((len(x) == 1) & (x.isalpha()) for x in value[0:5]):
        last_full_word_index = 0
    
    if all((len(x) == 1) & (x.isalpha()) for x in value[5:10]):
        last_full_word_index = 1
    
    if all((len(x) == 1) & (x.isalpha()) for x in value[10:15]):
        last_full_word_index = 2
    
    if all((len(x) == 1) & (x.isalpha()) for x in value[15:20]):
        last_full_word_index = 3
    
    if all((len(x) == 1) & (x.isalpha()) for x in value[20:25]):
        last_full_word_index = 4
    
    if all((len(x) == 1) & (x.isalpha()) for x in value[25:30]):
        last_full_word_index = 5
    
    print(last_full_word_index)

    disabled_list = []
    style_list = []
    for r in range(6):
        for c in range(5):
            if r == last_full_word_index+1: #activating the new row
                disabled_list.append(False) 
                style_list.append({'background-color': '#555'})

            else:
                disabled_list.append(True)

                if style[(r*5)+c]['background-color'] == '#555': 
                    style_list.append({'background-color': '#333'})
                else:
                    style_list.append({'background-color': style[(r*5)+c]['background-color']})
            

                

    return '1',disabled_list,style_list

@app.callback(
    Output({'type': 'wordle_letter', 'index': MATCH}, 'style',allow_duplicate=True),  
    Input({'type': 'wordle_letter_div', 'index': MATCH}, 'n_clicks'),  
    State({'type': 'wordle_letter', 'index': MATCH}, 'style'),  

)
def change_color(n_clicks, style):

    if style is None or style['background-color'] == '#555':
        return {'background-color' : '#E0E06C'}
    
    elif style['background-color'] == "#E0E06C":

        return {'background-color' : '#00AF82'}
    elif style['background-color'] == '#00AF82':
        return {'background-color' : '#555'}


app.clientside_callback(
    """
    function(v0, v1, v2, v3, v4) {

        v0 = JSON.stringify(v0, Object.keys(v0).sort());
        v1 = JSON.stringify(v1, Object.keys(v1).sort());
        v2 = JSON.stringify(v2, Object.keys(v2).sort());
        v3 = JSON.stringify(v3, Object.keys(v3).sort());
        v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
        let ids = ['{"index":"0_0","type":"wordle_letter"}','{"index":"0_1","type":"wordle_letter"}','{"index":"0_2","type":"wordle_letter"}','{"index":"0_3","type":"wordle_letter"}','{"index":"0_4","type":"wordle_letter"}' ];
        let values = [v0, v1, v2, v3, v4];
        for (let i = 0; i < values.length; i++) {

            this_value = values[i][1];
            
            if (this_value && this_value.length === 1) { 
                const next = document.getElementById(ids[i + 1]);
                if (next && document.activeElement.id === ids[i]) {
                    setTimeout(() => next.focus(), 0);
                }
            }
        }
        return null;
    }
    """,
    Output('output_div', 'children', allow_duplicate=True),
    Input({"index":"0_0","type":"wordle_letter"}, 'value'),
    Input({"index":"0_1","type":"wordle_letter"}, 'value'),
    Input({"index":"0_2","type":"wordle_letter"}, 'value'),
    Input({"index":"0_3","type":"wordle_letter"}, 'value'),
    Input({"index":"0_4","type":"wordle_letter"}, 'value'),        
)

app.clientside_callback(
    """
    function(v0, v1, v2, v3, v4) {

        v0 = JSON.stringify(v0, Object.keys(v0).sort());
        v1 = JSON.stringify(v1, Object.keys(v1).sort());
        v2 = JSON.stringify(v2, Object.keys(v2).sort());
        v3 = JSON.stringify(v3, Object.keys(v3).sort());
        v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
        let ids = ['{"index":"1_0","type":"wordle_letter"}','{"index":"1_1","type":"wordle_letter"}','{"index":"1_2","type":"wordle_letter"}','{"index":"1_3","type":"wordle_letter"}','{"index":"1_4","type":"wordle_letter"}' ];
        let values = [v0, v1, v2, v3, v4];
        for (let i = 0; i < values.length; i++) {

            this_value = values[i][1];
            
            if (this_value && this_value.length === 1) { 
                const next = document.getElementById(ids[i + 1]);
                if (next && document.activeElement.id === ids[i]) {
                    setTimeout(() => next.focus(), 0);
                }
            }
        }
        return null;
    }
    """,
    Output('output_div', 'children', allow_duplicate=True),
    Input({"index":"1_0","type":"wordle_letter"}, 'value'),
    Input({"index":"1_1","type":"wordle_letter"}, 'value'),
    Input({"index":"1_2","type":"wordle_letter"}, 'value'),
    Input({"index":"1_3","type":"wordle_letter"}, 'value'),
    Input({"index":"1_4","type":"wordle_letter"}, 'value'),        
)

app.clientside_callback(
    """
    function(v0, v1, v2, v3, v4) {

        v0 = JSON.stringify(v0, Object.keys(v0).sort());
        v1 = JSON.stringify(v1, Object.keys(v1).sort());
        v2 = JSON.stringify(v2, Object.keys(v2).sort());
        v3 = JSON.stringify(v3, Object.keys(v3).sort());
        v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
        let ids = ['{"index":"2_0","type":"wordle_letter"}','{"index":"2_1","type":"wordle_letter"}','{"index":"2_2","type":"wordle_letter"}','{"index":"2_3","type":"wordle_letter"}','{"index":"2_4","type":"wordle_letter"}' ];
        let values = [v0, v1, v2, v3, v4];
        for (let i = 0; i < values.length; i++) {

            this_value = values[i][1];
            
            if (this_value && this_value.length === 1) { 
                const next = document.getElementById(ids[i + 1]);
                if (next && document.activeElement.id === ids[i]) {
                    setTimeout(() => next.focus(), 0);
                }
            }
        }
        return null;
    }
    """,
    Output('output_div', 'children', allow_duplicate=True),
    Input({"index":"2_0","type":"wordle_letter"}, 'value'),
    Input({"index":"2_1","type":"wordle_letter"}, 'value'),
    Input({"index":"2_2","type":"wordle_letter"}, 'value'),
    Input({"index":"2_3","type":"wordle_letter"}, 'value'),
    Input({"index":"2_4","type":"wordle_letter"}, 'value'),        
)

app.clientside_callback(
    """
    function(v0, v1, v2, v3, v4) {

        v0 = JSON.stringify(v0, Object.keys(v0).sort());
        v1 = JSON.stringify(v1, Object.keys(v1).sort());
        v2 = JSON.stringify(v2, Object.keys(v2).sort());
        v3 = JSON.stringify(v3, Object.keys(v3).sort());
        v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
        let ids = ['{"index":"3_0","type":"wordle_letter"}','{"index":"3_1","type":"wordle_letter"}','{"index":"3_2","type":"wordle_letter"}','{"index":"3_3","type":"wordle_letter"}','{"index":"3_4","type":"wordle_letter"}' ];
        let values = [v0, v1, v2, v3, v4];
        for (let i = 0; i < values.length; i++) {

            this_value = values[i][1];
            
            if (this_value && this_value.length === 1) { 
                const next = document.getElementById(ids[i + 1]);
                if (next && document.activeElement.id === ids[i]) {
                    setTimeout(() => next.focus(), 0);
                }
            }
        }
        return null;
    }
    """,
    Output('output_div', 'children', allow_duplicate=True),
    Input({"index":"3_0","type":"wordle_letter"}, 'value'),
    Input({"index":"3_1","type":"wordle_letter"}, 'value'),
    Input({"index":"3_2","type":"wordle_letter"}, 'value'),
    Input({"index":"3_3","type":"wordle_letter"}, 'value'),
    Input({"index":"3_4","type":"wordle_letter"}, 'value'),        
)

app.clientside_callback(
    """
    function(v0, v1, v2, v3, v4) {

        v0 = JSON.stringify(v0, Object.keys(v0).sort());
        v1 = JSON.stringify(v1, Object.keys(v1).sort());
        v2 = JSON.stringify(v2, Object.keys(v2).sort());
        v3 = JSON.stringify(v3, Object.keys(v3).sort());
        v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
        let ids = ['{"index":"4_0","type":"wordle_letter"}','{"index":"4_1","type":"wordle_letter"}','{"index":"4_2","type":"wordle_letter"}','{"index":"4_3","type":"wordle_letter"}','{"index":"4_4","type":"wordle_letter"}' ];
        let values = [v0, v1, v2, v3, v4];
        for (let i = 0; i < values.length; i++) {

            this_value = values[i][1];
            
            if (this_value && this_value.length === 1) { 
                const next = document.getElementById(ids[i + 1]);
                if (next && document.activeElement.id === ids[i]) {
                    setTimeout(() => next.focus(), 0);
                }
            }
        }
        return null;
    }
    """,
    Output('output_div', 'children', allow_duplicate=True),
    Input({"index":"4_0","type":"wordle_letter"}, 'value'),
    Input({"index":"4_1","type":"wordle_letter"}, 'value'),
    Input({"index":"4_2","type":"wordle_letter"}, 'value'),
    Input({"index":"4_3","type":"wordle_letter"}, 'value'),
    Input({"index":"4_4","type":"wordle_letter"}, 'value'),        
)

app.clientside_callback(
    """
    function(v0, v1, v2, v3, v4) {

        v0 = JSON.stringify(v0, Object.keys(v0).sort());
        v1 = JSON.stringify(v1, Object.keys(v1).sort());
        v2 = JSON.stringify(v2, Object.keys(v2).sort());
        v3 = JSON.stringify(v3, Object.keys(v3).sort());
        v4 = JSON.stringify(v4, Object.keys(v4).sort());                        
        
        let ids = ['{"index":"5_0","type":"wordle_letter"}','{"index":"5_1","type":"wordle_letter"}','{"index":"5_2","type":"wordle_letter"}','{"index":"5_3","type":"wordle_letter"}','{"index":"5_4","type":"wordle_letter"}' ];
        let values = [v0, v1, v2, v3, v4];
        for (let i = 0; i < values.length; i++) {

            this_value = values[i][1];
            
            if (this_value && this_value.length === 1) { 
                const next = document.getElementById(ids[i + 1]);
                if (next && document.activeElement.id === ids[i]) {
                    setTimeout(() => next.focus(), 0);
                }
            }
        }
        return null;
    }
    """,
    Output('output_div', 'children', allow_duplicate=True),
    Input({"index":"5_0","type":"wordle_letter"}, 'value'),
    Input({"index":"5_1","type":"wordle_letter"}, 'value'),
    Input({"index":"5_2","type":"wordle_letter"}, 'value'),
    Input({"index":"5_3","type":"wordle_letter"}, 'value'),
    Input({"index":"5_4","type":"wordle_letter"}, 'value'),        
)