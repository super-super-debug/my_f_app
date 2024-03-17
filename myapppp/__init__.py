from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import pymysql
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY']='dev'
app.logger.setLevel(logging.DEBUG)
app.logger.debug("debug")
    
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Ichimura$2002@localhost/My_chatrooms?charset=utf8mb4'
db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)


from .authenication import bp
app.register_blueprint(bp)

from .my_web_app import bp
app.register_blueprint(bp)
        
