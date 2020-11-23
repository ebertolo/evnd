# eVND - Projeto de Conclusao de Curso
Tecnologias utilizadas:
- Flask
- Python 3
- SQLAlchemy
- Bootstrap
- Jquery

# Instruções para Instalar Localmente em Ambiente Linux (importante ter Python 3.6 ou superior instalado)
```
$ git clone https://github.com/ebertolo/evnd.git
$ pip3 install -r requeriments.txt

```
# Limpando a Base e Criando Usuario e Perfil Admin
Para limpar a base demo e fazer o primeiro acesso é necessário criar o Usuario Admin e os Perfis da Aplicação.
Acesse a pasta na qual rodou o comando clone do Git, ela conterá a pasta evnd, execute o shell do flask para ter acesso ao banco:
```
$ cd evnd
$ flask shell
```
Assim que iniciar o shell que será indicado com o seguinte prompt >>>, digite os comandos abaixo, exatamente nessa ordem:
```
>>> from app import db
>>> from app.models import User, Role
>>> db.drop_all()
>>> db.create_all()
>>> role_admin = Role("Admin")
>>> role_vendas = Role("Vendas")
>>> role_suporte = Role("Suporte")
>>> db.session.add(role_admin)
>>> db.session.commit()
>>> db.session.add(role_vendas)
>>> db.session.commit()
>>> db.session.add(role_suporte)
>>> db.session.commit()

```
Ainda no shell, crie o usuario admin, o login precisa ser um email válido e a senha precisa ter 6 caracteres pelo menos:
```
>>> u = User("login@email", "Admin" , "Nome Admin", "senha6", 1)
>>> db.session.add(u)
>>> db.session.commit()
>>> exit()

```
# Acessando a aplicação
Ainda na pasta evnd após sair do shell execute no prompt:
```
$ python3 run.py

```
Basta acessar http://localhost:5001
