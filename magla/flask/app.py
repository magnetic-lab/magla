
"""Magla Flask Server.

All Flask-related logic, as well as routes are centralized here.
"""
from os import environ

from flask import Flask, render_template
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField
# from wtforms.validators import DataRequired

import magla

APP = Flask(__name__)
APP.config["WTF_CSRF_ENABLED"] = False
CONFIG = magla.MaglaConfig(environ["MAGLA_CONFIG"])

## routes
@APP.route("/", methods=["GET", "POST"])
def index():
    """Serve server index with form and calculation result if present."""
    # form = MaglaServerForm()
    # data to be sent to UI
    data = {
        "ver": magla.__version__
        # "form": form
    }

    return render_template("index.html", data=data)


# class MaglaServerForm(FlaskForm):
#     """flask_wtf FlaskForm description."""
#     string_field = StringField("Enter a string:", validators=[DataRequired()])
#     submit = SubmitField("Submitz0rz.")

APP.run(host=CONFIG.get("server_host"), port=CONFIG.get("server_port"), debug=True)
