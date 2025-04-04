from flask import Flask
from flask_cors import CORS

from backend.db import connect_mongo

def create_app():
    app = Flask(__name__)
    CORS(app)
    connect_mongo()

    # Register blueprints
    from backend.routes.test_routes import test_bp
    app.register_blueprint(test_bp, url_prefix='/test')

    from backend.routes.student_routes import student_bp
    app.register_blueprint(student_bp, url_prefix='/student')
    
    from backend.routes.generate_routes import generate_bp
    app.register_blueprint(generate_bp, url_prefix='/generate')

    from backend.routes.process_routes import process_bp
    app.register_blueprint(process_bp,url_prefix='/process')

    return app

