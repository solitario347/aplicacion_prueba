from flask import Flask, redirect, url_for
from config import Config
from models import db, User
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # Ruta a la que redirige si no está autenticado
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from auth.routes import auth_bp
    from events.routes import events_bp
    from users.routes import users_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(users_bp)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return redirect(url_for('events.list_events'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)