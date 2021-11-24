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