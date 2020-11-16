#/usr/bin/python3
import os
from re import S
from urllib.parse import urlparse, urljoin
from flask import render_template, send_from_directory, session, request, redirect, url_for, flash, abort
from flask_login import login_required, login_user, logout_user
from werkzeug.exceptions import HTTPException
from app import app, db, forms
from app.models import Activity, Customer, Partner, Product, SalesPerson, ServiceTicket, User, convert_to_date, get_partner_types, get_service_ticket_status
from app.models import get_customer_types, get_states, get_partner_types, get_activity_types
from sqlalchemy.exc import IntegrityError


""" _________________________________________________________________________________________________
    Links Principais e configuracao da Home
"""
def favicon():
    """Serve Favicon para browsers mais antigos."""
    return send_from_directory(os.path.join(app.root_path, "static"),
                               "favicon.ico", mimetype="image/vnd.microsoft.icon")


@app.route("/",  methods = ["GET"])
@login_required
def index():
    """Pagina Inicial."""
    return render_template("pages/index.html", page="Sistema eVND")


@app.route("/menu/<name>")
@login_required
def menu(name):
    """Menus a serem construidos."""
    return render_template("pages/home.html", page=name)



""" _________________________________________________________________________________________________
    Erros  Personalizados
""" 
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
    next = request.args.get("next")
    print(next)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            flash("Usuario {} logado com sucesso no eVND.".format(form.email.data))
            login_user(user, form.remember_me.data)

            if not is_safe_url(next):
                return abort(400)
            return redirect(next or url_for("index"))

        flash("Dados inválidos favor preencher corretamente.")
    return render_template("pages/login.html",  LoginForm=form)


@app.route("/logout")
@login_required
def logout():
    """Processa comando de logout"""
    logout_user()
    flash("Você efetuou logout do eVND")
    return redirect(url_for("login"))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and \
           ref_url.netloc == test_url.netloc



""" _________________________________________________________________________________________________
    Cadastro Clientes - CRUD
"""
#Create
@login_required
@app.route("/customers/insert", methods = ["POST"])
def customers_insert():
    """Lê form, instancia objeto e persiste no BD com SQLAlchemy"""
    
    message="Novo cadastro incluído com sucesso"
    if request.method == "POST":
        tax_id = request.form["tax_id"] #CNPJ
        customer_type_id = request.form["customer_type_id"]
        name = request.form["name"]
        contact_name = request.form["contact_name"]
        contact_phone = request.form["contact_phone"]
        contact_email = request.form["contact_email"]
        address_line1 = request.form["address_line1"]
        address_line2 = request.form["address_line2"]
        number = request.form["number"]
        postal_code = request.form["postal_code"]
        city = request.form["city"]
        state = request.form["state"]

        if Customer.query.filter_by(name = name).first():
            message = "Já existe um cliente no cadastro com esse nome."
        elif Customer.query.filter_by(contact_email = contact_email).first():
            message = "Já existe um cliente no cadastro com este email de contato."
        elif Customer.query.filter_by(tax_id = tax_id).first():
            message = "Já existe um cliente no cadastro com esse CNPJ"
        else:
            customer = Customer(tax_id, customer_type_id, name, contact_name, contact_phone, contact_email, \
                address_line1, address_line2, number, postal_code, city, state)
            db.session.add(customer)
            db.session.commit()

        flash(message)
        return redirect(url_for("customers_index"))


#Read
@app.route("/customers", methods = ["GET"])
@login_required
def customers_index():
    """Lista os objetos persistidos no DB"""
    customer_set = Customer.query.all()
    return render_template("pages/customers.html", page="Clientes", customers = customer_set, states=get_states(), customer_types=get_customer_types())


#Update
@app.route("/customers/update", methods = ["GET","POST"])
@login_required
def customers_update():
    """Atualiza um objeto carregado em momória e o persiste com SQLAlchemy"""

    message="Cadastro atualizado com sucesso."
    if request.method == "POST":
        customer = Customer.query.get(request.form.get("id"))
        customer.name = request.form["name"]
        customer.tax_id = request.form["tax_id"]
        customer.customer_type_id = request.form["customer_type_id"]
        customer.contact_name = request.form["contact_name"]
        customer.contact_phone = request.form["contact_phone"]
        customer.contact_email = request.form["contact_email"]
        customer.address_line1 = request.form["address_line1"]
        customer.address_line2 = request.form["address_line2"]
        customer.number = request.form["number"]
        customer.postal_code = request.form["postal_code"]
        customer.city = request.form["city"]
        customer.state = request.form["state"]

        try:
            db.session.commit() 
        except IntegrityError:
            db.session.rollback()
            message = "Dados incorretos, novo nome, email ou CNPJ em uso por outro cadastro." 

        flash(message)
        return redirect(url_for("customers_index"))


