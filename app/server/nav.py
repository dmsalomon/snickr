
from flask import current_app
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Text
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION

def basebar():
    return Navbar(
        current_app.config.get('SITE_NAME'),
        View('Home', '.index'),
        Text(f'Using Flask-Bootstrap {FLASK_BOOTSTRAP_VERSION}'),
    )

def ctxbar():
    bar = list(basebar().items)

    if not is_authenticated():
        bar.insert(1,
            View('Login', '.login'),
        )
    else:
        bar.insert(1,
            View('Logout', 'backend.logout'),
        )

    return Navbar(current_app.config.get('SITE_NAME'), *bar)

def configure_nav(app):
    nav = Nav()
    nav.register_element('base', basebar)
    nav.register_element('ctx', ctxbar)
    nav.init_app(app)
