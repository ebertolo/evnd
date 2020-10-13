import os
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_fontawesome import FontAwesome
from flask import Flask
from flask_login import LoginManager


basedir = os.path.abspath(os.path.dirname(__file__))
#template_dir = os.path.abspath('/templates')

app = Flask(__name__)
app.config["SECRET_KEY"] = "endgame infinite-war age-of-ultron the-avengers"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

fa = FontAwesome(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)
db.create_all()

from app import views, forms