#Delete
@app.route("/customers/delete/<id>/", methods = ["GET", "POST"])
@login_required
def customers_delete(id):
    message="Cadastro excluído com sucesso."
    customer = Customer.query.get(id)
    db.session.delete(customer)
    try:
        db.session.commit() 
    except IntegrityError:
        db.session.rollback()
    message = "Não é possivel excluir esse registro pois está em uso."

    flash(message)
    return redirect(url_for("customers_index"))



""" _________________________________________________________________________________________________
    Cadastro Produtos - CRUD
""" 
#Create
@app.route("/products/insert", methods = ["POST"])
@login_required
def products_insert():
    """Lê form, instancia objeto e persiste no BD com SQLAlchemy"""
    message="Novo cadastro incluído com sucesso"
    if request.method == "POST":
        code =  request.form["code"]
        name = request.form["name"]
        info = request.form["info"]
        html_link = request.form["html_link"]
        group_name_short = request.form["group_name_short"]
        group_name_long = request.form["group_name_long"]

        if Product.query.filter_by(name = name).first():
            message = "Já existe um produto no cadastro com esse nome"
        else:
            product = Product(code, name, info, html_link, group_name_short, group_name_long)
            db.session.add(product)
            db.session.commit()

        flash(message)
        return redirect(url_for("products_index"))


#Read
@app.route("/products")
@login_required
def products_index():
    """Lista os objetos persistidos no DB"""
    product_set = Product.query.all()
    return render_template("pages/products.html", page="Produtos", products = product_set)


#Update
@app.route("/products/update", methods = ["GET", "POST"])
@login_required
def products_update():
    """Atualiza um objeto carregado em momória e o persiste com SQLAlchemy"""

    message = "Cadastro atualizado com sucesso."
    if request.method == "POST":
        product = Product.query.get(request.form.get("id"))
        product.code = request.form["code"]
        product.name = request.form["name"]
        product.info = request.form["info"]
        product.html_link = request.form["html_link"]
        product.group_name_short = request.form["group_name_short"]
        product.group_name_long =  request.form["group_name_long"]

        try:
            db.session.commit() 
        except IntegrityError:
            db.session.rollback()
            message = "Novo nome em uso por outro cadastro." 

        flash(message)
        return redirect(url_for("products_index"))


#Delete
@app.route("/products/delete/<id>/", methods = ["GET", "POST"])
@login_required
def products_delete(id):
    message = "Cadastro excluído com successo."
    product = Product.query.get(id)
    db.session.delete(product)

    try:
        db.session.commit() 
    except IntegrityError:
        db.session.rollback()
    message = "Não é possivel excluir esse registro pois está em uso."

    flash(message)
    return redirect(url_for("products_index"))



""" _________________________________________________________________________________________________
    Cadastro Força de Vendas - CRUD
""" 
#Create
@app.route("/sales-person/insert", methods = ["POST"])
@login_required
def sales_person_insert():
    """Lê form, instancia objeto e persiste no BD com SQLAlchemy"""

    message="Novo cadastro incluído com sucesso"
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]

        if SalesPerson.query.filter_by(email = email).first():
            message = "Já existe um parceiro no cadastro com esse email"
        else:
            salesperson = SalesPerson(name, phone, email)
            db.session.add(salesperson)
            db.session.commit()

        flash(message)
        return redirect(url_for("sales_person_index"))


#Read
@app.route("/sales-person")
@login_required
def sales_person_index():
    """Lista os objetos persistidos no DB"""
    salesperson_set = SalesPerson.query.all()
    return render_template("pages/sales-team.html", page="Equipe", salesteam=salesperson_set)


#Update
@app.route("/sales-person/update", methods = ["GET", "POST"])
@login_required
def sales_person_update():
    """Atualiza um objeto carregado em momória e o persiste com SQLAlchemy"""

    message = "Cadastro atualizado com sucesso."
    if request.method == "POST":
        salesperson = SalesPerson.query.get(request.form.get("id"))
        salesperson.name = request.form["name"]
        salesperson.phone = request.form["phone"]
        salesperson.email = request.form["email"]

        try:
            db.session.commit() 
        except IntegrityError:
            db.session.rollback()
            message = "Novo Email em uso por outro cadastro."

        flash(message)
        return redirect(url_for("sales_person_index"))


