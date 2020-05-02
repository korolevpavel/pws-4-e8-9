from flask_wtf import FlaskForm
from wtforms import StringField


class MainForm(FlaskForm):
    address = StringField('address')
