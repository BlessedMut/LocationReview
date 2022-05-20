from flask_login import UserMixin

from . import db


class User(db.Document, UserMixin):
    email = db.EmailField(max_length=50)
    password = db.StringField(required=True)
    fullname = db.StringField(min_length=3, max_length=50)


class IPAddresses(db.Document):
    ip = db.StringField(required=True)
    continent = db.StringField(required=True, max_length=30)
    country = db.StringField(required=True)
    country_code = db.StringField(required=True)
    region = db.StringField(required=True)
    region_code = db.StringField(required=True)
    city = db.StringField(required=True)
    search_frequency = db.IntField()
    user_email = db.StringField(required=True)
