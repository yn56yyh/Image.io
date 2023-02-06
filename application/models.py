from application import db, login_manager
from flask_login import UserMixin

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    gender = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer)
    hypertension = db.Column(db.Integer)
    heart_disease = db.Column(db.Integer)
    ever_married = db.Column(db.Integer)
    work_type = db.Column(db.Integer)
    residence_type = db.Column(db.Integer)
    avg_glucose_level = db.Column(db.Float)
    bmi = db.Column(db.Float)
    smoking_status = db.Column(db.Integer)
    stroke = db.Column(db.Integer)
    predicted_dt = db.Column(db.DateTime, nullable = False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
