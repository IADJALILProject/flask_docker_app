from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    # Intégration du dashboard Dash dans Flask
    from app.dashboard.dash_app import create_dash_app
    create_dash_app(app)

    return app


