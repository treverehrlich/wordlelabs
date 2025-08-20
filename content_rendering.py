from dash import Input, Output, State, html, dcc
from dash_extensions import EventListener, Keyboard
from datetime import datetime
from functions import *
import json

import plotly.graph_objs as go
from plotly.subplots import make_subplots
import string

def render_main_layout():

    '''
    Initial/main skeleton of the page layout objects
    '''

    return html.Div(children=[

        Keyboard(id="key-listener"),
        dcc.Location(id="url"),  # triggers callback on load
        dcc.Store(id="my_words", storage_type="session"),
        dcc.Store(id="all_words", storage_type="session"),        
        dcc.Store(id="my_letters", storage_type="session"),        
        dcc.Store(id="enter_flag", storage_type="session"),                
        dcc.Store(id="backspace_flag", storage_type="session"),           
        dcc.Store(id="new_letter_flag", storage_type="session"),           
        dcc.Store(id="completed_word_index", storage_type="session"),           


        html.Div(
            children=[

                html.Div(children=[

                    html.Div(children=[
                        html.Img(src=f'assets/logo_smaller.png?v={str(datetime.now())}', className='logoStyle'),
                    ], className='logoStyleDiv'),

                    html.Div(children=[
                        html.Div(id='title', className='mainTitle',children="World's Best Wordle Solver"),
                        html.Div(className='mainTaglines',children="Use these tools to consistently make better guesses, and easily beat your friends! We LOVE Wordle!"),                    

                    ], className="mainTitleBox")                    

                ], className="mainHeaderBox"),

                html.Div([
                    html.Div(children="How to use: pick one of our suggested words, then enter Wordle's response below: type the letters, and tap for colors. Then we'll give you the next best word, and so on.", className="instructionLine"),
                    html.Div(children="Suggested best words:", id="suggestBest", className="suggestionsLine"),
                    html.Div(children="Bravest words (try if you dare!):", id="suggestWorst", className="suggestionsLine"),
                    ], id="instructionDiv"
                ),


                html.Div(children=grid_builder(), className='gridAreaContainer'),
                html.Div(children="", id="status_output"),
                
                keyboard_builder(),

                #dcc.Input(id='dummy_input', value='', autoFocus=True, style={'opacity': 50, 'position': 'absolute'}),



            ],
            className="col col1"

        ),

        html.Div(
            children=[
                html.Div([
                    html.Div(children="Words for You",className='colHeaderText'),
                    html.Div(children="Word count:",id='headerWordcount', className='colHeaderWordcount'),                                        
                    html.Div(children="Remaining words based on your guesses, sorted best to worst.",className='colSubtitleText'),
                ],   
                className='colHeader'),
                html.Div([], id='remainingWordsListScored' ,className='genericWordList'),

            ],
            className="col col2"

        ),

        # html.Div(
        #     children=[
        #         html.Div([
        #             html.Div(children="Unused Wordles",className='colHeaderText'),
        #             html.Div(children=f"Word Count: {len(unusedListRaw)}",className='colHeaderWordcount'),                      
        #             html.Div(children="Potential words for today's game, past Wordles removed.",className='colSubtitleText'),
        #         ],   
        #         className='colHeader'),
        #         unusedList,

        #     ],
        #     className="col col3"        

        # ),   

        html.Div(
            children=[

                html.Div(children="Letter Popularity",className='colHeaderText'),

                html.Div([
                    dcc.Graph(id='chart_distro', 
                            figure={
                                "data": [],
                                "layout": {
                                    "xaxis": {"visible": False},
                                    "yaxis": {"visible": False},
                                    "annotations": [],
                                    "paper_bgcolor": "rgba(0,0,0,0)",  # transparent background
                                    "plot_bgcolor": "rgba(0,0,0,0)",
                                },                                 
                            },
                          
                            config={"responsive": True, "staticPlot": True, "displaylogo": False}                            
                    )
                ], id='chart_distro_div'),

                html.Div(children="Letter Positions",className='colHeaderText'),

                html.Div([
                    dcc.Graph(id='chart_histro', 
                            figure={
                                "data": [],
                                "layout": {
                                    "xaxis": {"visible": False},
                                    "yaxis": {"visible": False},
                                    "annotations": [],
                                    "paper_bgcolor": "rgba(0,0,0,0)",  # transparent background
                                    "plot_bgcolor": "rgba(0,0,0,0)",
                                },                                  
                            },
                            config={"responsive": True, "staticPlot": True, "displaylogo": False}
                        )
                ], id='chart_histro_div'),

            ],
            className="col col3"

        ),                

        html.Div(
            children=[
                html.Div([
                    html.Div(children="Used Wordle Words",className='colHeaderText'),
                    html.Div(children=f"Word Count:",id="usedWordleCount", className='colHeaderWordcount'),                      
                    html.Div(children="This list is updated only after current day's game has ended.",className='colSubtitleText'),
                ],   
                className='colHeader'),
                html.Div(children=[],id='usedWordleList',className='genericWordList'),

            ],
            className="col col4"

        ),             

    ], className='flexContainer') 

