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
from flask.views import MethodView



# registration= Blueprint("registration",__name__)
with open('config.json', 'r') as f:
    params = json.load(f)['host_mail']

book_coordinates = BookCoordinates()
token_operation = TokenOperation()
verification_coordinate= VerificationCoordinate()
book_operation = BookOperation()



class UserRegistration(MethodView):
    def post(self):
        try:
            user_data = request.get_json()
            validation = user_validation(user_data)
            if validation is not True:
                print(validation.get_json())
                return jsonify(validation.get_json())
            check_username = check_user(user_data['user_name'])
            if check_username is False:
                # new_registration = new_user_registration(user_data)
                new_user_registration(user_data)
                return jsonify({"message": "New User registration successful", "data": user_data})
        except Exception as e:
            log.exception(e.__str__())
            return jsonify({"message": "Something is wrong"})



class Verify(MethodView):
    def post(self):
        """
            This function will take user email as a input for email verification
            and after that it will send OTP to that email address for validation purpose
            :return: It will send message and Email of user
            """
        try:
            email = request.get_json()
            if len(email['email']) == 0:
                raise EmptyData
            email_status_check = check_mail_status(email)
            if email_status_check is True:
                return jsonify({"message": "This User mail is already verified", "Data": email})
            verification_coordinate.mail_for_verification(email_status_check)
            if True:
                return jsonify({"message": "OTP is send on given mail address", "data": email})
        except EmptyData:
            return jsonify({"message": "Empty data is not allowed", "Data": email})
        except Exception as e:
            log.exception(e.__str__())
            return jsonify({"message": "Something is wrong"})



class Validate(MethodView):
    def post(self):
        """
            This function will take user email and verification OTP as a input
            and then it will match user OTP and system OTP if the match is found
            then it will return verified email address with user id token
            :return: whether the email is verified por not if the email is verified
                    then it send user token also.
            """
        try:
            user_data = request.get_json()
            if len(user_data['otp']) != 6:
                raise InvalidSize
            elif not user_data['otp'].isnumeric():
                raise InvalidNumericData
            user = verification_coordinate.validate_mail(user_data['email'],user_data['otp'])
            if user is False:
                return jsonify({"message": "Due to Invalid Email or OTP , Email verification is unsuccessful"})
            create_token = token_operation.encode_token(user.user_id)
            return jsonify({"message": "Email verification successfully", "token": create_token})
        except InvalidSize:
            return jsonify({"message": "OTP size is Invalid", "Data": user_data})
        except InvalidNumericData:
            return jsonify({"message": "OTP should be in numeric", "Data": user_data})
        except Exception as e:
            log.exception(e.__str__())
            return jsonify({"message": "Something is Wrong"})



class UserLogin(MethodView):
    def post(self):
        """
            This function will take username and password as a input from user
            and it will compare with database all entries
            if the match is found then it will return login successful or unsuccessful
            :return: message of login successful or unsuccessful with user data
            """
        try:
            user_data = request.get_json()
            if len(user_data['user_name']) == 0 or len(user_data['password']) == 0:
                raise EmptyData
            user = InfoModel.query.filter_by(user_name=user_data['user_name'], password=user_data['password']).first()
            if user.is_verified == 'YES':
                if user.password == str(user_data['password']):
                    encoded_jwt = jwt.encode({"user_id": user.user_id}, "secret", algorithm="HS256")
                    return jsonify(
                        {"message": f"User Login Successful... Welcome {user.user_name}", "token": encoded_jwt})
            else:
                return jsonify({"message": "User Email is Not Verified", "Data": user.email_address})
        except EmptyData:
            return jsonify({"message": "Empty data is not allowed", "Data": user_data})
        except Exception as e:
            return jsonify({"message": str(e)})



class AddBook(MethodView):
    def post(self):
        """
            In this function we are adding particular book in our database
            :return: status of book is added or not
        """
        try:
            request_data = request.get_json()
            if request_data['author_name'].isnumeric or request_data['title'].isnumeric:
                raise InvalidStringData
            book = BookProduct.query.filter_by(author=request_data['author_name'], title=request_data['title']).first()
            if book is not None:
                book.quantity = int(book.quantity) + int(request_data['quantity'])
                db.session.commit()
                return jsonify({"message": "Book Quantity is updated"})
            # new_book = add_book(request_data)
            book_operation.add_book(request_data)
            return jsonify({"message": "New book is added."})
        except InvalidStringData:
            log.exception("Invalid String data")
            return jsonify({"message": "Invalid Data"})
        except Exception as e:
            log.exception(e.__str__())
            return jsonify({"message": "Something is wrong"})



class Books(MethodView):
    def get(self):
        """
            this function for displaying all books
            :return:
        """
        try:
            all_books = book_operation.get_all_books()
            return jsonify({"message": "All Books Details", "details": all_books})
        except Exception as e:
            log.exception(e.__str__())
            return jsonify({"message": "Something is wrong"})



