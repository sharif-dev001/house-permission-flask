from flask import Flask
from config import Config
from extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from routes.auth import auth
    app.register_blueprint(auth)

    return app

app = create_app()

with app.app_context():
    from models import User, Request, Approval
    db.create_all()

@app.route('/')
def home():
    return "System Running Correctly"

if __name__ == "__main__":
    app.run(debug=True)