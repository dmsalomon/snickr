
from functools import wraps

from flask import Flask
from flask import flash, render_template, session, redirect, url_for, jsonify, request, make_response

from flask_bootstrap import Bootstrap
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit, disconnect, join_room, leave_room

from forms import *
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
        wx = workspaces(uname)
        if wx:
            for w in wx:
                w = w['wsname']
                links.append(Link(w, f'/{w}'))
            bar.append(Subgroup('Workspaces', *links))

        if 'wsname' in session:
            links = []
            wsname = session['wsname']
            cx = channels(uname, wsname)
            for c in cx:
                c = c['chname']
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
        select *
        from wsmember natural join workspace
        where uname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (uname,))
        return cursor.fetchall()

def channels(uname, wsname):
    # get all public channels in the workspace
    # as well as private channels that this
    # user is a member of
    q = """
        select distinct
        C.wsname, C.chname, C.owner, C.chtype, C.chcreated
        from chmember M, channel C
        where C.wsname = %s and (
            C.chtype = 'public' or (
                M.wsname = C.wsname and
                M.chname = C.chname and
                M.member = %s and
                C.chtype = 'private'
            )
        )
    """

    with conn.cursor() as cursor:
        cursor.execute(q, (wsname,uname))
        return cursor.fetchall()

@app.route('/', methods=('GET', 'POST'))
@login_required
def index():
    uname = session['uname']
    wsx = workspaces(uname)
    form = WorkspaceForm()

    if request.method == 'GET' or not form.validate_on_submit():
        return render_template('home.html', wsx=wsx, form=form)

    wsname = form.wsname.data
    desc = form.description.data

    q1 = """
        insert into workspace(wsname, description)
        values (%s, %s)
        """

    q2 = """
        insert into wsmember(wsname, uname, admin)
        values (%s, %s, true)
        """

    try:
        with conn.cursor() as cursor:
            cursor.execute(q1, (wsname, desc))
            cursor.execute(q2, (wsname, uname))
            conn.commit()
    except pymysql.err.IntegrityError:
        error = f'Workspace {wsname} is already taken. Try another.'
        flash(error, "danger")
        conn.rollback()

    return redirect(url_for('index'))

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
        conn.rollback()
        return redirect(url_for('register'))

    return redirect(url_for('index'))

def workspace_auth(uname, wsname):

    return bool(data)

@app.route('/<channel>/invite', methods=('GET', 'POST'))
@login_required
def chmember():
    form = ChannelUserForm()

    if request.method == 'GET' or not form.validate_on_submit():
        return render_template('chmember.html', form=form)

    uname = session['uname']

    wsname = form.wsname.data
    chname = form.chname.data
    user = form.uname.data

    q = """
        select chtype
        from channel
        where wsname = %s
        and chname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (wsname, chname))
        data = cursor.fetchone()

    if chname.startswith('_') or not data:
        err = f"No such channel {chname} in {wsname}"
        flash(err, "danger")
        return redirect(url_for('chmember'))

    chtype = data['chtype']

    if chtype == 'private':
        q = """
            select *
            from chmember
            where wsname = %s
            and chname = %s
            and member = %s
            """
        with conn.cursor() as cursor:
            cursor.execute(q, (wsname, chname, uname))
            data = cursor.fetchone()
    else:
        q = """
            select *
            from wsmember
            where wsname = %s
            and uname = %s
            """
        with conn.cursor() as cursor:
            cursor.execute(q, (wsname, uname))
            data = cursor.fetchone()

    if not data:
        err = f"You cannot add members to channel {chname}"
        flash(err, "danger")
        return redirect(url_for('chmember'))

    q = """
        select *
        from user
        where uname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (user))
        data = cursor.fetchone()

    if not data:
        err = f"No such user {user}"
        flash(err, "danger")
        return redirect(url_for('chmember'))

    q = """
        select *
        from chmember
        where member = %s
        and wsname = %s
        and chname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (user, wsname, chname))
        data = cursor.fetchone()

    if data:
        err = f"User {user} is already a member of {chname}"
        flash(err, "warning")
        return redirect(url_for('chmember'))

    q = """
        insert into chmember (wsname, chname, member)
        values (%s, %s, %s)
        """

    try:
        with conn.cursor() as cursor:
            cursor.execute(q, (wsname, chname, user))
            conn.commit()
            msg = f"{user} added to {chname}!", "success"
    except:
        msg = f"Could not add {user} to {chname}", "danger"
        conn.rollback()

    flash(*msg)
    return redirect(url_for('chmember'))

@app.route('/<wsname>/invite', methods=('GET', 'POST'))
@login_required
def wsinvite(wsname):
    uname = session['uname']
    form = WorkspaceInviteForm()

    q = """
        select admin
        from wsmember
        where wsname = %s
        and uname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (wsname, uname))
        data = cursor.fetchone()
        if not data or not data['admin']:
            return "unauthorized"

    if request.method == 'GET' or not form.validate_on_submit():
        return render_template('wsinvite.html', ws=wsname, form=form)

    invitee = form.uname.data

    q1 = """
        select *
        from wsmember
        where wsname = %s
        and uname = %s
        """

    q2 = """
        insert into wsinvitation(wsname, invitee, inviter)
        values (%s, %s, %s)
        """

    err = None

    try:
        with conn.cursor() as cursor:
            cursor.execute(q1, (wsname, invitee))
            if cursor.fetchone():
                err = f'{invitee} is already a member of {wsname}'
                raise Exception
            cursor.execute(q2, (wsname, invitee, uname))
            conn.commit()
        flash("nice!!", "success")
    except:
        conn.rollback()
        err = err or f'could not invitee {invitee} to {wsname}'
        flash(err, "danger")

    return redirect('/' + wsname + '/invite')

