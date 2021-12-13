from auth.app import app
from flask_migrate import Migrate
from models import db

import datetime
import json
from builtins import print
import pandas as pd
import jwt
import re
import pyotp
from flask import jsonify, request
from flask.typing import ResponseReturnValue
from flask_mail import *
from auth.exceptions import *
from auth.app import app, mail,log
from auth.models import *
import logging
from io import TextIOWrapper
from tabulate import tabulate
import csv
from utility import *
from flask.views import View

# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:root@localhost:5432/bookstore_product"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

with open('config.json', 'r') as f:
    params = json.load(f)['host_mail']


def user_validation(user_data):
    try:
        special_symbol = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        email_pattern = re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if len(user_data['user_name']) == 0 or len(user_data['first_name']) == 0 or len(user_data['last_name']) == 0 or \
                len(user_data['contact_number']) == 0 or len(user_data['password']) == 0 or len(user_data['email_address']) == 0:
            raise EmptyData
        elif not user_data['contact_number'].isnumeric():
            raise InvalidNumericData
        elif user_data['first_name'].isdigit() or user_data['last_name'].isdigit():
            raise InvalidStringData
        elif not special_symbol.search(user_data['first_name']) is None or not special_symbol.search(user_data['last_name']) is None:
            raise SpecialCharacterError
        elif email_pattern.search(user_data['email_address']) is None:
            raise InvalidEmailAddress
        return True
    except EmptyData:
        return jsonify({"message": "Empty data is not allowed"})
    except InvalidNumericData:
        return jsonify({"message": "Contact number should be in numeric"})
    except InvalidStringData:
        return jsonify({"message": "FirstName and LastName should be in String"})
    except SpecialCharacterError:
        return jsonify({"message": "Don't use Special letters in FirstName and LastName"})
    except InvalidEmailAddress:
        return jsonify({"message": "Invalid Email address"})

def check_user(user_name):
    user = InfoModel.query.filter_by(user_name=user_name).first()
    if user is None:
        return False
    return True

def check_mail_status(email):
    user = InfoModel.query.filter_by(email_address=email['email']).first()
    if user.is_verified == 'YES':
        return True
    return user

def new_user_registration(user_data):
    new_user = InfoModel(user_data['user_name'], user_data['first_name'], user_data['last_name'],
                         user_data['contact_number'], user_data['password'], user_data['email_address'])
    db.session.add(new_user)
    db.session.commit()
    info_model_schema = InfoModelSchema()
    data = info_model_schema.dump(new_user)
    return data




def generate_total_bill(order_items_list):
    billing_list = []
    for entry in order_items_list:
        billing_list.append(entry['baseprice'] * entry['quantity'])
    total_bill = sum(billing_list)
    return total_bill

def generate_order_items_list(user_id):
    order = Orders.query.filter_by(user_id=user_id, status='in queue').first()
    items = OrderItems.query.filter_by(order_id=order.order_id).all()
    order_items_list = []
    for order_item in items:
        data = BookProduct.query.join(OrderItems).with_entities(
            BookProduct.title, BookProduct.baseprice, OrderItems.quantity).filter_by(
            product_id=order_item.book_id).first()
        book_product_schema = BookProductSchema()
        order_items_list.append(book_product_schema.dump(data))
    order.status = 'confirm'
    db.session.commit()
    return order_items_list

def generate_order_table(order_items_list):
    header = order_items_list[0].keys()
    rows = [x.values() for x in order_items_list]
    data_in_table_form = tabulate(rows, header, tablefmt='grid')
    return data_in_table_form

def generate_bill_message(user_email,data_in_table_form,total_bill):
    message = Message('Your Order', sender=params['gmail_user'], recipients=[user_email])
    message.body = f"your books order details are \n" \
                   f"{data_in_table_form} \n" \
                   f"and total bill is -> {total_bill}"
    return message

def generate_new_order(user_id):
    order = Orders(user_id)
    db.session.add(order)
    db.session.commit()
    return None

