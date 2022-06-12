from flask import Flask
from .views import views
from .config import *


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_key

    app.register_blueprint(views, url_prefix='/')

    return app
