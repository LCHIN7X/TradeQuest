from flask import Flask, render_template
from models import db
from flask_login import LoginManager

DATABASE_NAME = 'database.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "TRADEQUEST"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_NAME}"

    from user.models import User
    from user.views import views
    app.register_blueprint(views, url_prefix="/views")

    from trade.views import trade
    app.register_blueprint(trade, url_prefix="/trade")

    db.init_app(app)

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "views.login"
    login_manager.init_app(app)

    @login_manager.user_loader 
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route("/")
    def home():
        return render_template('home.html')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

