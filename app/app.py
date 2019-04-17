
from flask import Flask
from flask_bootstrap import Bootstrap

from frontend import frontend
from backend import backend
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
app.register_blueprint(frontend)
app.register_blueprint(backend)
configure_nav(app)

if __name__ == '__main__':
    app.run(debug=True)
