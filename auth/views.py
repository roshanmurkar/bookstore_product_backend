import datetime
import json
import jwt
import re
import pyotp
from flask import jsonify, request
from flask_mail import *
from auth.exceptions import *
from auth.app import app, mail
from auth.models import db, InfoModel, InfoModelSchema,BookProduct,BookProductSchema,Orders,OrdersSchema,CartsSchema,Carts
import logging
from io import TextIOWrapper

logging.basicConfig(filename="bookstore_otp.log", filemode="w",datefmt='%Y-%m-%d,%H:%M:%S:%f')
log = logging.getLogger()

# registration= Blueprint("registration",__name__)
with open('config.json','r') as f:
    params = json.load(f)['host_mail']


@app.route('/registration',methods=['POST'])
def register():
    """
    This function will take all require fields for user registration
    :return: Status of User Registration
    """
    user_data = request.get_json()
    username = user_data['username']
    firstname = user_data['firstname']
    lastname = user_data['lastname']
    contactnumber = user_data['contactnumber']
    password = user_data['password']
    emailaddress = user_data['emailaddress']

    try:
        special_symbol = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        email_pattern = re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if len(username) == 0 or len(firstname) == 0 or len(lastname) == 0 or \
                len(contactnumber) == 0 or len(password) == 0 or len(emailaddress) == 0:
            raise EmptyData
        elif not contactnumber.isnumeric():
            raise InvalidNumericData
        elif firstname.isdigit() or lastname.isdigit():
            raise InvalidStringData
        elif not special_symbol.search(firstname) is None or not special_symbol.search(lastname) is None:
            raise SpecialCharacterError
        elif email_pattern.search(emailaddress) is None:
            raise InvalidEmailAddress
        user = InfoModel.query.filter_by(username=user_data['username']).first()
        if user is None:
            new_user = InfoModel(username, firstname, lastname, contactnumber, password, emailaddress)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "New User registration successful", "data": user_data})
        else:
            return jsonify({"message": "UserName is already Registered","Data":user_data})
    except EmptyData:
        return jsonify({"message": "Empty data is not allowed","Data":user_data})
    except InvalidNumericData:
        return jsonify({"message": "Contact number should be in numeric","Data":contactnumber})
    except InvalidStringData:
        return jsonify({"message":"FirstName and LastName should be in String","Data":user_data})
    except SpecialCharacterError:
        return jsonify({"message":"Don't use Special letters in FirstName and LastName","Data":user_data})
    except InvalidEmailAddress:
        return jsonify({"message":"Invalid Email address","Data":emailaddress})
    except Exception as e:
        return jsonify({"message":str(e)})

# details= Blueprint("details",__name__)

@app.route('/details',methods=['GET'])
def details():
    info_model = InfoModel.query.all()
    info_model_schema = InfoModelSchema(many=True)
    output = info_model_schema.dump(info_model)
    return jsonify({"message":"All User Registrations","details": output})


# login= Blueprint("login",__name__)

@app.route('/login',methods=['POST'])
def login():
    """
    This function will take username and password as a input from user
    and it will compare with database all entries
    if the match is found then it will return login successful or unsuccessful
    :return: message of login successful or unsuccessful with user data
    """
    user_data = request.get_json()
    try:
        if len(user_data['username']) == 0 or len(user_data['password']) == 0:
            raise EmptyData
        user = InfoModel.query.filter_by(username=user_data['username'],password=user_data['password']).first()
        if user.is_verified == 'YES':
            if user.password == str(user_data['password']):
                encoded_jwt = jwt.encode({"uid": user.uid}, "secret", algorithm="HS256")
                return jsonify({"message": f"User Login Successful... Welcome {user.username}", "token": encoded_jwt})
        else:
            return jsonify({"message":"User Email is Not Verified","Data":user.emailaddress})
    except EmptyData:
        return jsonify({"message": "Empty data is not allowed","Data":user_data})
    except Exception as e:
        return jsonify({"message":str(e)})