@app.route('/<wsname>', methods=('GET', 'POST'))
@login_required
def workspace(wsname):
    uname = session['uname']

    q = """
        select admin
        from wsmember
        where uname = %s
        and wsname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (uname,wsname))
        data = cursor.fetchone()

    if not data:
        return "unauthorized"

    session['wsname'] = wsname
    session['admin'] = data['admin']

    cs = channels(uname, wsname)

    q = """
        select uname, admin
        from wsmember
        where wsname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (wsname))
        ux = cursor.fetchall()

    form = ChannelForm()

    if request.method == 'GET' or not form.validate_on_submit():
        return render_template('workspace.html', cs=cs, us=ux, u=session, form=form)

    chname = form.chname.data
    chtype = form.chtype.data

    print("probe")

    q1 = """
        insert into channel(wsname, chname, owner, chtype)
        values (%s, %s, %s, %s)
        """

    q2 = """
        insert into chmember(wsname, chname, member)
        values (%s, %s, %s)
        """

    try:
        with conn.cursor() as cursor:
            cursor.execute(q1, (wsname, chname, uname, chtype))
            cursor.execute(q2, (wsname, chname, uname))
            conn.commit()
    except pymysql.err.IntegrityError:
        error = f'Channel {chname} is already taken. Try another.'
        flash(error, "danger")
        conn.rollback()

    return redirect('/' + wsname)

def channel_auth(uname, wsname, chname):
    q1 = """
        select *
        from chmember
        where wsname = %s
        and chname = %s
        and member = %s
        """

    q2 = """
        select chtype
        from channel
        where wsname = %s
        and chname = %s
        """

    q3 = """
        insert into chmember(wsname, chname, member)
        values (%s, %s, %s)
        """

    try:
        with conn.cursor() as cursor:
            cursor.execute(q1, (wsname,chname,uname))
            if cursor.fetchone():
                return True
            cursor.execute(q2, (wsname,chname))
            data = cursor.fetchone()
            if data and data['chtype'] == 'public':
                cursor.execute(q3, (wsname,chname,uname))
                conn.commit()
                return True
    except:
        return False

    return False

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

@app.route('/<wsname>/direct/<peer>')
@login_required
def direct(wsname, peer):
    uname = session['uname']

    a, b = min(uname, peer), max(uname, peer)
    chname = f'_{a}_{b}'

    q = """
        select *
        from channel
        where chname = %s
        and wsname = %s
        """

    with conn.cursor() as cursor:
        cursor.execute(q, (chname, wsname))
        data = cursor.fetchone()

    if not data:
        q = """
            insert into channel(wsname, chname, owner, chtype)
            values (%s, %s, %s, %s)
            """
        q1 = """
            insert into chmember(wsname, chname, member)
            values (%s, %s, %s)
            """
        with conn.cursor() as cursor:
            cursor.execute(q, (wsname, chname, uname, 'direct'))
            cursor.execute(q1, (wsname, chname, uname))
            if a != b:
                cursor.execute(q1, (wsname, chname, peer))
            conn.commit()

    session['wsname'] = wsname
    session['chname'] = chname

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
    print("connect")

@socket.on('join')
def on_join(room):
    print("join", room)
    join_room(room)

@socket.on('leave')
def on_leave(room):
    print("leave", room)
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

    print("post msg")

    q = """
        insert into message(wsname, chname, sender, content)
        values (%s, %s, %s, %s)
        """

    try:
        with conn.cursor() as cursor:
            cursor.execute(q, (wsname, chname, uname, content))
            conn.commit()
    except pymysql.err.IntegrityError:
        conn.rollback()
        print("how?")
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
    socket.run(app, host='0.0.0.0', debug=True)
