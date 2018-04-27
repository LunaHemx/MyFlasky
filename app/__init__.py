from flask import Flask,render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import FlaskForm
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager,UserMixin


app = Flask(__name__)
app.config['SECRET_KEY']='hard to guess string'
bootstrap=Bootstrap(app)
db=SQLAlchemy(app)
db.init_app(app)
login_manager=LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='auth.login'



def create_app(config_name):
    login_manager.init_app(app)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    return app



