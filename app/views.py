#/usr/bin/python3
from operator import ge
import os
from re import S
from urllib.parse import urlparse, urljoin
from flask import render_template, send_from_directory, session, request, redirect, url_for, flash, abort
from flask_login import login_required, login_user, logout_user
from sqlalchemy.sql.functions import current_time
from werkzeug.exceptions import HTTPException
from app import app, db, forms
from app.models import Activity, Customer, Partner, Product, SalesPerson, ServiceTicket, User, convert_to_date, get_activity_status, get_partner_types, get_service_ticket_status
from app.models import get_customer_types, get_states, get_partner_types, get_activity_types, get_role_types
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError
from datetime import datetime



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
    return render_template("pages/index.html", page="Sistema eVND", current_time=datetime.utcnow())


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

            # Salva os dados gerais na sessão do usuário
            update_user_info(user.short_name, user.id_role)
            update_count_activities()
            update_count_service_tickets()

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
    """Valida se url é segura, evita redirecionamento malicioso"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and \
           ref_url.netloc == test_url.netloc


""" _________________________________________________________________________________________________
    Cadastro Usuarios - CRUD
""" 
#Create
@app.route("/users/insert", methods = ["POST"])
@login_required
def users_insert():
    """Lê form, instancia objeto e persiste no BD com SQLAlchemy"""

    message="Novo cadastro incluído com sucesso"
    if request.method == "POST":
        id_role = request.form["id_role"]
        short_name = request.form["short_name"]
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email = email).first():
            message = "Já usuário no cadastro com esse email."

        elif len(email) < 6:
            message = "Senha deve ter pelo menos 6 caracteres."

        else:
            user = User(email, password, short_name, full_name, id_role)
            db.session.add(user)
            db.session.commit()

        flash(message)
        return redirect(url_for("users_index"))


#Read
@app.route("/users")
@login_required
def users_index():
    """Lista os objetos persistidos no DB"""
    users_set = User.query.all()
    return render_template("pages/users.html", page="Usuários do eVND", role_types=get_role_types(), users=users_set, current_time=datetime.utcnow())


#Update
@app.route("/users/update", methods = ["GET", "POST"])
@login_required
def users_update():
    """Atualiza um objeto carregado em momória e o persiste com SQLAlchemy"""

    message = "Cadastro atualizado com sucesso."
    if request.method == "POST":
        user = User.query.get(request.form.get("id"))
        user.short_name = request.form["short_name"]
        user.full_name = request.form["full_name"]
        user.email = request.form["email"]
        new_password = request.form["password"]
        if new_password:
            if len(new_password) < 6:
                flash("A nova senha precisa ter pelo menos 6 caracteres.")
            else:
                user.password = new_password
        
        if User.query.filter_by(email = user.email).filter(User.id != user.id).first():
            message = "Já existe usuário no cadastro com esse email."
            db.session.rollback()

        else:
            try:
                db.session.commit() 
            except IntegrityError:
                db.session.rollback()
                message = "Novo Email em uso por outro cadastro."

        flash(message)
        return redirect(url_for("users_index"))


#Delete
@app.route("/users/delete/<id>/", methods = ["GET", "POST"])
@login_required
def users_delete(id):
    """Exclui item selecionado"""

    message="Cadastro excluído com sucesso."
    if 1 > 0:#Activity.query.filter_by(id_sales_person=id).count() > 0:
        message = "Não é possível excluir membro da equipe com atividades cadastradas."
    
    else:
        user = User.query.get(id)
        db.session.delete(user)
        try:
            db.session.commit() 
        except IntegrityError:
            db.session.rollback()
            message = "Não é possivel excluir esse registro pois está em uso."
  
    flash(message)
    return redirect(url_for("users_index"))



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
    return render_template("pages/customers.html", page="Empresas Clientes", customers = customer_set, \
                            states=get_states(), customer_types=get_customer_types(), current_time=datetime.utcnow())


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

        if Customer.query.filter_by(name = customer.name).filter(Customer.id != customer.id).first():
            message = "Já existe um cliente no cadastro com esse nome."
            db.session.rollback()

        elif Customer.query.filter_by(contact_email = customer.contact_email).filter(Customer.id != customer.id).first():
            message = "Já existe um cliente no cadastro com este email de contato."
            db.session.rollback()

        elif Customer.query.filter_by(tax_id = customer.tax_id).filter(Customer.id != customer.id).first():
            message = "Já existe um cliente no cadastro com esse CNPJ"
            db.session.rollback()

        else:
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
    """Exclui item selecionado"""

    message="Cadastro excluído com sucesso."    
    if Activity.query.filter_by(id_customer=id).count() > 0:
        message = "Não é possível excluir clientes com atividades cadastradas."
    
    elif ServiceTicket.query.filter_by(id_customer=id).count() > 0:
        message = "Não é possível excluir clientes com chamados cadastradas."
        
    else:
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
    message="Novo cadastro incluído com sucesso."
    if request.method == "POST":
        code =  request.form["code"]
        id_partner = request.form["id_partner"]
        id_partner_support = request.form["id_partner_support"]
        name = request.form["name"]
        info = request.form["info"]
        html_link = request.form["html_link"]
        group_name_short = request.form["group_name_short"]
        group_name_long = request.form["group_name_long"]

        if Product.query.filter_by(code = code).first():
            message = "Já existe um produto no cadastro com esse codigo."

        elif int(id_partner) == 0:
            message = "É necessario selecionar um fornecedor."
        
        elif Product.query.filter_by(name = name).first():
            message = "Já existe um produto no cadastro com esse nome."

        else:
            product = Product(code, id_partner, id_partner_support, name, info, html_link, group_name_short, group_name_long)
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
    return render_template("pages/products.html", page="Catálogo de Produtos", products = product_set, suppliers_list=get_suppliers_list(), supporters_list=get_supporters_list(), current_time=datetime.utcnow())


#Update
@app.route("/products/update", methods = ["GET", "POST"])
@login_required
def products_update():
    """Atualiza um objeto carregado em momória e o persiste com SQLAlchemy"""

    message = "Cadastro atualizado com sucesso."
    if request.method == "POST":
        product = Product.query.get(request.form.get("id"))
        product.code = request.form["code"]
        product.id_partner = request.form["id_partner"]
        product.id_partner_support = request.form["id_partner_support"]
        product.name = request.form["name"]
        product.info = request.form["info"]
        product.html_link = request.form["html_link"]
        product.group_name_short = request.form["group_name_short"]
        product.group_name_long =  request.form["group_name_long"]


        if Product.query.filter_by(code = product.code).filter(Product.id != product.id).first():
            message = "Já existe um produto no cadastro com esse codigo."
            db.session.rollback()
        
        elif int(product.id_partner) == 0:
            message = "É necessario selecionar um fornecedor."
            db.session.rollback()
        
        elif Product.query.filter_by(name = product.name).filter(Product.id != product.id).first():
            message = "Já existe um produto no cadastro com esse nome."
            db.session.rollback()

        else:
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
    """Exclui item selecionado"""
    
    message = "Cadastro excluído com successo."
    if Activity.query.filter_by(id_product=id).count() > 0:
        message = "Não é possível excluir produtos com atividades cadastradas."

    elif ServiceTicket.query.filter_by(id_product=id).count() > 0:
        message = "Não é possível excluir produtos com chamados cadastradas."

    else:
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
            message = "Já existe um membro de equipe no cadastro com esse email."

        if SalesPerson.query.filter_by(name = name).first():
            message = "Já existe um membro de equipe no cadastro com esse nome."

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
    return render_template("pages/sales-team.html", page="Equipe de Vendas", users=get_users_list(), salesteam=salesperson_set, current_time=datetime.utcnow())


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

        if SalesPerson.query.filter_by(email = salesperson.email).filter(SalesPerson.id != salesperson.id).first():
            message = "Já existe um membro de equipe no cadastro com esse email."
            db.session.rollback()

        if SalesPerson.query.filter_by(name = salesperson.name).filter(SalesPerson.id != salesperson.id).first():
            message = "Já existe um membro de equipe no cadastro com esse nome."
            db.session.rollback()

        else:
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
    """Exclui item selecionado"""

    message="Cadastro excluído com sucesso."
    if Activity.query.filter_by(id_sales_person=id).count() > 0:
        message = "Não é possível excluir membro da equipe com atividades cadastradas."
    
    else:
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
def partners_insert():
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
        return redirect(url_for("partners_index"))

#Read
@app.route("/partners")
@login_required
def partners_index():
    """Lista os objetos persistidos no DB"""
    partner_set = Partner.query.all()
    return render_template("pages/partners.html", page="Parceiros de Negócios", partner_types=get_partner_types(), partners = partner_set, current_time=datetime.utcnow())


#Update
@app.route("/partners/update", methods = ["GET", "POST"])
@login_required
def partners_update():
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


        if Partner.query.filter_by(name = partner.name).filter(Partner.id != partner.id).first():
            message = "Já existe um parceiro no cadastro com esse nome"
            db.session.rollback()

        elif Partner.query.filter_by(contact_email = partner.contact_email).filter(Partner.id != partner.id).first():
            message = "Já existe um parceiro no cadastro com este email de contato"
            db.session.rollback()

        elif Partner.query.filter_by(tax_id = partner.tax_id).filter(Partner.id != partner.id).first():
            message = "Já existe um parceiro no cadastro com esse CNPJ"        
            db.session.rollback()

        else:
            try:
                db.session.commit() 
            except IntegrityError:
                db.session.rollback()
                message = "Dados incorretos. CNPJ, Email ou Nome em uso por outro cadastro."
        
        flash(message)
        return redirect(url_for("partners_index"))


#Delete
@app.route("/partners/delete/<id>/", methods = ["GET", "POST"])
@login_required
def partners_delete(id):
    message="Cadastro excluído com sucesso."

    if ServiceTicket.query.filter_by(id_partner=id).count() > 0:
        message = "Não é possível excluir parceiros referenciados em chamados cadastradas."
    
    elif Product.query.filter_by(id_partner=id).count() > 0:
        message = "Não é possível excluir parceiros referenciados como Fornecedor de um Produto."
    
    elif Product.query.filter_by(id_partner_support=id).count() > 0:
        message = "Não é possível excluir parceiros referenciados como Assistência Técnica de um Produto."

    else:
        partner = Partner.query.get(id)
        db.session.delete(partner)
        try:
            db.session.commit() 
        except IntegrityError:
            db.session.rollback()
            message = "Não é possivel excluir esse registro pois está em uso."

    flash(message)
    return redirect(url_for("partners_index"))



""" _________________________________________________________________________________________________
    Cadastro Chamados do CRM  - CRUD
