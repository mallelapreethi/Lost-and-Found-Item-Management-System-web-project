from flask import Flask
import mysql.connector
#from flask_login import LoginManager
mydb = mysql.connector.connect(host="localhost",
                               user="root",
                               password="GAMRAKSHA@100",
                               database="lnfdb")

def create_app():
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'habcdefghjiklm'
        from .views import views 
        from .auth import auth
        app.register_blueprint(views, url_prefix='/')
        app.register_blueprint(auth, url_prefix='/')
        return app


