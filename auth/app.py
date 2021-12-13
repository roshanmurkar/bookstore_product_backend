from flask import Flask
from flask_mail import *
from random import *
import json
import logging


app = Flask(__name__)

with open('config.json','r') as f:
    params = json.load(f)['host_mail']

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:root@localhost:5432/bookstore_product"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = params['gmail_user']
app.config['MAIL_PASSWORD'] = params['gmail_password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

logging.basicConfig(filename="bookstore_otp.log", filemode="w", datefmt='%Y-%m-%d,%H:%M:%S:%f')
log = logging.getLogger()
# log.setLevel(logging.DEBUG)