#Delete
@app.route("/salesperson/delete/<id>/", methods = ["GET", "POST"])
@login_required
def sales_person_delete(id):
    message="Cadastro excluído com sucesso."
    salesperson = SalesPerson.query.get(id)
    db.session.delete(salesperson)
    try:
        db.session.commit() 
    except IntegrityError:
        db.session.rollback()
    message = "Não é possivel excluir esse registro pois está em uso."

    flash(message)
    return redirect(url_for("sales_person_index"))



""" _________________________________________________________________________________________________
    Cadastro Parceiros (Fornecedores e Assistência Ténica) - CRUD
""" 
#Create
@app.route("/partners/insert", methods = ["POST"])
@login_required
def partner_insert():
    """Lê form, instancia objeto e persiste no BD com SQLAlchemy"""

    message = "Novo cadastro incluído com sucesso"
    if request.method == "POST":
        name  = request.form["name"]
        contact_name = request.form["contact_name"]
        contact_phone = request.form["contact_phone"]
        contact_email = request.form["contact_email"]
        tax_id = request.form["tax_id"]
        partner_type_id = request.form["partner_type_id"]

        if Partner.query.filter_by(name = name).first():
            message = "Já existe um parceiro no cadastro com esse nome"
        elif Partner.query.filter_by(contact_email = contact_email).first():
            message = "Já existe um parceiro no cadastro com este email de contato"
        elif Partner.query.filter_by(tax_id = tax_id).first():
            message = "Já existe um parceiro no cadastro com esse CNPJ"
        else:
            partner = Partner(name, contact_name, contact_phone, contact_email, tax_id, partner_type_id)
            db.session.add(partner)
            db.session.commit()
            
        flash(message)
        return redirect(url_for("partner_index"))

#Read
@app.route("/partners")
@login_required
def partner_index():
    """Lista os objetos persistidos no DB"""
    partner_set = Partner.query.all()
    return render_template("pages/partners.html", page="Parceiros", partner_types=get_partner_types(), partners = partner_set)


#Update
@app.route("/partners/update", methods = ["GET", "POST"])
@login_required
def partner_update():
    """Atualiza um objeto carregado em momória e o persiste com SQLAlchemy"""

    message = "Cadastro atualizado com sucesso."
    if request.method == "POST":
        partner = Partner.query.get(request.form.get("id"))
        partner.name = request.form["name"]
        partner.contact_name = request.form["contact_name"]
        partner.contact_phone = request.form["contact_phone"]
        partner.contact_email = request.form["contact_email"]
        partner.tax_id =  request.form["tax_id"]
        partner.partner_type_id =  request.form["partner_type_id"]

        try:
            db.session.commit() 
        except IntegrityError:
            db.session.rollback()
            message = "Dados incorretos. CNPJ, Email ou Nome em uso por outro cadastro."
        
        flash(message)
        return redirect(url_for("partner_index"))


#Delete
@app.route("/partners/delete/<id>/", methods = ["GET", "POST"])
@login_required
def partner_delete(id):
    message="Cadastro excluído com sucesso."
    partner = Partner.query.get(id)
    db.session.delete(partner)
    try:
        db.session.commit() 
    except IntegrityError:
        db.session.rollback()
    message = "Não é possivel excluir esse registro pois está em uso."

    flash(message)
    return redirect(url_for("partner_index"))



""" _________________________________________________________________________________________________
    Cadastro Chamados do CRM  - CRUD
""" 
#Create
@app.route("/service-tickets/insert", methods = ["POST"])
@login_required
def service_ticket_insert():

    """Lê form, instancia objeto e persiste no BD com SQLAlchemy"""
    if request.method == "POST":
        id_status = request.form["id_status"]
        id_customer = request.form["id_customer"]
        id_product = request.form["id_product"]
        id_activity = request.form["id_activity"]
        id_partner = request.form["id_partner"]
        request_date = convert_to_date(request.form["request_date"])
        done_date = convert_to_date(request.form["request_date"]) if request.form["request_date"] else None
        description = request.form["description"]

        serviceticket = ServiceTicket(id_status, id_customer, id_product, id_activity, id_partner, \
                          done_date, request_date, description)
        db.session.add(serviceticket)
        db.session.commit()

        flash("Novo cadastro incluído com sucesso")
        return redirect(url_for("service_ticket_index"))


