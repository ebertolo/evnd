import os
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config["SECRET_KEY"] = "endgame infinite-war age-of-ultron the-avengers"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)



# Forms
class CustomerForm(FlaskForm):
    name = StringField("Digite seu nome:", validators=[DataRequired()])
    contact_name = StringField("Nome de Contato:", validators=[DataRequired()])
    contact_phone = StringField("Telefone Contato:", validators=[DataRequired()])
    tax_id = StringField("CNPJ:", validators=[DataRequired()])
    submit = SubmitField("Enviar")

class CustomerTypeForm(FlaskForm):
    description_short = StringField("Tipo Cliente:", validators=[DataRequired()])
    desciption_long = StringField("Descrição Longa:", validators=[DataRequired()])
    submit = SubmitField("Enviar")


# Rotinas Principais
@app.route("/")
def index():
    return render_template("pages/index.html", page="Home")

@app.route("/product/<name>")
def product(name):
    return render_template("pages/home.html", page=name, items=["arroz", "feijao", "farinha" , "teste"])

@app.route("/customer", methods=["GET", "POST"])
def customer():
    form = CustomerForm()

    if form.validate_on_submit():
        customer = Customer.query.filter_by(name=form.name.data).first()
        if customer is None:
            customer = Customer(name = form.name.data)
            db.session.add(customer)
            session['known'] = False
            flash("Cliente cadastrado com sucesso")
        else:   
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('customer')) 
          
    return render_template("pages/customer.html", form=form, page="Clientes", 
    name = session.get('name'), known = session.get('known', False))

@app.route("/customer-type", methods=["GET", "POST"])
def customer_type():
    form = CustomerTypeForm()

    if form.validate_on_submit():
        customerType = Customer.query.filter_by(name=form.name.data).first()
        if customerType is None:
            customerType = CustomerType(description_short = form.description_short.data)
            db.session.add(customerType)
            session['known'] = False
            flash("Tipo de Cliente cadastrado com sucesso")
        else:    
            session['known'] = True
        form.name.data = ''
        return redirect(url_for('customer-type'))

    return render_template("pages/customer-type.html", form=form, page="Tipo Cliente", 
    dknown = session.get('known', False))


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
