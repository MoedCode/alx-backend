#!/usr/bin/env python3
"""A Basic Flask app with internationalization support.
"""
from flask import (
    Flask, render_template,
    request, g
)

from flask_babel import Babel


class Config(object):
    """configure available languages in our appConfiguration for Babel
    """
    LANGUAGES = ["en", "fr"]
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"


users = {
    1: {"name": "Balou", "locale": "fr", "timezone": "Europe/Paris"},
    2: {"name": "Beyonce", "locale": "en", "timezone": "US/Central"},
    3: {"name": "Spock", "locale": "kg", "timezone": "Vulcan"},
    4: {"name": "Teletubby", "locale": None, "timezone": "Europe/London"},
}

app = Flask(__name__)
app.config.from_object(Config)
# app.url_map.strict_slashes = False
babel = Babel(app)


@babel.localeselector
def get_locale() -> str:
    """determine the best match with our supported languages
    """
    loca = request.args.get('locale')
    if loca in app.config['LANGUAGES']:
        return loca
    return request.accept_languages.best_match(app.config['LANGUAGES'])


def get_user():
    """
    Returns a user dictionary or None if ID value can't be found
    or if 'login_as' URL parameter was not found
    """
    id = request.args.get('login_as', None)
    if id is not None and int(id) in users.keys():
        return users.get(int(id))
    return None


@app.before_request
def before_request():
    """
    Add user to flask.g if user is found
    """
    user = get_user()
    g.user = user


@app.route('/')
def get_index() -> str:
    """Define route for the home page
    """
    return render_template('5-index.html')


if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0', debug=True)