#Read
@app.route("/service-tickets")
@login_required
def service_ticket_index():
    """Lista os objetos persistidos no DB"""
    serviceticket_set = ServiceTicket.query.all()
    return render_template("pages/service-tickets.html", page="Chamados", servicetickets = serviceticket_set, \
                            customers_list=get_customers_list(), products_list=get_products_list(), \
                            activities_list=get_activities_list(), partners_list=get_partners_list(), \
                            service_ticket_status=get_service_ticket_status(), partner_types=get_partner_types(),
                            activity_types=get_activity_types())


#Update
@app.route("/service-tickets/update", methods = ["GET", "POST"])
@login_required
def service_ticket_update():
    """Atualiza um objeto carregado em momória e o persiste com SQLAlchemy"""
    if request.method == "POST":
        serviceticket = ServiceTicket.query.get(request.form.get("id"))
        serviceticket.id_status = request.form["id_status"]
        serviceticket.id_customer = request.form["id_customer"]
        serviceticket.id_product = request.form["id_product"]
        serviceticket.id_activity = request.form["id_activity"]
        serviceticket.id_partner = request.form["id_partner"]
        serviceticket.request_date = convert_to_date(request.form["request_date"])
        serviceticket.done_date = convert_to_date(request.form["done_date"])
        serviceticket.description = request.form["description"]
        db.session.commit() 

        flash("Cadastro atualizado com sucesso.")
        return redirect(url_for("service_ticket_index"))


#Delete
@app.route("/service-tickets/delete/<id>/", methods = ["GET", "POST"])
@login_required
def service_ticket_delete(id):
    serviceticket = ServiceTicket.query.get(id)
    db.session.delete(serviceticket)
    db.session.commit()
    
    flash("Cadastro excluído com sucesso.")
    return redirect(url_for("service_ticket_index"))



""" _________________________________________________________________________________________________
    Cadastro Atividades do CRM  - CRUD
""" 
#Create
@app.route("/actvities/insert", methods = ["POST"])
@login_required
def activities_insert():

    """Lê form, instancia objeto e persiste no BD com SQLAlchemy"""
    if request.method == "POST":
        id_status = request.form["id_status"]
        id_activity_type = request.form["id_activity_type"]
        id_customer = request.form["id_customer"]
        id_sales_person = request.form["id_sales_person"]
        id_product = request.form["id_product"]
        planned_date = request.form["planned_date"]
        done_date = request.form["done_date"]
        description = request.form["description"]

        partner = Partner(id_status, id_activity_type, id_customer, id_sales_person, id_product, \
                          planned_date, done_date, description)
        db.session.add(partner)
        db.session.commit()

        flash("Novo cadastro incluído com sucesso")
        return redirect(url_for("activities_index"))


#Read
@app.route("/actvities")
@login_required
def activities_index():
    """Lista os objetos persistidos no DB"""
    activity_set = Activity.query.all()
    return render_template("pages/activities.html", page="Atividades", activities = activity_set)


#Update
@app.route("/actvities/update", methods = ["GET", "POST"])
@login_required
def activities_update():
    """Atualiza um objeto carregado em momória e o persiste com SQLAlchemy"""
    if request.method == "POST":
        activity = Activity.query.get(request.form.get("id"))
        activity.id_status = request.form["id_status"]
        activity.id_activity_type = request.form["id_activity_type"]
        activity.id_customer = request.form["id_customer"]
        activity.id_sales_person = request.form["id_sales_person"]
        activity.id_product = request.form["id_product"]
        activity.planned_date = request.form["planned_date"]
        activity.done_date = request.form["done_date"]
        activity.description = request.form["description"]
        db.session.commit() 

        flash("Cadastro atualizado com sucesso.")
        return redirect(url_for("activities_index"))


#Delete
@app.route("/actvities/delete/<id>/", methods = ["GET", "POST"])
@login_required
def activities_delete(id):
    activity = Activity.query.get(id)
    db.session.delete(activity)
    db.session.commit()

    flash("Cadastro excluído com sucesso.")
    return redirect(url_for("activities_index"))


def get_customers_list():
    customers = [[0, "--"]] + [[customer.id, customer.name] for customer in Customer.query.all()]
    return customers

def get_products_list():
    products = [[0, "--"]] + [[product.id, product.name] for product in Product.query.all()]
    return products

def get_partners_list():
    partners = [[0, "--", "--"]] + [[partner.id, partner.name, partner.partner_type_id] for partner in Partner.query.all()]
    return partners

def get_activities_list():
    activities = [[0, "--", "--"]] + [[activity.id, str(activity.id).zfill(4) + " - " + activity.sales_person.name, activity.id_activity_type] for activity in Activity.query.all()]
    return activities
