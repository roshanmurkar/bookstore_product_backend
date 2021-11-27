from flask_sqlalchemy import SQLAlchemy
from auth.app import app
from flask_marshmallow import Marshmallow


db = SQLAlchemy(app)
ma = Marshmallow(app)
class InfoModel(db.Model):
    __tablename__ = 'userregistration'

    uid = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String())
    firstname = db.Column(db.String())
    lastname = db.Column(db.String())
    contactnumber = db.Column(db.String())
    password = db.Column(db.String())
    emailaddress = db.Column(db.String())
    is_verified = db.Column(db.String())
    otp = db.Column(db.Integer)


    def __init__(self, username,firstname,lastname,contactnumber,password,emailaddress):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.contactnumber = contactnumber
        self.password = password
        self.emailaddress = emailaddress

    def __repr__(self):
        return f"{self.username}:{self.firstname}:{self.lastname}:{self.contactnumber}:{self.password}:{self.emailaddress}"

class InfoModelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InfoModel
        load_instance = True

class BookProduct(db.Model):
    __tablename__ = 'product'

    pid = db.Column(db.Integer, primary_key=True)
    author= db.Column(db.String())
    title = db.Column(db.String())
    baseprice = db.Column(db.Integer())
    description = db.Column(db.String())

    def __init__(self, author,title,baseprice,description):
        self.author = author
        self.title = title
        self.baseprice = baseprice
        self.description = description

    def __repr__(self):
        return f"{self.author}:{self.title}:{self.baseprice}:{self.description}"

class BookProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BookProduct
        load_instance = True

class Orders(db.Model):
    __tablename__ = 'orders'

    cart_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer())
    username = db.Column(db.String())

    def __init__(self, uid,username):
        self.uid = uid
        self.username = username

    def __repr__(self):
        return f"{self.uid}:{self.username}"

class OrdersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        load_instance = True

class Carts(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer,db.ForeignKey('orders.cart_id'))
    bookname = db.Column(db.String())
    authorname = db.Column(db.String())
    price = db.Column(db.Integer())

    def __init__(self,cart_id,bookname,authorname,price):
        self.cart_id = cart_id
        self.bookname = bookname
        self.authorname = authorname
        self.price = price

    def __repr__(self):
        return f"{self.cart_id}:{self.bookname}:{self.authorname}:{self.price}"

class CartsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Carts
        load_instance = True



# CREATE TABLE product(pid serial primary key, author varchar(50) not null, title varchar(50) not null,baseprice int not null,description varchar(250) not null);
# create table buybook (bid serial primary key,bookname varchar(30) not null,bookauthor varchar(30) not null,price int not null);
# create table carts (id serial primary key,cart_id int not null,bookname varchar(50) not null,authorname varchar(50) not null,price int not null,foreign key(cart_id) references orders (cart_id));
# create table orders (cart_id serial primary key,uid int not null,username varchar(30) not null);