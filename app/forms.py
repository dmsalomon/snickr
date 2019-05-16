
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, RadioField, SubmitField
from wtforms.validators import InputRequired, Length, Email, Regexp

class RegistrationForm(FlaskForm):
    uname = StringField('Username', [
        InputRequired(),
        Length(min=3, max=32),
        Regexp(r'^[^\W_]+$',
            message='Only alphanumeric characters allowed',
        )
    ])
    nickname = StringField('Nickname', [
        Length(min=3, max=32),
        Regexp(r'^[^\W\d_]+$',
            message='Only alphabetic characters allowed',
        )
    ])
    email = StringField('Email', [InputRequired(), Email()])
    password = PasswordField('Password', [
        InputRequired(),
        Length(min=4, max=32),
    ])

class LoginForm(FlaskForm):
    uname = StringField('Username', [
        InputRequired(),
        Length(min=3, max=32),
    ])
    password = PasswordField('Password', [
        InputRequired(),
        Length(min=4, max=32),
    ])

class WorkspaceForm(FlaskForm):
    wsname = StringField('Workspace', [
        InputRequired(),
        Length(min=3, max=32),
        Regexp(r'^[^\W_]+$',
            message='Only alphanumeric characters allowed',
        )
    ])
    description = StringField('Description', [
        Length(max=128)
    ])

class ChannelForm(FlaskForm):
    chname = StringField('Channel', [
        InputRequired(),
        Length(min=3, max=32),
        Regexp(r'^[^\W\d_]+$',
            message='Only alphabetic characters allowed',
        )
    ])
    chtype = RadioField('Channel Type', [
        InputRequired()
    ], choices=[
        ('public', 'public'),
        ('private', 'private'),
    ])

class WorkspaceInviteForm(FlaskForm):
    uname = StringField('Username', [
        InputRequired(),
        Length(min=3, max=32),
        Regexp(r'^[^\W_]+$',
            message='Only alphanumeric characters allowed',
        )
    ])
    submit = SubmitField('Submit', [
        InputRequired(),
    ])

class ChannelInviteForm(FlaskForm):
    uname = StringField('Username', [
        InputRequired(),
        Length(min=3, max=32),
        Regexp(r'^[^\W_]+$',
            message='Only alphanumeric characters allowed',
        )
    ])
    submit = SubmitField('Submit', [
        InputRequired(),
    ])
