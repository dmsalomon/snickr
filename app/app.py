
from functools import wraps

from flask import Flask
from flask import flash, render_template, session, redirect, url_for, jsonify, request, make_response

from flask_bootstrap import Bootstrap
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit, disconnect, join_room, leave_room

from forms import LoginForm, RegistrationForm
from nav import configure_nav

import json
import random

app = Flask(
    __name__,
    template_folder="static/templates",
    static_folder="static/dist",
)

try:
    app.config.from_object('config')
except:
    app.config.update(
        SECRET_KEY = 'notsecret',
    )

app.jinja_env.auto_reload = True
Bootstrap(app)
CORS(app)
socket = SocketIO(app)

from flask import current_app
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Text, Link, Subgroup

def ctxbar():
    bar = []

    if not is_authenticated():
        bar.append(View('Login', 'login'))
    else:
        uname = session['uname']
        links = []
        for w in workspaces(uname):
            links.append(Link(w, f'/{w}'))
        bar.append(Subgroup('Workspaces', *links))

        if 'wsname' in session:
            links = []
            wsname = session['wsname']
            for c in channels(uname, wsname):
                links.append(Link(c, f'/{wsname}/{c}'))
            bar.append(Subgroup(w, *links))

        bar.append(View('Logout', 'logout'))

    return Navbar(current_app.config.get('SITE_NAME'), *bar)

def configure_nav(app):
    nav = Nav()
    nav.register_element('ctx', ctxbar)
    nav.init_app(app)

configure_nav(app)

import pymysql
conn = pymysql.connect(host=app.config['DBHOST'],
                       user=app.config['DBUSER'],
                       password=app.config['DBPASS'],
                       db=app.config['DBNAME'],
                       cursorclass=pymysql.cursors.DictCursor)

def is_authenticated():
    return 'uname' in session

def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not is_authenticated():
            return redirect(url_for('login'))
        return f(*a, **kw)
    return dec

def workspaces(uname):
    q = """
        select wsname
        from wsmember
        where uname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (uname,))
        for row in cursor.fetchall():
            yield row['wsname']


def channels(uname, wsname):
    q = """
        select chname
        from chmember
        where member = %s
        and wsname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (uname, wsname,))
        for row in cursor.fetchall():
            yield row['chname']

@app.route('/')
@login_required
def index():
    uname = session['uname']
    ws = list(workspaces(uname))

    if len(ws) == 0:
        return "no workspaces"

    ws = random.choice(ws)

    return redirect('/' + ws)

@app.route('/login')
def login():
    return render_template('login.html', form=LoginForm())

@app.route('/register')
def register():
    return render_template('register.html', form=RegistrationForm())

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

    if data:
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

    session['wsname'] = wsname

    cs = list(channels(uname, wsname))

    if len(cs) == 0:
        return "you are in no channels"

    c = random.choice(cs)
    return redirect(f'/{wsname}/{c}')

def channel_auth(uname, wsname, chname):
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
    print('logged in:', uname)

    if not channel_auth(uname, wsname, chname):
        return "unauthorized"

    session['wsname'] = wsname
    session['chname'] = chname

    q = """
        select msgid, sender, content, posted
        from message
        where wsname = %s
        and chname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (wsname, chname))
        data = cursor.fetchall()

    resp = make_response(render_template('channel.html'))
    resp.set_cookie('uname', uname)
    resp.set_cookie('wsname', wsname)
    resp.set_cookie('chname', chname)
    return resp

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))

def socket_login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not is_authenticated():
            disconnect()
        return f(*a, **kw)
    return dec

@socket.on('connect')
def on_connection():
    pass

@socket.on('join')
def on_join(room):
    join_room(room)

@socket.on('leave')
def on_leave(room):
    leave_room(room)

@socket.on('disconnect')
def on_disconnect():
    print('disconnect')

@socket.on('get msg')
def get_msg(wsname, chname, page):
    q = """
        select msgid, sender, content, posted
        from message
        where wsname = %s
        and chname = %s
        order by posted
        limit %s, %s
        """

    per = 20
    offset = page * per

    with conn.cursor() as cursor:
        conn.commit()
        cursor.execute(q, (wsname, chname, offset, per))
        data = cursor.fetchall()

    return jsonify(data).get_json()

@socket.on('post msg')
def post_msg(msg):
    uname = msg['sender']
    wsname = msg['wsname']
    chname = msg['chname']
    content = msg['content']

    q = """
        insert into message(wsname, chname, sender, content)
        values (%s, %s, %s, %s)
        """

    try:
        with conn.cursor() as cursor:
            cursor.execute(q, (wsname, chname, uname, content))
            conn.commit()
    except pymysql.err.IntegrityError:
        return "error"

    q = """
        select last_insert_id() as id
        """

    try:
        with conn.cursor() as cursor:
            cursor.execute(q)
            data = cursor.fetchone()
    except:
        return "error"

    msg['msgid'] = data['id']

    room = f'{wsname}:{chname}'
    emit('new msg', jsonify(msg).get_json(), room=room)

@app.route('/this')
def this():
    socket.emit('new msg', jsonify({
        "content": "new message",
        "sender": "webapp",
        "msgid": 100,
    }).get_json())
    return "f"

if __name__ == '__main__':
    socket.run(app, debug=True)
