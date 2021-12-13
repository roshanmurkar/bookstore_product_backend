from email.policy import default

from flask_sqlalchemy import SQLAlchemy
from auth.app import app
from flask_marshmallow import Marshmallow
import datetime
from sqlalchemy import Column, Integer, DateTime

db = SQLAlchemy(app)
ma = Marshmallow(app)
class InfoModel(db.Model):
    __tablename__ = 'registration'

    user_id = db.Column(db.Integer, primary_key=True)
    user_name= db.Column(db.String())
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    contact_number = db.Column(db.String())
    password = db.Column(db.String())
    email_address = db.Column(db.String())
    is_verified = db.Column(db.String())
    otp = db.Column(db.Integer)


    def __init__(self, user_name,first_name,last_name,contact_number,password,email_address):
        self.user_name = user_name
        self.first_name = first_name
        self.last_name = last_name
        self.contact_number = contact_number
        self.password = password
        self.email_address = email_address

    def __repr__(self):
        return f"{self.user_name}:{self.first_name}:{self.last_name}:{self.contact_number}:{self.password}:{self.email_address}"

class InfoModelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InfoModel
        load_instance = True

class BookProduct(db.Model):
    __tablename__ = 'product'

    product_id = db.Column(db.Integer, primary_key=True)
    author= db.Column(db.String())
    title = db.Column(db.String())
    baseprice = db.Column(db.Integer())
    description = db.Column(db.String())
    quantity = db.Column(db.Integer)

    def __init__(self, author,title,baseprice,description,quantity):
        self.author = author
        self.title = title
        self.baseprice = baseprice
        self.description = description
        self.quantity =quantity

    def __repr__(self):
        return f"{self.author}:{self.title}:{self.baseprice}:{self.description}:{self.quantity}"

class BookProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BookProduct
        load_instance = True

class Carts(db.Model):
    __tablename__ = 'carts'

    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer())
    # timestamp = DateTime(default=datetime.datetime.utcnow)
    # time_stamp = db.Column(DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(),default='not ordered')

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        # dictionary = {"uid":self.uid}
        # return dictionary
        return f"{self.user_id}"

class CartsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Carts
        load_instance = True

class CartItems(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer,db.ForeignKey('carts.cart_id'))
    book_id = db.Column(db.Integer,db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer)
    # time_stamp = db.Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    def __init__(self,cart_id,book_id,quantity):
        self.cart_id = cart_id
        self.book_id = book_id
        self.quantity = quantity

    def __repr__(self):
        return f"{self.cart_id}:{self.book_id}:{self.quantity}"

class CartItemsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CartItems
        load_instance = True


class Orders(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('registration.user_id'))
    # time_stamp = db.Column(DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(), default='in queue')

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        # dictionary = {"uid":self.uid}
        # return dictionary
        return f"{self.user_id}"

class OrdersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        load_instance = True


class OrderItems(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer,db.ForeignKey('orders.order_id'))
    book_id = db.Column(db.Integer,db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer)

    def __init__(self,order_id,book_id,quantity):
        self.order_id = order_id
        self.book_id = book_id
        self.quantity = quantity


    def __repr__(self):
        return f"{self.order_id}:{self.book_id}:{self.quantity}"

class OrderItemsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderItems
        load_instance = True


# create table registration (user_id serial primary key,user_name varchar(30) not null,first_name varchar(20) not null,last_name varchar(20) not null,contact_number varchar(12) not null, password varchar(20) not null,email_address varchar(30) not null,is_verified varchar(10),otp int)
# CREATE TABLE product(product_id serial primary key, author varchar(50) not null, title varchar(50) not null,baseprice int not null,description varchar(250) not null,quantity int not null );
# create table cart_items (id serial primary key,cart_id int not null,book_id int not null,quantity int not null,time_stamp timestamp default current_timestamp,foreign key(cart_id) references carts (cart_id),foreign key(book_id) references product(product_id));
# create table carts (cart_id serial primary key,user_id int not null,time_stamp timestamp default current_timestamp,status varchar(20) default('not ordered'));
# create table orders (order_id serial primary key,cart_id int not null,time_stamp timestamp default current_timestamp,foreign key(cart_id) references carts (cart_id));
# create table order_items (id serial primary key,cart_id int not null,book_id int not null,foreign key(cart_id) references carts(cart_id),foreign key(book_id) references product(product_id));


