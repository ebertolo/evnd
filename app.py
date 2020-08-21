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
# TODO: A SER IMPLEMENTADO NO FUTURO
#class CustomerType(db.Model):
#    __tablename__ = "customer_types"
#    id = db.Column(db.Integer, primary_key=True)
#    description_short = db.Column(db.String(10), unique=True)
#    desciption_long = db.Column(db.String(50))
#    customers = db.relationship("Customer", backref="customertype", lazy='dynamic')
#
#    def __repr__(self):
#        return "<CustomerType %r>" % self.name


class Customer(db.Model):
    """ Model Cliente """

    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(15))
    contact_email = db.Column(db.String(100), unique=True)
    tax_id = db.Column(db.String(20), unique=True)
    customer_type_id = db.Column(db.Integer) # A ser substituido com uma chave extrangeira no futuro

    def __init__(self, name, tax_id, contact_name, contact_phone, contact_email, customer_type_id):
        self.name = name
        self.tax_id = tax_id # CNPJ Do Cliente
        self.contact_name = contact_name
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.customer_type_id = customer_type_id

    def __repr__(self):
        return "<Customer %r>" % self.name

class Product(db.Model):
    """ Model Produto """

    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    info = db.Column(db.String(500))
    html_link = db.Column(db.String(250))
    product_group_name_short = db.Column(db.String(20))
    product_group_name_long = db.Column(db.String(100))

    def __init__(self, name, info, html_link, product_group_name_short, product_group_name_long):
        self.name = name
        self.info = info
        self.html_link = html_link
        self.product_group_name_short = product_group_name_short
        self.product_group_name_long = product_group_name_long

    def __repr__(self):
        return "<Product %r>" % self.name

class SalesPerson(db.Model):
    """ Model Equipe de Venda """

    __tablename__ = "sales_person"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True)

    def __init__(self, name, phone, email):
        self.name = name
        self.phone = phone 
        self.email = email

    def __repr__(self):
        return "<SalesPerson %r>" % self.name

class Activity(db.Model):
    """ Model Ativdidades"""

    __tablename__ = "activity"
    id = db.Column(db.Integer, primary_key=True)
    id_status = db.Column(db.Integer)
    id_activity_type = db.Column(db.String(50), unique=True)
    id_customer = db.Column(db.Integer)
    id_sales_person = db.Column(db.Integer)
    id_product = db.Column(db.Integer)
    activity_date = db.Column(db.DateTime)
    description = db.Column(db.String(500))

    def __init__(self, id_status, id_activity_type, id_customer, id_sales_person, id_product, activity_date, description ):
        self.id_status = id_status
        self.id_activity_type = id_activity_type
        self.id_customer = id_customer
        self.id_sales_person = id_sales_person
        self.id_product = id_product 
        self.activity_date = activity_date
        self.description = description

    def __repr__(self):
        return "<Activity %r>" % self.name

################################# Rotas Clientes #################################
#Clientes
@app.route("/customers")
def customers_index():
    customer_set = Customer.query.all()
    return render_template("pages/customers.html", page="Clientes", customers = customer_set)

#Insert
@app.route('/customers/insert', methods = ['POST'])
def customers_insert():

    if request.method == 'POST':
        name = request.form['name']
        tax_id = request.form['tax_id']
        contact_name = request.form['contact_name']
        contact_phone = request.form['contact_phone']
        contact_email = request.form['contact_email']
        customer_type_id = request.form['customer_type_id']


        my_data = Customer(name, tax_id, contact_name, contact_phone, contact_email, customer_type_id)
        db.session.add(my_data)
        db.session.commit()

        flash("Cliente cadastro com sucesso")
        return redirect(url_for('customers_index'))

#Update
@app.route('/customers/update', methods = ['GET', 'POST'])
def customers_update():

    if request.method == 'POST':
        my_data = Customer.query.get(request.form.get('id'))
        my_data.name = request.form['name']
        my_data.tax_id = request.form['tax_id']
        my_data.contact_name = request.form['contact_name']
        my_data.contact_phone = request.form['contact_phone']
        my_data.contact_email = request.form['contact_email']
        my_data.customer_type_id = request.form['customer_type_id']
        db.session.commit()

        flash("Cliente atualizado com sucesso.")
        return redirect(url_for('customers_index'))

#Delete
@app.route('/customers/delete/<id>/', methods = ['GET', 'POST'])
def customers_delete(id):
    my_data = Customer.query.get(id)
    db.session.delete(my_data)
    db.session.commit()

    flash("Cliente excluído com successo.")
    return redirect(url_for('customers_index'))

################################# Rotas Produtos #################################
@app.route("/products")
def products_index():
    product_set = Customer.query.all()
    return render_template("pages/products.html", page="Produtos", customers = product_set)

#Insert
@app.route('/products/insert', methods = ['POST'])
def products_insert():

    if request.method == 'POST':
        name = request.form['name']
        info = request.form['info']
        html_link = request.form['html_link']
        product_group_name_short = request.form['product_group_name_short']
        product_group_name_long = request.form['product_group_name_long']


        my_data = Product(name, info, html_link, product_group_name_short, product_group_name_long)
        db.session.add(my_data)
        db.session.commit()

        flash("Produto cadastro com sucesso")
        return redirect(url_for('products_index'))

#Update
@app.route('/products/update', methods = ['GET', 'POST'])
def products_update():

    if request.method == 'POST':
        my_data = Product.query.get(request.form.get('id'))
        my_data.name = request.form['name']
        my_data.info = request.form['info']
        my_data.html_link = request.form['html_link']
        my_data.product_group_name_short = request.form['product_group_name_short']
        my_data.product_group_name_long = request.form['product_group_name_long']
        db.session.commit()

        flash("Produto atualizado com sucesso.")
        return redirect(url_for('products_index'))

#Delete
@app.route('/products/delete/<id>/', methods = ['GET', 'POST'])
def products_delete(id):
    my_data = Product.query.get(id)
    db.session.delete(my_data)
    db.session.commit()

    flash("Produto excluído com successo.")
    return redirect(url_for('products_index'))

# Pagina Incial
@app.route("/")
def index():
    return render_template("pages/index.html", page="Sistema eVND")

# Menus a serem construidos
@app.route("/menu/<name>")
def menu(name):
    return render_template("pages/home.html", page=name)


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
