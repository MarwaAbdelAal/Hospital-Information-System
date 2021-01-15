from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)      # __name__ is a special var in python that is just the name of the module
app.config['SECRET_KEY'] = '8a24707af73b201e1cc1ce5c0193ce8e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from his.dashboard import add_dash
app = add_dash(app)
from his import routes