""" 
#Create
@app.route("/service-tickets/insert", methods = ["POST"])
@login_required
def service_ticket_insert():
    """Lê form, instancia objeto e persiste no BD com SQLAlchemy"""

    message = "Novo cadastro incluído com sucesso"
    if request.method == "POST":
        id_status = request.form["id_status"]
        id_customer = request.form["id_customer"]
        id_product = request.form["id_product"]
        id_activity = request.form["id_activity"]
        id_partner = request.form["id_partner"]
        request_date = convert_to_date(request.form["request_date"])
        done_date = convert_to_date(request.form["done_date"]) if request.form["done_date"] else None
        description = request.form["description"]
 
        if int(id_customer) == 0:
            message = "É necessário selecionar um Cliente."

        else:
            serviceticket = ServiceTicket(id_status, id_customer, id_product, id_activity, id_partner, \
                            request_date, done_date, description)
            db.session.add(serviceticket)
            db.session.commit()

        #Atualiza badge de número de chamados pendentes no menu principal
        update_count_service_tickets()

        flash(message)
        return redirect(url_for("service_ticket_index"))


#Read
@app.route("/service-tickets")
@login_required
def service_ticket_index():
    """Lista os objetos persistidos no DB"""
    serviceticket_set = ServiceTicket.query.all()
    return render_template("pages/service-tickets.html", page="Chamados de Clientes", servicetickets = serviceticket_set, \
                            customers_list=get_customers_list(), products_list=get_products_list(), \
                            activities_list=get_activities_list(), partners_list=get_partners_list(), \
                            service_ticket_status=get_service_ticket_status(), partner_types=get_partner_types(),
                            activity_types=get_activity_types(), current_time=datetime.utcnow())


#Update
@app.route("/service-tickets/update", methods = ["GET", "POST"])
@login_required
def service_ticket_update():
    """Atualiza um objeto carregado em momória e o persiste com SQLAlchemy"""
    
    message="Cadastro atualizado com sucesso."
    if request.method == "POST":
        serviceticket = ServiceTicket.query.get(request.form.get("id"))
        serviceticket.id_status = request.form["id_status"]
        serviceticket.id_customer = request.form["id_customer"]
        serviceticket.id_product = request.form["id_product"]
        serviceticket.id_activity = request.form["id_activity"]
        serviceticket.id_partner = request.form["id_partner"]
        serviceticket.request_date = convert_to_date(request.form["request_date"])
        serviceticket.done_date = convert_to_date(request.form["done_date"]) if request.form["done_date"] else None
        serviceticket.description = request.form["description"]
        
        if serviceticket.id_customer == 0:
            message = "É necessário selecionar um Cliente."
            db.session.rollback()
        
        else:
            db.session.commit() 
            #Atualiza badge de número de chamados pendentes no menu principal
            update_count_service_tickets()

        flash(message)
        return redirect(url_for("service_ticket_index"))


#Delete
@app.route("/service-tickets/delete/<id>/", methods = ["GET", "POST"])
@login_required
def service_ticket_delete(id):
    """Exclui registro selecionado"""


    serviceticket = ServiceTicket.query.get(id)
    db.session.delete(serviceticket)
    db.session.commit()

    #Atualiza badge de número de chamados pendentes no menu principal
    update_count_service_tickets()
    
    flash("Cadastro excluído com sucesso.")
    return redirect(url_for("service_ticket_index"))



""" _________________________________________________________________________________________________
    Cadastro Atividades do CRM  - CRUD