def keyboard_builder():

    # QWERTY layout rows
    row1 = list("QWERTYUIOP")
    row2 = list("ASDFGHJKL")
    row3 = ["Backspace"] + list("ZXCVBNM") + ["Enter"]

    return html.Div(
                [
                    make_row(row1),
                    make_row(row2),
                    make_row(row3)
                ],
                className="keyboardContainer"
            )

def make_row(keys):

    return html.Div(
        [
            html.Button(
                "⌫" if key == "Backspace" else ("Enter" if key == "Enter" else key),
                id={"type": "key-btn", "index": key},
                n_clicks=0,
                className="keyboard-key special-key" if key in ["Backspace", "Enter"] else "keyboard-key"
            )
            for key in keys
        ],
        className="keyboard-row"
    )



def grid_builder():

    wordle_rows = []

    for row in range(6):
        wordle_rows.append(row_builder(row))
   
    return html.Div(id='wordle_grid', children=wordle_rows, className="wordleGridClassDiv") 

def row_builder(row):

    wordle_boxes = []

    for col in range(5):
        wordle_boxes.append(box_builder(row,col))
   
    return html.Div(id=f'wordle_row_{row}', children=wordle_boxes, className="wordleRowClassDiv")     


def box_builder(row,col):

    #autoFocusBoolean = False
    # autoFocusBoolean=True if (row == 0 and col == 0) else False
    #disabledBox=True if (row > 0) else False
    #disabledBox = True

    bgcolor = '#555' if row == 0 else '#333'

    return html.Div(
        id={"type" : "wordle_letter", "index" : f'{row}_{col}'}
        ,children=[]
        ,style={'backgroundColor' : bgcolor}
        ,className="wordleBoxClassDiv")


def format_list_of_words(thisList):

    wordListFormatted = []

    for word in thisList:
        wordListFormatted.append(html.Div(word, className="wordDivsInList"))

    return wordListFormatted
   
def format_list_of_words_scored(thisListDict):

    thisListDict = dict(sorted(thisListDict.items(), key=lambda item: item[1]['score'], reverse=True))

    format_row = []

    for key, value in thisListDict.items():
        format_row.append(html.Div(f'{key}',className="wordDivsInList"))
        #format_row.append(html.Div(f'{key} ({value['score']})',className="wordDivsInList"))

    # First 3 values
    first_three = list(thisListDict.keys())[:5]

    # Last 3 values
    last_three = list(thisListDict.keys())[-5:]

    return format_row, first_three, last_three

def distro_builder(occurrances):

    # Sort letters alphabetically
    letters = sorted(occurrances.keys())
    counts = [occurrances[letter] for letter in letters]

    # Create the bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=letters,
            y=counts,
            marker_color='lime'  # Optional: neon green bars
        )
    ])

    # Style the layout
    fig.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(title="", showgrid=False, showline=False, tickfont=dict(size=12)),
        yaxis=dict(title="", showgrid=False, showline=False, tickfont=dict(size=12)),
    )

    # Remove axis lines & ticks (optional for minimal style)
    fig.update_xaxes(showline=False, showticklabels=True, ticks='',tickfont=dict(color='white'))
    fig.update_yaxes(showline=False, showticklabels=False, ticks='',tickfont=dict(color='white'))

    # Show plot
    return fig

def histo_builder(weights):

    # Create 26 subplots (5 rows x 6 cols)
    fig = make_subplots(rows=4, cols=7, subplot_titles=list(string.ascii_uppercase))

    # Position tracker
    row, col = 1, 1

    for i, letter in enumerate(string.ascii_lowercase):

        if letter in weights:

        #     y_weights = [0,0,0,0,0] # in case that letter has been ruled out already
        # else:
            y_weights = weights[letter]

            # Create bar chart for current letter
            bar = go.Bar(
                x=[1, 2, 3, 4, 5],
                y=y_weights,
                showlegend=False
            )
            fig.add_trace(bar, row=row, col=col)

        # Advance to next subplot position
        col += 1
        if col > 7:
            col = 1
            row += 1

    # Layout tweaks
    fig.update_layout(
        #title_text="Letter Position Distribution",
        plot_bgcolor="black",       # Inside each chart
        paper_bgcolor="black",      # Outside the charts
        margin=dict(l=0, r=0, t=25, b=0),  # Remove outer whitespace        
    )

    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, title='',tickfont=dict(color='white'))
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, title='',tickfont=dict(color='white'))

    

    # Show plot
    return fig
