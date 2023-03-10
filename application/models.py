from application import db, login_manager
from flask_login import UserMixin

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    image_url = db.Column(db.String(500), nullable=False)
    model_selection = db.Column(db.String(20), nullable = False)
    pred = db.Column(db.String(20), nullable = False)
    pred_dt = db.Column(db.DateTime, nullable = False)
    conf_pct = db.Column(db.Float, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