""" 
#Create
@app.route("/activities/insert", methods = ["POST"])
@login_required
def activities_insert():
    """Lê form, instancia objeto e persiste no BD com SQLAlchemy"""

    message = "Novo cadastro incluído com sucesso"
    if request.method == "POST":
        id_status = request.form["id_status"]
        id_activity_type = request.form["id_activity_type"]
        id_customer = request.form["id_customer"]
        id_sales_person = request.form["id_sales_person"]
        id_product = request.form["id_product"]
        planned_date = convert_to_date(request.form["planned_date"])
        done_date = convert_to_date(request.form["done_date"]) if request.form["done_date"] else None
        description = request.form["description"]

        if int(id_customer) == 0:
            message = "É necessário selecionar um cliente."

        elif int(id_sales_person) == 0:
            message = "É necessário selecionar um vendedor responsável pela atividade."

        else:
            activity = Activity(id_status, id_activity_type, id_customer, id_sales_person, id_product, \
                            planned_date, done_date, description)
            db.session.add(activity)
            db.session.commit()

            #Atualiza badge de atividades pendentes no menu principal
            update_count_activities()

        flash(message)
        return redirect(url_for("activities_index"))


#Read
@app.route("/activities")
@login_required
def activities_index():
    """Lista os objetos persistidos no DB"""
    activity_set = Activity.query.all()
    return render_template("pages/activities.html", page="Atividades da Equipe de Vendas", activities = activity_set, \
                            activity_status=get_activity_status(), activity_types=get_activity_types(), \
                            customers_list=get_customers_list(), salesperson_list=get_salesperson_list(), \
                            products_list=get_products_list(),current_time=datetime.utcnow())


#Update
@app.route("/activities/update", methods = ["GET", "POST"])
@login_required
def activities_update():
    """Atualiza um objeto carregado em momória e o persiste com SQLAlchemy"""

    message = "Cadastro atualizado com sucesso."
    if request.method == "POST":
        activity = Activity.query.get(request.form.get("id"))
        activity.id_status = request.form["id_status"]
        activity.id_activity_type = request.form["id_activity_type"]
        activity.id_customer = request.form["id_customer"]
        activity.id_sales_person = request.form["id_sales_person"]
        activity.id_product = request.form["id_product"]
        activity.planned_date = convert_to_date(request.form["planned_date"])
        activity.done_date = convert_to_date(request.form["done_date"]) if request.form["done_date"] else None
        activity.description = request.form["description"]
        
        if int(activity.id_customer) == 0:
            message = "É necessário selecionar um cliente."
            db.session.rollback()

        elif int(activity.id_sales_person) == 0:
            message = "É necessário selecionar um vendedor responsável pela atividade."
            db.session.rollback()

        else:
            db.session.commit() 
            #Atualiza badge de atividades pendentes no menu principal
            update_count_activities()

        flash(message)
        return redirect(url_for("activities_index"))


#Delete
@app.route("/activities/delete/<id>/", methods = ["GET", "POST"])
@login_required
def activities_delete(id):
    """Exclui registro selecionado"""
    
    message="Cadastro excluído com sucesso."
    if ServiceTicket.query.filter_by(id_activity=id).count() > 0:
        message = "Não é possível excluir atividades referenciadas em chamados cadastrados."

    else:
        activity = Activity.query.get(id)
        db.session.delete(activity)
        db.session.commit()

        #Atualiza badge de atividades pendentes no menu principal
        update_count_activities()

    flash(message)
    return redirect(url_for("activities_index"))


""" _________________________________________________________________________________________________
    Relatórios de Chamados