def check_cart(cart_id):
    cart_check = Carts.query.filter_by(cart_id=cart_id).first()
    return cart_check

def check_cart_by_user_id(user_id):
    cart_check = Carts.query.filter_by(user_id=user_id, status='not ordered').first()
    if cart_check is None:
        return False
    return cart_check

def create_new_cart(user_id):
    new_cart = Carts(user_id)
    db.session.add(new_cart)
    db.session.commit()
    return new_cart

def check_book_in_cart(cart_id,book_id):
    book_in_cart = CartItems.query.filter_by(cart_id=cart_id, book_id=book_id).first()
    return book_in_cart

def update_book_quantity(book,new_quantity):
    book.quantity = int(book.quantity) + int(new_quantity)
    db.session.commit()
    return book




def check_cart_items(cart_id):
    cart_data = CartItems.query.filter_by(cart_id=cart_id).all()
    return cart_data

def get_particular_cart_details(cart_data):
    cart_details = []
    for data in cart_data:
        book = BookProduct.query.join(CartItems).with_entities(BookProduct.author,
                                                               BookProduct.title,
                                                               BookProduct.baseprice,
                                                               CartItems.quantity).filter_by(product_id=data.book_id).first()
        book_product_schema = BookProductSchema()
        cart_details.append(book_product_schema.dump(book))
    return cart_details



def add_books_in_order_items(user_id,cart_id):
    order = Orders.query.filter_by(user_id=user_id, status='in queue').first()
    cart_books = CartItems.query.filter_by(cart_id=cart_id).all()
    for book in cart_books:
        print("inside book in cart_books")
        order_items = OrderItems(order.order_id, book.book_id, book.quantity)
        db.session.add(order_items)
        db.session.commit()
    return None



class BookCoordinates:
    def check_book_in_database(self,book_id):
        book_details = BookProduct.query.filter_by(product_id=book_id).first()
        if book_details is None:
            return False
        return book_details

    def add_new_book_in_cart(self,cart_id,book_id,quantity):
        cart_book = CartItems(cart_id, book_id,quantity)
        db.session.add(cart_book)
        db.session.commit()
        return cart_book


class BookOperation:
    def add_book(self,book_data):
        new_book = BookProduct(book_data['author_name'], book_data['title'], book_data['baseprice'],
                               book_data['description'], book_data['quantity'])
        db.session.add(new_book)
        db.session.commit()
        return None

    def get_all_books(self):
        book_product = BookProduct.query.all()
        book_product_schema = BookProductSchema(many=True)
        all_books_details = book_product_schema.dump(book_product)
        return all_books_details



class TokenOperation:
    def decode_token(self,token):
        decoded_value = jwt.decode(token, "secret", algorithms=["HS256"])
        user = InfoModel.query.filter_by(user_id=decoded_value['user_id']).first()
        return user

    def encode_token(self,user_id):
        encoded_jwt = jwt.encode({"user_id": user_id}, "secret", algorithm="HS256")
        return encoded_jwt



class VerificationCoordinate:
    def generate_otp(self):
        otp = pyotp.TOTP('base32secret3232')
        system_otp = otp.now()
        print(system_otp)
        time.sleep(1)
        return system_otp

    def mail_for_verification(self,user):
        otp = generate_otp()
        log.warning(f"{otp} OTP is created for user {user.user_name} with {user.email_address} "
                    f"email address at {datetime.datetime.now()}")
        user.otp = otp
        db.session.commit()
        print(user.email_address)
        message = Message('OTP for verification', sender=params['gmail_user'], recipients=[user.email_address])
        message.body = f"Enter this - {str(otp)} - OTP for your EMAIL verification ! THANK YOU :)"
        mail.send(message)
        return True

    def validate_mail(self,email, otp):
        user = InfoModel.query.filter_by(email_address=email).first()
        if user is not None and user.otp == int(otp):
            user.is_verified = 'YES'
            user.otp = 0
            db.session.commit()
            return user
        return False