class SingleCart(MethodView):
    def get(self):
        """
            this function to see particular card details by passing its cart_id
            :return: particular cart details
            """
        try:
            request_data = request.get_json()
            if not request_data['cart_id'].isnumeric:
                raise InvalidNumericData
            cart_data = check_cart_items(request_data['cart_id'])
            if len(cart_data) == 0:
                return jsonify({"message": "Cart is not found"})
            cart_details = get_particular_cart_details(cart_data)
            return jsonify({"message": "successful", "data": cart_details})
        except InvalidNumericData:
            log.exception("Cart_id should be numeric data")
            return jsonify({"message": "Cart_id should be numeric data"})
        except Exception as e:
            log.exception(e.__str__())
            return jsonify({"message": "Something is wrong"})



class BuyBook(MethodView):
    def post(self):
        """
            this function for buying particular cart using cart_id
            :return: email and response
        """
        try:
            auth = request.headers.get('authorization')
            user = token_operation.decode_token(auth)
            if user is None:
                raise InvalidToken
            request_data = request.get_json()
            cart_check = check_cart(request_data['cart_id'])
            if cart_check is None:
                return jsonify({"message": "Cart is not found"})
            generate_new_order(cart_check.user_id)
            cart_check.status = 'Ordered'
            db.session.commit()
            add_books_in_order_items(user.user_id, request_data['cart_id'])
            order_items = generate_order_items_list(user.user_id)
            total_bill = generate_total_bill(order_items)
            data_in_table_form = generate_order_table(order_items)
            user_email = user.email_address
            message = generate_bill_message(user_email,data_in_table_form,total_bill)
            mail.send(message)
            print(data_in_table_form)
            return jsonify({"message": "Ordered Successful. Please check mail for order details. Thank You :)",
                            "data": order_items})
        except InvalidToken:
            log.exception("Token is invalid")
            return jsonify({"message": "Token is invalid"})
        except Exception as e:
            log.exception(e.__str__())
            return jsonify({"message": "something is wrong"})



class UploadBooks(MethodView):
    def post(self):
        """
            in this function we are adding whole csv file of books in our database
            :return: status of csv file is uploaded or not
        """
        try:
            csv_file = request.files['file']
            df_csv = pd.read_csv(csv_file, delimiter=',')
            for index, row in df_csv.iterrows():
                author = row['author']
                title = row['title']
                baseprice = row['baseprice']
                description = row['description']
                quantity = row['quantity']
                query = BookProduct(author=author, title=title, baseprice=baseprice, description=description,
                                            quantity=quantity)
                db.session.add(query)
                db.session.commit()
                return jsonify({"message": "CSV file uploaded successfully"})
        except Exception as e:
            log.exception(e.__str__())
            return jsonify({"message": "Something is wrong"})



class AddBookInCart(MethodView):
    def post(self):
        try:
            auth = request.headers.get('authorization')
            user = token_operation.decode_token(auth)
            request_data = request.get_json()
            book_details = book_coordinates.check_book_in_database(request_data['book_id'])
            if book_details is False:
                return jsonify({"message": f"No Book is present with book_id {request_data['book_id']}"})
            cart = check_cart_by_user_id(user.user_id)
            if cart is False:
                cart = create_new_cart(user.user_id)
            book_in_cart = check_book_in_cart(cart.cart_id,request_data['book_id'])
            if book_in_cart is not None:
                # update_quantity = update_book_quantity(book_in_cart,request_data['book_quantity'])
                update_book_quantity(book_in_cart,request_data['book_quantity'])
                return jsonify({"message": "Book Quantity is updated"})
            # new_book_in_cart = book_coordinates.add_new_book_in_cart(cart.cart_id,book_details.product_id,request_data['book_quantity'])
            book_coordinates.add_new_book_in_cart(cart.cart_id,book_details.product_id,request_data['book_quantity'])
            return jsonify({"message": "Your book is added in your cart"})
        except Exception as e:
            log.exception(e.__str__())
        return jsonify({"message": "something is wrong"})


app.add_url_rule('/upload_books', view_func=UploadBooks.as_view('upload_books'))
app.add_url_rule('/buy_book', view_func=BuyBook.as_view('buy_book'))
app.add_url_rule('/particular_cart_details', view_func=SingleCart.as_view('single_cart'))
app.add_url_rule('/books', view_func=Books.as_view('books'))
app.add_url_rule('/add_book', view_func=AddBook.as_view('add_book'))
app.add_url_rule('/add_book_in_cart', view_func=AddBookInCart.as_view('add_book_in_cart'))
app.add_url_rule('/login', view_func=UserLogin.as_view('user_login'))
app.add_url_rule('/registration', view_func=UserRegistration.as_view('user_registration'))
app.add_url_rule('/verify', view_func=Verify.as_view('verify'))
app.add_url_rule('/verify/validate', view_func=Validate.as_view('validate'))

if __name__ == '__main__':
    app.run(debug=True)
