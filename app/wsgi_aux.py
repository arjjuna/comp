import os

from . import create_app

app = create_app(os.environ.get('FLASK_CONFIG', 'production'))