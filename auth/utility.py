from auth.app import app
from flask_migrate import Migrate
from models import db
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:root@localhost:5432/bookstore_product"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)