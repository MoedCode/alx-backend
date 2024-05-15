#!/usr/bin/env python3
"""
First you will setup a basic bable Flask app
"""
from flask import (
    Flask, render_template, request
)
from flask_babel import Babel


class Config(object):
    """
    configure available languages in our appConfiguration for Babel
    """
    LANGUAGES = ["en", "fr"]
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object(Config)
babel = Babel(app)


@babel.localeselector
def get_locale():
    """ determine the best match with our supported languages """
    return request.accept_languages.best_match(app.config['LANGUAGES'])


@app.route('/', strict_slashes=False)
def index() -> str:
    """
    Define route for the home page
    """
    return render_template('3-index.html')


if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0', debug=True)
