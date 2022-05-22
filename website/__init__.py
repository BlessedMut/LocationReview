import urllib
from datetime import timedelta

from flask import Flask
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from requests import session

app = Flask(__name__)
db = MongoEngine()

DB_URI = 'mongodb+srv://blessedmute:' + urllib.parse.quote('@Support1999') + '@pydev.knajo.mongodb.net/test'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '@Support!999wkpProg219$$fish'
    # app.config['MONGODB_SETTINGS'] = {
    #     'db': 'test_database_location',
    #     'host': 'localhost',
    #     'port': 27017
    # }
    app.config["MONGODB_HOST"] = DB_URI
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=7)

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, IPAddresses

    # create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.objects.get(id=id)

    return app

# def create_database(app):
#     # if not path.exists('website/' + DB_NAME):
#     db.create_all(app=app)
#     print('Created Database!')
