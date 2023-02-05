from flask import Flask
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

#create the Flask app
app = Flask(__name__)
CORS(app)

# Instantiate Bcrypt 
bcrypt = Bcrypt(app)

# Instatiating the Login Manager
login_manager = LoginManager(app)

# Instantiate SQLAlchemy to handle Database Process
db = SQLAlchemy()


# load configuration from config.cfg
app.config.from_pyfile('config.cfg')
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    db.init_app(app)
    from .models import Entry
    db.create_all()
    db.session.commit()
    print ('Database has been created!')





from application import routes