from flask import Flask
from flask_cors import CORS
from extensions import login_manager

def create_app():
    app = Flask(__name__)
    from config import Config
    app.config.from_object(Config)
    
    CORS(app, supports_credentials=True)
    login_manager.init_app(app)
    
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp
    from routes.payment import payment_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')
    
    from utils.scheduler import start_scheduler
    start_scheduler(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
