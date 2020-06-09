import os
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template, session, request, redirect, url_for, flash
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

# Models
class CustomerType(db.Model):
    __tablename__ = "customer_types"
    id = db.Column(db.Integer, primary_key=True)
    description_short = db.Column(db.String(10), unique=True)
    desciption_long = db.Column(db.String(50))
    customers = db.relationship("Customer", backref="customertype", lazy='dynamic')

    def __repr__(self):
        return "<CustomerType %r>" % self.name


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)
    contact_name =  db.Column(db.String(50))
    contact_phone =  db.Column(db.String(15))
    tax_id = db.Column(db.String(20), unique=True)
    customer_type_id = db.Column(db.Integer, db.ForeignKey("customer_types.id"))

    def __init__(self, name, contact_name, contact_phone):
        self.name = name
        self.contact_name = contact_name
        self.contact_phone = contact_phone

    def __repr__(self):
        return "<Customer %r>" % self.username

 
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
# Index
@app.route("/")
def index():
    all_data = Customer.query.all()
    return render_template("pages/index.html", page="Home", employees = all_data)

#Insert
@app.route('/insert', methods = ['POST'])
def insert():

    if request.method == 'POST':
        name = request.form['name']
        contact_name = request.form['contact_name']
        contact_phone = request.form['contact_phone']


        my_data = Customer(name, contact_name, contact_phone)
        db.session.add(my_data)
        db.session.commit()

        flash("Cliente cadastro com sucesso")
        return redirect(url_for('index'))

#Update
@app.route('/update', methods = ['GET', 'POST'])
def update():

    if request.method == 'POST':
        my_data = Customer.query.get(request.form.get('id'))
        my_data.name = request.form['name']
        my_data.contact_name = request.form['contact_name']
        my_data.contact_phone = request.form['contact_phone']
        db.session.commit()

        flash("Cliente atualizado com sucesso.")
        return redirect(url_for('index'))

#Delete
@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = Customer.query.get(id)
    db.session.delete(my_data)
    db.session.commit()

    flash("Employee Deleted Successfully")
    return redirect(url_for('index'))

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
