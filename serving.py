import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import dash
import dash_bootstrap_components as dbc

#url_path = "/sensei/"

app = dash.Dash(
    __name__,
    meta_tags=[{
        'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.5, minimum-scale=0.7'
    }],
    # external_stylesheets=[dbc.themes.MINTY, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css'],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    title="Wordle Labs",
    update_title=None,
    #url_base_pathname=url_path,
    serve_locally=True
)

server = app.server