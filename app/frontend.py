
from flask import Blueprint
from flask import render_template

from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator

from backend import backend

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def index():
    return render_template('index.html')
