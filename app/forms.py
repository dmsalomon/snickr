
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, Regexp

class RegistrationForm(FlaskForm):
    uname = StringField(
        'Username',
        [InputRequired(), Length(min=3, max=32)]
    )
    nickname = StringField(
        'Nickname',
        [Regexp(r'[a-zA-Z]+',
            message='Only alphabetic characters allowed')]
    )
    email = StringField('Email', [InputRequired(), Email()])
    password = PasswordField('Password', [InputRequired(), Length(min=4, max=32)])

class LoginForm(FlaskForm):
    uname = StringField('Username', [InputRequired(), Length(min=3, max=32)])
    password = PasswordField('Password', [InputRequired(), Length(min=4, max=32)])
