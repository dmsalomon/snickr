
import hashlib

from flask import Flask
from flask import flash, render_template, session, redirect, url_for

from flask_bootstrap import Bootstrap
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION

from forms import LoginForm, RegistrationForm
from nav import configure_nav

app = Flask(__name__)
Bootstrap(app)

try:
    app.config.from_object('config')
except:
    app.config.update(
        SECRET_KEY = 'notsecret',
    )

app.jinja_env.auto_reload = True

from flask import current_app
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Text

def basebar():
    return Navbar(
        current_app.config.get('SITE_NAME'),
        View('Home', 'index'),
        Text(f'Using Flask-Bootstrap {FLASK_BOOTSTRAP_VERSION}'),
    )

def ctxbar():
    bar = list(basebar().items)

    if not is_authenticated():
        bar.insert(1,
            View('Login', 'login'),
        )
    else:
        bar.insert(1,
            View('Logout', 'logout'),
        )

    return Navbar(current_app.config.get('SITE_NAME'), *bar)

def configure_nav(app):
    nav = Nav()
    nav.register_element('base', basebar)
    nav.register_element('ctx', ctxbar)
    nav.init_app(app)

configure_nav(app)

import pymysql
conn = pymysql.connect(host=app.config['DBHOST'],
                       user=app.config['DBUSER'],
                       password=app.config['DBPASS'],
                       db=app.config['DBNAME'],
                       cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html', form=LoginForm())

@app.route('/register')
def register():
    return render_template('register.html', form=RegistrationForm())

def is_authenticated():
    return 'uname' in session

@app.route('/login', methods=('POST',))
def loginAuth():
    form = LoginForm()
    if not form.validate_on_submit():
        return render('login.html', form=form)

    uname = form.uname.data
    password = form.password.data
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()

    q = """
        select nickname, email
        from user
        where uname = %s
        and password = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (uname, hashed))

    data = cursor.fetchone()

    if(data):
        session['uname'] = uname
        session['nickname'] = data['nickname']
        session['email'] = data['email']
        return redirect(url_for('index'))
    else:
        error = 'Invalid username or password.'
        flash(error, "danger")
        return redirect(url_for('login'))

@app.route('/register', methods=('POST',))
def registerAuth():
    form = RegistrationForm()
    if form.validate_on_submit():
        uname = form.uname.data
        email = form.email.data
        nick = form.nickname.data
        password = form.password.data
        hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()

        q = """
            insert into user(uname, nickname, email, password)
            values (%s, %s, %s, %s)
            """

        try:
            with conn.cursor() as cursor:
                cursor.execute(q, (uname, nick, email, hashed))
                conn.commit()
        except pymysql.err.IntegrityError:
            error = f'Username {uname} is already taken. Try another.'
            flash(error, "danger")
            return redirect(url_for('register'))

        return redirect(url_for('index'))

    # form error
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.pop('uname')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
