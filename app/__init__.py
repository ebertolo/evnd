#/usr/bin/python3
import os
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_fontawesome import FontAwesome
from flask import Flask
from flask_login import LoginManager
from flask_datepicker import datepicker 

# Inicializa aplicação flask e carrega as configurações do arquivo setting.py
app = Flask(__name__)
app.config.from_object('app.settings')

# Configura biblioteca de acesso
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = "Para acessar esta página favor logar no eVND."
login_manager.login_message_category = "info"
login_manager.init_app(app)

# Carrega e linka as bibliotecas auxiliares ao app principal

fa = FontAwesome(app)
bootstrap = Bootstrap(app)
datepicker(app)
moment = Moment(app)


# Carrega ORM para linkar classes python com as tabelas do banco, cria as tabelas caso não existam
db = SQLAlchemy(app, session_options={"autoflush": False})
db.create_all()

# Esse import deve ser o ultimo comando do arquivo para evitar referencia circular
from app import views, forms