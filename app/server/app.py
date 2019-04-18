
from functools import wraps

from flask import Flask
from flask import flash, render_template, session, redirect, url_for, jsonify

from flask_bootstrap import Bootstrap
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_cors import CORS

from forms import LoginForm, RegistrationForm
from nav import configure_nav

app = Flask(
    __name__,
    template_folder="../static/templates",
    static_folder="../static/dist",
)
Bootstrap(app)
CORS(app)

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
    if not is_authenticated():
        return redirect(url_for('login'))

    uname = session['uname']

    q = """
        select wsname
        from wsmember
        where uname = %s
        """

    ws = []
    with conn.cursor() as cursor:
        cursor.execute(q, (uname,))
        for row in cursor.fetchall():
            ws.append(row['wsname'])

    if len(ws) == 1:
        return redirect('/' + ws[0])

    return "<br />".join(ws)

@app.route('/login')
def login():
    return render_template('login.html', form=LoginForm())

@app.route('/register')
def register():
    return render_template('register.html', form=RegistrationForm())

def is_authenticated():
    return 'uname' in session

def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not is_authenticated():
            return redirect(url_for('login'))
        return f(*a, **kw)
    return dec

@app.route('/login', methods=('POST',))
def loginAuth():
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('login.html', form=form)

    uname = form.uname.data
    password = form.password.data
    # hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()

    q = """
        select nickname, email
        from user
        where uname = %s
        and password = sha2(%s, 256)
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (uname, password))
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
    if not form.validate_on_submit():
        return render_template('register.html', form=form)

    uname = form.uname.data
    email = form.email.data
    nick = form.nickname.data
    password = form.password.data
    # hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()

    q = """
        insert into user(uname, nickname, email, password)
        values (%s, %s, %s, sha2(%s, 256))
        """

    try:
        with conn.cursor() as cursor:
            cursor.execute(q, (uname, nick, email, password))
            conn.commit()
    except pymysql.err.IntegrityError:
        error = f'Username {uname} is already taken. Try another.'
        flash(error, "danger")
        return redirect(url_for('register'))

    return redirect(url_for('index'))

def workspace_auth(uname, wsname):
    q = """
        select *
        from wsmember
        where uname = %s
        and wsname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (uname,wsname))
        data = cursor.fetchone()

    return bool(data)

@app.route('/<wsname>')
@login_required
def workspace(wsname):
    uname = session['uname']

    if not workspace_auth(uname, wsname):
        return "unauthorized"
    return "authorized"

def channel_auth(uname, wsname, chname):
    if not workspace_auth(uname, wsname):
        return False

    q = """
        select *
        from chmember
        where member = %s
        and wsname = %s
        and chname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (uname,wsname,chname))
        data = cursor.fetchone()

    return bool(data)

@app.route('/<wsname>/<chname>')
@login_required
def channel(wsname, chname):
    uname = session['uname']

    if not channel_auth(uname, wsname, chname):
        return "unauthorized"

    q = """
        select msgid, sender, content, posted
        from message
        where wsname = %s
        and chname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (wsname, chname))
        data = cursor.fetchall()

    h = "<table>"
    for row in data:
        h += f"<tr>"
        h += f"<td>{row['sender']}</td>"
        h += f"<td>{row['content']}</td>"
        h += f"<td>{row['posted']}</td>"
        h += "</tr>"
    h += "</table>"

    return render_template('channel.html')
    return f"<html><body>{h}</body></html>"

@app.route('/<wsname>/<chname>/<int:page>')
@login_required
def messages(wsname, chname, page):
    uname = session['uname']

    if not channel_auth(uname, wsname, chname):
        return "unauthorized"

    q = """
        select msgid, sender, content, posted
        from message
        where wsname = %s
        and chname = %s
        limit %s, %s
        """

    per = 20
    offset = page * per

    with conn.cursor() as cursor:
        conn.commit()
        cursor.execute(q, (wsname, chname, offset, per))
        data = cursor.fetchall()

    return jsonify(messages=data)

@app.route('/logout')
@login_required
def logout():
    session.pop('uname')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
