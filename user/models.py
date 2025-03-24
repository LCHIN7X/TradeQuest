from models import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    cash = db.Column(db.Float, default=1000.0)
    is_vip = db.Column(db.Boolean, default=False)
    bio = db.Column(db.String(200), default=None)
    profile_pic = db.Column(db.String(200), default="default_pfp.png")

    def get_is_vip(self):
        return bool(self.is_vip)


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    symbol = db.Column(db.String(10), nullable=False)