""" 
@app.route("/reports/tickets/customer")
@login_required
def rpt_tickets_customer():
    """Lista os items do Relatorio agrupando por tipo e com count decrescente"""
    report_set = db.session.query(ServiceTicket.id_customer, func.count(ServiceTicket.id).label("Total")).\
                        group_by(ServiceTicket.id_customer).order_by(desc("Total")).all()
    return render_template("pages/reports.html", page="Top Clientes em Quantidade de Chamados", report_set = report_set, \
                            report_list=get_customers_list(), report_type_name="Chamados", report_head_name="Cliente", current_time=datetime.utcnow())


@app.route("/reports/tickets/partner")
@login_required
def rpt_tickets_partner():
    """Lista os items do Relatorio agrupando por tipo e com count decrescente"""
    report_set = db.session.query(ServiceTicket.id_partner, func.count(ServiceTicket.id).label("Total")).filter(ServiceTicket.id_partner != 0).\
                        group_by(ServiceTicket.id_partner).order_by(desc("Total")).all()
    return render_template("pages/reports.html", page="Top Parceiros em Quantidade de Chamados", report_set = report_set, \
                            report_list=get_partners_list(), report_type_name="Chamados", report_head_name="Parceiro", current_time=datetime.utcnow())


@app.route("/reports/tickets/product")
@login_required
def rpt_tickets_product():
    """Lista os items do Relatorio agrupando por tipo e com count decrescente"""
    report_set = db.session.query(ServiceTicket.id_product, func.count(ServiceTicket.id).label("Total")).filter(ServiceTicket.id_product != 0).\
                        group_by(ServiceTicket.id_product).order_by(desc("Total")).all()
    return render_template("pages/reports.html", page="Top Produtos em Quantidade de Chamados", report_set = report_set, \
                            report_list=get_products_list(), report_type_name="Chamados", report_head_name="Produto", current_time=datetime.utcnow())



""" _________________________________________________________________________________________________
    Relatórios de Atividades
