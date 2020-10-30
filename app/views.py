#/usr/bin/python3
import os
from urllib.parse import urlparse, urljoin
from flask import render_template, send_from_directory, session, request, redirect, url_for, flash, abort
from flask_login import login_required, login_user, logout_user
from werkzeug.exceptions import HTTPException
from app import app, db, forms
from app.models import Customer, Product, User


#   _________________________________________________________________________________________________
#   Links Principais e configuracao da Home

def favicon():
    """Serve Favicon para browsers mais antigos."""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/",  methods = ['GET'])
@login_required
def index():
    """Pagina Inicial."""
    return render_template("pages/index.html", page="Sistema eVND")

@app.route("/menu/<name>")
@login_required
def menu(name):
    """Menus a serem construidos."""
    return render_template("pages/home.html", page=name)


#   _________________________________________________________________________________________________
#   Erros  Personalizados

@app.errorhandler(404)
def page_not_found(e):
    """Retorna pagina de erro para rotas não existentes e mantém code orginal 404"""
    return render_template("exceptions/404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Retorna pagina de erro para erros gerais e mantem code original 500"""
    return render_template("exceptions/500.html"), 500

# TODO: DESCOMENTAR ASSIM QUE TERMINAR OS MODULOS
# @app.errorhandler(Exception)
# def handle_500(e):
#     """Gerencia erros internos não previstos e exibe mensagem amigável"""
#     original = getattr(e, "original_exception", None)
#
#     if original is None:
#         return render_template("exceptions/500.html"), 500
#
#     return render_template("exceptions/500.html", e=original), 500


""" _________________________________________________________________________________________________
    Login Usuarios 
""" 
@app.route("/login", methods=["GET", "POST"])
def login():
    """Renderiza e processa o formulário de login"""
    form = forms.LoginForm()
    next = request.args.get('next')
    print(next)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            flash("Usuario {} logado com sucesso no eVND.".format(form.email.data))
            login_user(user, form.remember_me.data)

            if not is_safe_url(next):
                return abort(400)
            return redirect(next or url_for('index'))

        flash("Dados inválidos favor preencher corretamente.")
    return render_template("pages/login.html",  LoginForm=form)

@app.route("/logout")
@login_required
def logout():
    """Processa comando de logout"""
    logout_user()
    flash("Você efetuou logout do eVND")
    return redirect(url_for("login"))


""" _________________________________________________________________________________________________
    Cadastro Clientes 
"""
@app.route("/customers")
@login_required
def customers_index():
    customer_set = Customer.query.all()
    return render_template("pages/customers.html", page="Clientes", customers = customer_set)

#Insert
@app.route('/customers/insert', methods = ['POST'])
@login_required
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
@login_required
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
@login_required
def customers_delete(id):
    my_data = Customer.query.get(id)
    db.session.delete(my_data)
    db.session.commit()

    flash("Cliente excluído com successo.")
    return redirect(url_for('customers_index'))



""" _________________________________________________________________________________________________
    Cadastro Produtos 
""" 
@app.route("/products")
@login_required
def products_index():
    product_set = Customer.query.all()
    return render_template("pages/products.html", page="Produtos", customers = product_set)

#Insert
@app.route('/products/insert', methods = ['POST'])
@login_required
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
@login_required
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
@login_required
def products_delete(id):
    my_data = Product.query.get(id)
    db.session.delete(my_data)
    db.session.commit()

    flash("Produto excluído com successo.")
    return redirect(url_for('products_index'))




def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc