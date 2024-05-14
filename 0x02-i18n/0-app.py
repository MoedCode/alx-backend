#!/usr/bin/env python3

"""First you will setup a basic bable Flask app """

from flask import Flask, render_template
from flask_babel import Babel

app = Flask(__name__)
bable = Babel(app)


@app.route('/',  strict_slashes=False)
def index() -> str:
    """ Define route for the home page"""
    return render_template("0-index.html")


if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0', debug=True)
