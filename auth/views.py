from flask_sqlalchemy import SQLAlchemy
from auth.models import db, InfoModel,InfoModelSchema
from flask import jsonify,request,Blueprint
from auth.app import app,otp,mail
import json
from flask_mail import *
import jwt

# registration= Blueprint("registration",__name__)
with open('config.json','r') as f:
    params = json.load(f)['host_mail']


@app.route('/registration',methods=['POST'])
def register():
    user_data = request.get_json()
    info_model = InfoModel.query.all()
    info_model_schema = InfoModelSchema(many=True)
    output = info_model_schema.dump(info_model)
    for user in output:
        if user['username'] == user_data['username'] and str(user['password']) == str(user_data['password']):
            return jsonify({"message": "User is already Register ! Thank you", "Data": user_data})

    username = user_data['username']
    firstname = user_data['firstname']
    lastname = user_data['lastname']
    contactnumber = user_data['contactnumber']
    password = user_data['password']
    emailaddress = user_data['emailaddress']

    new_user = InfoModel(username,firstname,lastname,contactnumber,password,emailaddress)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message":"New User registration successful","data":user_data})



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
    user_data = request.get_json()
    # info_model = InfoModel.query.all()
    # info_model_schema = InfoModelSchema(many=True)
    # output = info_model_schema.dump(info_model)
    # for user in output:
    #     if user['username'] == user_data['username'] and str(user['password']) == str(user_data['password']):
    #         return jsonify({"message":"User Login Successful","Data":user})
    user = InfoModel.query.filter_by(username=user_data['username'],password=user_data['password']).first()
    if user.password == str(user_data['password']) and user.is_verified == 'YES':
        encoded_jwt = jwt.encode({"uid": user.uid}, "secret", algorithm="HS256")
        return jsonify({"message": f"User Login Successful... Welcome {user.username}","token":encoded_jwt})
    return jsonify({"message":"User Login Unsuccessful","Data":user_data})


@app.route('/verify',methods=['POST','GET'])
def verify():
    email = request.get_json()
    print(otp)
    message = Message('OTP for verification',sender=params['gmail_user'],recipients=[email['email']])
    message.body = f"Enter this - {str(otp)} - OTP for your EMAIL verification ! THANK YOU :)"
    mail.send(message)
    return jsonify({"message":"OTP is send on given mail address","data":email})

@app.route('/validate',methods=['POST'])
def validate():
    user_data = request.get_json()
    print(otp)
    if otp == int(user_data['otp']):
        user = InfoModel.query.filter_by(emailaddress=user_data['email']).first()
        user.is_verified = 'YES'
        db.session.commit()
        print(user.uid)
        encoded_jwt = jwt.encode({"uid":user.uid}, "secret", algorithm="HS256")
        print(encoded_jwt)
        return jsonify({"message":"Email verification successfully","token":encoded_jwt})
    return jsonify({"message":"Email verification unsuccessful"})


if __name__ == '__main__':
    app.run(debug=True)