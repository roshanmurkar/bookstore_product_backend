from flask import Flask,jsonify,request
from auth.app import app
from auth.views import registration
from auth.views import details
from auth.views import login

app.register_blueprint(registration)
app.register_blueprint(details)
app.register_blueprint(login)

if __name__ == '__main__':
    app.run(debug=True)