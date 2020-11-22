import os

# Configurações Gerais do Servidor
DEBUG = True

# Chave utilizada pela biblioteca de forms para proteger a aplicacao de ataques Cross Domain Reference ataques.
SECRET_KEY =  "endgame infinite-war age-of-ultron the-avengers"

# Parametros do SQLAlchemy ORM utilizado para acesso ao banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "data.sqlite")
SQLALCHEMY_COMMIT_ON_TEARDOWN = True 
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Parametros do Email
MAIL_HOSTNAME = "smtp.gmail.com"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORTER = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "evnd.unisul@gmail.com" #Email criado apenas para o projeto por isso foi mantido a senha no codigo
MAIL_PASSWORD = "%TGB6yhn"
