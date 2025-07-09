import dash
from serving import app, server
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from callback_manager import get_main_layout

app.layout = get_main_layout()

# For local development only. The app will
# get called via gunicorn on the Ec2.
if __name__ == '__main__':
    app.run(host="localhost", port="8051", debug=True, use_reloader=False)





