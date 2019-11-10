from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_moment import Moment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'endgame infinite-war age-of-ultron the-avengers'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Rotinas Principais
@app.route("/")
def index():
    return render_template("pages/index.html", page="Home")

@app.route("/product/<name>")
def product(name):
    return render_template("pages/home.html", page=name, items=["arroz", "feijao", "farinha" , "teste"])

@app.route("/customer/<id>", methods=["GET", "POST"])
def customer(id):
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template("pages/customer.html", form=form, page="Clientes", id=id)



# Paginas de Erros customizados
@app.errorhandler(404)
def page_not_found(e):
    return render_template("exceptions/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("exceptions/500.html"), 500


# Permite execucao via script
if __name__ == "__main__":
    app.run(host="0.0.0.0")