""" 
@app.route("/reports/activities/customer")
@login_required
def rpt_activities_customer():
    """Lista os items do Relatorio agrupando por tipo e com count decrescente"""
    report_set = db.session.query(Activity.id_customer, func.count(Activity.id).label("Total")).\
                        group_by(Activity.id_customer).order_by(desc("Total")).all()
    return render_template("pages/reports.html", page="Top Clientes em Quantidade de Atividades", report_set = report_set, \
                            report_list=get_customers_list(), report_type_name="Atividades", report_head_name="Cliente", current_time=datetime.utcnow())


@app.route("/reports/activities/salesperson")
@login_required
def rpt_activities_salesperson():
    """Lista os items do Relatorio agrupando por tipo e com count decrescente"""
    report_set = db.session.query(Activity.id_sales_person, func.count(Activity.id).label("Total")).\
                        group_by(Activity.id_sales_person).order_by(desc("Total")).all()
    return render_template("pages/reports.html", page="Top Vendedor em Quantidade de Atividades", report_set = report_set, \
                            report_list=get_salesperson_list(), report_type_name="Atividades", report_head_name="Vendedor", current_time=datetime.utcnow())


@app.route("/reports/activities/product")
@login_required
def rpt_activities_product():
    """Lista os items do Relatorio agrupando por tipo e com count decrescente"""
    report_set = db.session.query(Activity.id_product, func.count(Activity.id).label("Total")).filter(Activity.id_product != 0).\
                        group_by(Activity.id_product).order_by(desc("Total")).all()
    return render_template("pages/reports.html", page="Top Produdo em Quantidade de Atividades", report_set = report_set, \
                            report_list=get_products_list(), report_type_name="Atividades", report_head_name="Produto", current_time=datetime.utcnow())


def get_users_list():
    """Seleciona apenas usuarios do Perfil Vendas"""
    users = [[0, "--"]] + [[user.id, user.short_name + " - " + user.email] for user in User.query.filter_by(id_role=1).order_by().all()]
    return users

def get_salesperson_list():
    salesteam = [[0, "--"]]+ [[salesperson.id, salesperson.name] for salesperson in SalesPerson.query.all()]
    return salesteam

def get_customers_list():
    customers = [[0, "--"]] + [[customer.id, customer.name] for customer in Customer.query.all()]
    return customers

def get_products_list():
    products = [[0, "--"]] + [[product.id, product.name] for product in Product.query.all()]
    return products

def get_partners_list():
    partners = [[0, "--"]] + [[partner.id, partner.name] for partner in Partner.query.all()]
    return partners

def get_suppliers_list():
    partners = [[0, "--"]] + [[partner.id, partner.name] for partner in Partner.query.filter_by(partner_type_id=1).all()]
    return partners

def get_supporters_list():
    partners = [[0, "--", "--"]] + [[partner.id, partner.name, partner.partner_type_id] for partner in Partner.query.filter_by(partner_type_id=0).all()]
    return partners

def get_activities_list():
    activities = [[0, "--", "--"]] + [[activity.id, str(activity.id).zfill(4) + " - " + activity.sales_person.name] for activity in Activity.query.all()]
    return activities

def update_count_service_tickets():
    """Armazena em variável de sessão o número de chamados que estejam pendentes, com os seguintes status:
        0 - Criado
        1 - Atrasado
        2 - Pendente de Parceiro
        3 - Pendente de Cliente
    """
    count_service_tickets = db.session.execute('select count(id) as c from Service_Ticket where id_status < 4').scalar()
    session["count_service_tickets"] = count_service_tickets if count_service_tickets > 0 else ""
    return 

def update_count_activities():
    """Armazena na variável de sessão o número de atividades que estejam pendentes, com os seguintes status:
        0 - Criado
        1 - Atrasado
        2 - Pendente de Parceiro
        3 - Pendente de Cliente
    """
    count_activities = db.session.execute('select count(id) as c from Activity where id_status < 4').scalar()
    session["count_activities"] =  count_activities if count_activities > 0 else ""
    return

def update_user_info(name, id):
    """Armazena Nome e Perfil de Acesso do Usuario"""
    session["user_name"] = name
    session["user_role"] = id
    return