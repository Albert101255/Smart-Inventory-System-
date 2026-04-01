from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from app.models import db, User

mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register Blueprints
    from app.auth.routes import auth
    from app.admin.routes import admin
    from app.products.routes import products
    from app.stock.routes import stock
    from app.reports.routes import reports
    
    app.register_blueprint(auth)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(products)
    app.register_blueprint(stock)
    app.register_blueprint(reports)

    # Create tables
    with app.app_context():
        db.create_all()

    from flask import render_template
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    return app
