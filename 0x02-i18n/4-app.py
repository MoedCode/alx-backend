#!/usr/bin/env python3
"""A Basic Flask app with internationalization support.
"""
from flask import (
    Flask, render_template, request
)

from flask_babel import Babel


class Config:
    """configure available languages in our appConfiguration for Babel
    """
    LANGUAGES = ["en", "fr"]
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"


app = Flask(__name__)
app.config.from_object(Config)
app.url_map.strict_slashes = False
babel = Babel(app)


@babel.localeselector
def get_locale() -> str:
    """determine the best match with our supported languages
    """
    return request.accept_languages.best_match(app.config["LANGUAGES"])


@app.route('/')
def get_index() -> str:
    """Define route for the home page
    """
    return render_template('3-index.html')


if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0', debug=True)
