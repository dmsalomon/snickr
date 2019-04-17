
from flask import Blueprint
from flask import url_for, redirect, session

backend = Blueprint('backend', __name__)

def is_authenticated():
    return 'uname' in session

@backend.route('/login')
def login():
    session['uname'] = True
    return redirect(url_for('frontend.index'))

@backend.route('/logout')
def logout():
    session.pop('uname')
    return redirect(url_for('frontend.index'))
