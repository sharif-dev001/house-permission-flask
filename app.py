from flask import Flask
from config import Config
from extensions import db


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    # REGISTER BLUEPRINTS
    from routes.auth import auth
    app.register_blueprint(auth)

    from routes.admin import admin
    app.register_blueprint(admin)

    # IMPORT MODELS + CREATE TABLES
    with app.app_context():
        from models import User, Request, Approval
        db.create_all()

    # HOME ROUTE
    @app.route('/')
    def home():
        return "System Running Correctly"

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)