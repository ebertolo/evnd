#/usr/bin/python3
import re
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


""" _________________________________________________________________________________________________
    Classes a serem persistidas como tabelas através do SQLAlchemy, ORM para o Python e Flask
""" 
class Role(db.Model):
    """Model Perfil de Acesso"""
    
    __tablename__ = "Role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users =  db.relationship("User", back_populates="role")

    def __init__(self, name):
        """Método Construtor da Classe"""
        self.name = name
    
    def __repr__(self):
        """Retorna o nome da classe"""
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    """Model Autenticação"""

    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    id_role = db.Column(db.Integer, db.ForeignKey("Role.id"))
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(50), unique=True, index=True)
    short_name = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False, index=True)
    access_date = db.Column(db.DateTime, nullable=True)
    role = db.relationship("Role", back_populates="users")
    
    def __init__(self, email,  password, short_name, full_name, id_role):
        """Método Construtor da Classe"""
        self.email = email
        self.password = password
        self.short_name = short_name
        self.full_name = full_name
        self.access_date = datetime.now()
        self.id_role = id_role
    
    @property
    def password(self):
        """Propriedade Bloqueada para Leitura"""
        raise AttributeError('Password não é um atributo de leitura.')

    @password.setter
    def password(self, password):
        """Método de edição de Propriedade Protegida para Leitura"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Utiliza biblioteca de conversao de hash, para validar senha"""
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        """Método que retorna ID do usuario logado."""
        return User.query.get(int(user_id))

    def __repr__(self):
        return "<User %r>" % self.short_name


class Customer(db.Model):
    """Model Cliente"""

    __tablename__ = "Customer"
    id = db.Column(db.Integer, primary_key=True)
    tax_id = db.Column(db.String(20), unique=True)
    customer_type_id = db.Column(db.Integer) # TODO// Adicionar relacionamento como chave extrangeira
    name = db.Column(db.String(100), unique=True, index=True)
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(15))
    contact_email = db.Column(db.String(100), unique=True)
    address_line1 = db.Column(db.String(100), nullable=True)
    address_line2 = db.Column(db.String(100), nullable=True)
    number = db.Column(db.String(10), nullable=True)
    postal_code = db.Column(db.String(10), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(2), nullable=True)
    service_tickets = db.relationship("ServiceTicket", back_populates="customer")
    activities = db.relationship("Activity", back_populates="customer")

    def __init__(self, tax_id, customer_type_id, name,
                    contact_name, contact_phone, contact_email, 
                    address_line1, address_line2, number, postal_code, city, state):
        """Método Construtor da Classe"""
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
        """String padrão que descreve o objeto"""
        return "<Customer %r>" % self.name


class Product(db.Model):
    """Model Produto"""

    __tablename__ = "Product"
    id = db.Column(db.Integer, primary_key=True)
    code =  db.Column(db.String(100)) #Codigo do Fornecedor
    name = db.Column(db.String(100), unique=True, index=True)
    info = db.Column(db.String(500))  #Descricao do Produto
    html_link = db.Column(db.String(250), nullable=True)
    group_name_short = db.Column(db.String(30))
    group_name_long = db.Column(db.String(100))

    def __init__(self, code, name, info, html_link, group_name_short, group_name_long):
        """Método Construtor da Classe"""
        self.code = code 
        self.name = name
        self.info = info
        self.html_link = html_link
        self.group_name_short = group_name_short
        self.group_name_long = group_name_long

    def __repr__(self):
        """String padrão que descreve o objeto"""
        return "<Product %r>" % self.name


class SalesPerson(db.Model):
    """Model Equipe de Vendas"""

    __tablename__ = "Sales_Person"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True)
    activities =  db.relationship("Activity", back_populates="sales_person")

    def __init__(self, name, phone, email):
        """Método Construtor da Classe"""
        self.name = name
        self.phone = phone 
        self.email = email

    def __repr__(self):
        """String padrão que descreve o objeto"""
        return "<SalesPerson %r>" % self.name


class Partner(db.Model):
    """Model Parceiros - Fornecedores, Assistencia Tecnica"""

    __tablename__ = "Partner"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True)
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(15))
    contact_email = db.Column(db.String(100), unique=True)
    tax_id = db.Column(db.String(20), unique=True)
    partner_type_id = db.Column(db.Integer) # TODO: Adicionar relacionamento como chave extrangeira no futuro

    def __init__(self, name, contact_name, contact_phone, contact_email, tax_id, partner_type_id):
        """Método Construtor"""
        self.name = name
        self.contact_name = contact_name
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.tax_id = tax_id
        self.partner_type_id = partner_type_id
        
    def __repr__(self):
        """String padrão que descreve o objeto"""
        return "<Partner %r>" % self.name


