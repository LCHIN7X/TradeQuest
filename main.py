from flask import Flask, render_template, g
from models import db
from flask_login import LoginManager, current_user


DATABASE_NAME = 'database.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "TRADEQUEST"
    app.config["UPLOADED_PHOTOS_DEST"] = "static/images"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_NAME}"

    from user.models import User
    from user.views import views
    app.register_blueprint(views, url_prefix="/views")

    from trade.views import trade
    app.register_blueprint(trade, url_prefix="/trade")

    from ranking.views import rank
    app.register_blueprint(rank, url_prefix="/rank")

    from chatbot import chatbot
    app.register_blueprint(chatbot, url_prefix="/chatbot")

    from vip.views import vip 
    app.register_blueprint(vip,url_prefix="/vip")

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

    @app.context_processor
    def inject_profile_pic():
        if current_user.is_authenticated:
            return dict(current_profile_pic=current_user.profile_pic)  # Adjust based on your User model
        return dict(current_profile_pic=None)  # Default if no user is logged in
    


    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
