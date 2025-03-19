from flask import Flask
from model import db

DATABASE_NAME = 'database.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "TRADEQUEST"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_NAME}"

    db.init_app()

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