@app.route('/verify',methods=['POST','GET'])
def verify():
    """
    This function will take user email as a input for email verification
    and after that it will send OTP to that email address for validation purpose
    :return: It will send message and Email of user
    """
    email = request.get_json()
    try:
        if len(email['email']) == 0:
            raise EmptyData
        user = InfoModel.query.filter_by(emailaddress=email['email']).first()
        if user.is_verified == 'YES':
            return jsonify({"message":"This User mail is already verified","Data":email})
        else:
            otp = pyotp.TOTP('base32secret3232')
            system_otp = otp.now()
            print(system_otp)
            time.sleep(1)
            log.warning(f"{system_otp} OTP is created for user {user.username} with {user.emailaddress} "
                        f"email address at {datetime.datetime.now()}")
            user.otp = system_otp
            db.session.commit()
            message = Message('OTP for verification',sender=params['gmail_user'],recipients=[email['email']])
            message.body = f"Enter this - {str(system_otp)} - OTP for your EMAIL verification ! THANK YOU :)"
            mail.send(message)
            return jsonify({"message":"OTP is send on given mail address","data":email})
    except EmptyData:
        return jsonify({"message": "Empty data is not allowed","Data":email})
    except Exception as e:
        return jsonify({"message":str(e)})

@app.route('/verify/validate',methods=['POST'])
def validate():
    """
    This function will take user email and verification OTP as a input
    and then it will match user OTP and system OTP if the match is found
    then it will return verified email address with user id token
    :return: whether the email is verified por not if the email is verified
            then it send user token also.
    """
    user_data = request.get_json()
    try:
        if len(user_data['otp']) != 6:
            raise InvalidSize
        elif not user_data['otp'].isnumeric():
            raise InvalidNumericData
        user = InfoModel.query.filter_by(emailaddress=user_data['email']).first()
        if user.otp == int(user_data['otp']):
            # user = InfoModel.query.filter_by(emailaddress=user_data['email']).first()
            user.is_verified = 'YES'
            user.otp = 0
            db.session.commit()
            encoded_jwt = jwt.encode({"uid":user.uid}, "secret", algorithm="HS256")
            return jsonify({"message":"Email verification successfully","token":encoded_jwt})
        return jsonify({"message":"Due to Invalid OTP , Email verification is unsuccessful"})
    except InvalidSize:
        return jsonify({"message":"OTP size is Invalid","Data":user_data})
    except InvalidNumericData:
        return jsonify({"message":"OTP should be in numeric","Data":user_data})
    except Exception as e:
        return jsonify({"message":str(e)})

@app.route('/buybook',methods=['POST'])
def buy_book():
    # First decoding the token
    auth = request.headers.get('authorization')
    id = jwt.decode(auth, "secret", algorithms=["HS256"])
    user = InfoModel.query.filter_by(uid=id['uid']).first()
    # Taking book name as a input
    user_data = request.get_json()
    book_name = user_data['bookname']
    # Finding user entered book is present or not in over product table
    book_details = BookProduct.query.filter_by(title=book_name).first()
    if book_details is None:
        return jsonify({"message":f"No Book is present with name {book_name}"})
    # checking cart is already created for that user.
    cart = Orders.query.filter_by(uid=user.uid).first()
    if cart is None:
        # If cart is not created it will create new cart for that user
        new_cart = Orders(user.uid,user.username)
        db.session.add(new_cart)
        db.session.commit()
        # now adding that book details in users cart.
        add_book_in_cart = Carts(cart.cart_id, book_details.title, book_details.author, book_details.baseprice)
        db.session.add(add_book_in_cart)
        db.session.commit()
        return jsonify({"message":"new cart is created and your book is added in your cart"})
    else:
        # Checking book is already present in a cart or not
        book_name = Carts.query.filter_by(bookname=book_name).first()
        if book_name is None:
            # cart is already created so new book is add in existing cart.
            add_book_in_cart = Carts(cart.cart_id,book_details.title,book_details.author,book_details.baseprice)
            db.session.add(add_book_in_cart)
            db.session.commit()
            return jsonify({"message":"cart is already created and your book is added in your cart"})
        else:
            # If book is already in cart then it will return msg.
            return jsonify({"message":"book is already in cart ! Thank You :)"})
    return user.username


if __name__ == '__main__':
    app.run(debug=True)