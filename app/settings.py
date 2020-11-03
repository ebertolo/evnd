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