class ServiceTicket(db.Model):
    """Model Chamados"""

    __tablename__ = "Service_Ticket"
    id = db.Column(db.Integer, primary_key=True)
    id_status = db.Column(db.Integer)
    id_customer = db.Column(db.Integer, db.ForeignKey("Customer.id"))        
    id_product = db.Column(db.Integer, nullable=True)   # Relacionamento fraco, nao usar chave estrangeira
    id_activity = db.Column(db.Integer, nullable=True)  # Relacionamento fraco, nao usar chave estrangeira
    id_partner = db.Column(db.Integer, nullable=True) # Relacionamento fraco, nao usar chave estrangeira
    request_date = db.Column(db.DateTime)
    done_date = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String(500))
    customer = db.relationship("Customer", back_populates="service_tickets")
    
    def __init__(self, id_status, id_customer, id_product, id_activity, id_partner, request_date, done_date, description):
        """Método Construtor da Classe"""
        self.id_status = id_status
        self.id_customer = id_customer
        self.id_product = id_product
        self.id_activity = id_activity
        self.id_partner = id_partner
        self.request_date = request_date 
        self.done_date = done_date
        self.description = description
                
    def __repr__(self):
        return "<ServiceTicket %r>" % str(self.id)


class Activity(db.Model):
    """Model Ativididades"""

    __tablename__ = "Activity"
    id = db.Column(db.Integer, primary_key=True)
    id_status = db.Column(db.Integer)
    id_activity_type = db.Column(db.Integer)
    id_customer = db.Column(db.Integer, db.ForeignKey("Customer.id"))
    id_sales_person = db.Column(db.Integer, db.ForeignKey("Sales_Person.id"))
    id_product = db.Column(db.Integer, nullable=True)
    planned_date = db.Column(db.DateTime)
    done_date = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String(500))
    sales_person = db.relationship("SalesPerson", back_populates="activities")
    customer = db.relationship("Customer", back_populates="activities")

    def __init__(self, id_status, id_activity_type, id_customer, id_sales_person, id_product, planned_date, done_date, description):
        """Método Construtor da Classe"""
        self.id_status = id_status
        self.id_activity_type = id_activity_type
        self.id_customer = id_customer
        self.id_sales_person = id_sales_person
        self.id_product = id_product 
        self.planned_date = planned_date
        self.done_date = done_date
        self.description = description

    def __repr__(self):
        return "<Activity %r>" % str(self.id)



""" _________________________________________________________________________________________________
    Tabelas a serem mantidas apenas na Memória no formato de listas10
""" 
def get_states():
    """Retorna lista de estados do pais com suas siglas"""

    states = [
        ["SC", "Santa Catarina"],
        ["RS", "Rio Grande do Sul"],
        ["PR", "Paraná"],

        ["RJ", "Rio de Janeiro"],
        ["SP", "São Paulo"],
        ["MG", "Bahia"],
        ["ES", "Espírito Santo"],

        ["AM", "Amazonas"],
        ["RR", "Roraima"],
        ["RO", "Rondônia"],
        ["AP", "Amapá"],
        ["PA", "Pará"],
        ["AC", "Acre"],
        ["TO", "Tocantins"],

        ["BA", "Bahia"],
        ["CE", "Ceará"],
        ["RN", "Rio Grande do Norte"],
        ["AL", "Alagoas"],
        ["PI", "Piaui"],
        ["MA", "Maranhão"],
        ["PB", "Paraíba"],
        ["PE", "Pernambuco"],
        ["SE", "Sergipe"],

        ["MT", "Mato Grosso"],
        ["MS", "Mato Grosso do Sul"],
        ["DF", "Distrito Federal"],
        ["GO", "Goiás"],
    ]
    states.sort()
    return states

def get_customer_types():
    customer_types = [
        [1,"Lead/Prospect"], 
        [2, "Cliente Ativo"], 
        [3, "Cliente Vip"],

    ]
    return customer_types

def get_partner_types():
    partner_types = [
        [0, "Assistência Técnica"], 
        [1, "Fornecedor"], 
        [2, "Representante"],
    ]
    return partner_types

def get_service_ticket_status():
    service_ticket_status = [
        [0, "Criado"], 
        [1, "Atrasada"], 
        [2, "Pendente de Parceiro"],
        [3, "Pendente do Cliente"],
        [4, "Executando"],
        [5, "Concluída"],
    ]
    return service_ticket_status

def get_activity_types():
    activity_types = [
        ["0", "Telefonema"], 
        ["1", "Reunião"], 
        ["2", "Visita"],
        ["3", "Oferta"],
        ["4", "Email"],
    ]
    return activity_types

def get_activity_status():
    activity_status = [
        [0, "Agendada"], 
        [1, "Atrasada"], 
        [2, "Pendente de Parceiro"],
        [3, "Pendente do Cliente"],
        [4, "Executando"],
        [5, "Concluída"],
    ]
    return activity_status

""" _________________________________________________________________________________________________
    Funções Auxiliares para conversão e formatação de dados
""" 
def convert_to_date(str_date):
    """Converte uma string para o formato datetime python suportado pelo SQLAlchemy"""
    return datetime.strptime(str_date, "%d/%m/%Y")