from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class Product(db.Model):
    """ Model Produto """

    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)
    info = db.Column(db.String(500))
    html_link = db.Column(db.String(250), nullable=True)
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
    """ Model Equipe de Vendas """

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



class Customer(db.Model):
    """ Model Cliente """

    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)
    tax_id = db.Column(db.String(20), unique=True)
    customer_type_id = db.Column(db.Integer) # Adicionar relacionamento como chave extrangeira
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(15))
    contact_email = db.Column(db.String(100), unique=True)
    address_line1 = db.Column(db.String(100), nullable=True)
    address_line2 = db.Column(db.String(100), nullable=True)
    number = db.Column(db.String(10), nullable=True)
    postal_code = db.Column(db.String(10), nullable=True)
    city =  db.Column(db.String(100), nullable=True)
    state =  db.Column(db.String(2), nullable=True)

    def __init__(self, name, tax_id, customer_type_id,
                    contact_name, contact_phone, contact_email, 
                    address_line1, address_line2, number, postal_code, city, state):
        self.name = name
        self.tax_id = tax_id # CNPJ Do Cliente
        self.customer_type_id = customer_type_id
        self.contact_name = contact_name
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.number = number
        self.postal_code = postal_code
        self.city = city
        self.state = state
        
    def __repr__(self):
        return "<Customer %r>" % self.name



class Activity(db.Model):
    """ Model Ativididades"""

    __tablename__ = "activity"
    id = db.Column(db.Integer, primary_key=True)
    id_status = db.Column(db.Integer)
    id_activity_type = db.Column(db.String(50), unique=True)
    id_customer = db.Column(db.Integer, nullable=True)
    id_sales_person = db.Column(db.Integer)
    id_product = db.Column(db.Integer, nullable=True)
    planned_date = db.Column(db.DateTime)
    done_date = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String(500))

    def __init__(self, id_status, id_activity_type, id_customer, id_sales_person, id_product, planned_date, done_date, description):
        self.id_status = id_status
        self.id_activity_type = id_activity_type
        self.id_customer = id_customer
        self.id_sales_person = id_sales_person
        self.id_product = id_product 
        self.planned_date = planned_date
        self.done_date = done_date
        self.description = description

    def __repr__(self):
        return "<Activity %r>" % self.name



class Partner(db.Model):
    """ Model Parceiros - Fornecedores, Assistencia Tecnica"""

    __tablename__ = "partner"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(15))
    contact_email = db.Column(db.String(100), unique=True)
    tax_id = db.Column(db.String(20), unique=True)
    partner_type_id = db.Column(db.Integer) # Adicionar relacionamento como chave extrangeira no futuro

    def __init__(self, name, contact_name, contact_phone, contact_email, tax_id, partner_type_id):
        self.name = name
        self.contact_name = contact_name
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.tax_id = tax_id
        self.partner_type_id = partner_type_id
        
    def __repr__(self):
        return "<Partner %r>" % self.name



class ServiceTicket(db.Model):
    """ Model Chamados """

    __tablename__ = "service_ticket"
    id = db.Column(db.Integer, primary_key=True)
    id_status = db.Column(db.Integer)
    id_customer = db.Column(db.Integer)          #adicionar relacionamento de chave estrangeira
    id_product = db.Column(db.Integer, nullable=True)   #adicionar relacionamento fraco de chave estrangeira
    id_activity = db.Column(db.Integer, nullable=True)  #adicionar relacionamento fraco de chave estrangeira    
    request_date = db.Column(db.DateTime)
    done_date = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String(500))
    
    def __init__(self):
        self.name = name
                
    def __repr__(self):
        return "<ServiceTicket %r>" % self.name



class User(UserMixin, db.Model):
    """ Model Autenticação """

    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    short_name = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False, index=True)
    access_date = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, email,  password, short_name, full_name):

        self.email = email
        self.password = password
        self.short_name = short_name
        self.full_name = full_name
        self.access_date = datetime.now()
                
    @property
    def password(self):
        raise AttributeError('Password não é um atributo de leitura.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # def get_id(self):
    #     return self

    # def is_active(self):
    #     return True

    # def is_anonymous(self):
    #     return False

    # def is_authenticated(self):
    #     return True

    def __repr__(self):
        return "<Authentication %r>" % self.name