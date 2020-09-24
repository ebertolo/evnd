import os
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import render_template, send_from_directory, session, request, redirect, url_for, flash
from flask_wtf import FlaskForm

from app import app, db
from app.models import Customer, Product

# Serve o Favicon da Aplicação para browsers mais antigos
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Pagina Incial
@app.route("/",  methods = ['GET'])
def index():
    return render_template("pages/index.html", page="Sistema eVND")


# Menus a serem construidos
@app.route("/menu/<name>")
def menu(name):
    return render_template("pages/home.html", page=name)


################################# Erros  Personalizados #################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template("exceptions/404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("exceptions/500.html"), 500


################################# Rotas Cadastro Cliente #################################
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



