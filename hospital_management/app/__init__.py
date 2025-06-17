# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# from flask_migrate import Migrate
# from config import Config
# from dotenv import load_dotenv
# import os

# # ✅ Load environment variables
# load_dotenv()

# # ✅ Initialize extensions
# db = SQLAlchemy()
# login_manager = LoginManager()
# login_manager.login_view = 'auth.login'
# migrate = Migrate()

# # ✅ Import models so they are registered with SQLAlchemy
# from app.models import prediction_result



# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     # ✅ Ensure the upload folder exists
#     if not os.path.exists(app.config['UPLOAD_FOLDER']):
#         os.makedirs(app.config['UPLOAD_FOLDER'])

#     # ✅ Initialize extensions with app
#     db.init_app(app)
#     login_manager.init_app(app)
#     migrate.init_app(app, db)

#     # ✅ Register blueprints
#     from app.controllers.auth_controller import auth_bp
#     from app.controllers.appointment_controller import appointment_bp
#     from app.controllers.report_controller import report_bp
#     from app.controllers.ai_controller import ai_bp
#     from app.controllers.main_controller import main_bp

#     app.register_blueprint(auth_bp)
#     app.register_blueprint(appointment_bp)
#     app.register_blueprint(report_bp)
#     app.register_blueprint(ai_bp)
#     app.register_blueprint(main_bp)

#     return app


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from dotenv import load_dotenv
import os

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Ensure the upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # ✅ Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # ✅ Import all models so Flask-Migrate recognizes them
    from app.models import user, appointment, report, prediction_result

    # ✅ Register blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.appointment_controller import appointment_bp
    from app.controllers.report_controller import report_bp
    from app.controllers.ai_controller import ai_bp      # ✅ includes speech-to-text
    from app.controllers.main_controller import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(main_bp)

    return app
