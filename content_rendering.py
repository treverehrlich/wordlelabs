from dash import Input, Output, State, html, dcc
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

        dcc.Location(id="url"),  # triggers callback on load
        dcc.Store(id="my_words", storage_type="session"),

        html.Div(
            children=[

                html.Div(children=[

                    html.Div(children=[
                        html.Img(src=f'assets/logo_smaller.png?v={str(datetime.now())}', className='logoStyle'),
                    ], className='logoStyleDiv'),

                    html.Div(children=[
                        html.Div(id='title', className='mainTitle',children="World's Best Wordle Solver"),
                        html.Div(className='mainTaglines',children="Addicted to Wordle like us?"),
                        html.Div(className='mainTaglines',children="Consistently make better guesses!"),
                        html.Div(className='mainTaglines',children="Easily beat your friends!"),                    

                    ], className="mainTitleBox")                    

                ], className="mainHeaderBox"),

                html.Div([
                    html.Div(children="Suggested best word:", id="suggestBest", className="instructionLine"),
                    html.Div(children="Suggested worst word:", id="suggestWorst", className="instructionLine"),
                    ], id="instructionDiv"
                ),


                html.Div(children=grid_builder()
                , className='gridAreaContainer'),

                html.Div(children="", id="output_div"),


            ],
            className="col col1"

        ),

        html.Div(
            children=[
                html.Div([
                    html.Div(children="Words for You",className='colHeaderText'),
                    html.Div(children="Word count:",id='headerWordcount', className='colHeaderWordcount'),                                        
                    html.Div(children="Potential remaining words based on your guesses.",className='colSubtitleText'),
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
                          
                            config={'responsive': True})
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
                        config={'responsive': True})
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

    autoFocusBoolean=True if (row == 0 and col == 0) else False
    disabledBox=True if (row > 0) else False

    bgcolor = '#555' if row == 0 else '#333'

    return html.Div(id={"type" : "wordle_letter_div", "index" : f'{row}_{col}'}, children=[
        dcc.Input(
                id={"type" : "wordle_letter", "index" : f'{row}_{col}'},
                type='text',
                value='',
                autoFocus=autoFocusBoolean,
                autoComplete="off",
                maxLength=1,
                disabled=disabledBox,
                className="wordleBoxClass",
                style={'backgroundColor' : bgcolor}
            ),
    ], className="wordleBoxClassDiv")


def format_list_of_words(thisList):

    wordListFormatted = []

    for word in thisList:
        wordListFormatted.append(html.Div(word))

    return wordListFormatted
   
def format_list_of_words_scored(thisListDict):

    thisListDict = dict(sorted(thisListDict.items(), key=lambda item: item[1]['score'], reverse=True))

    format_row = []

    for key, value in thisListDict.items():
        format_row.append(html.Div(f'{key} ({value['score']})',className="wordDivsInList"))

    return format_row

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
