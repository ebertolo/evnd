from app import db

MESSAGES = { 
    'default': 'Hello to the World of Flask!', 
} 


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
