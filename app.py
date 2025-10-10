import os
from flask import Flask
from auth.routes import auth_bp
from views.routes import views_bp
from utils.jwt_utils import jwt_manager
from utils.scheduler import start_cleanup_scheduler

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)) + '../insightroom-frontend/pages', 
            static_folder=os.path.dirname(os.path.abspath(__file__)) + '/../insightroom-frontend/static')

# Конфигурация
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 900
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800

# Инициализация расширений
jwt_manager.init_app(app)

# Регистрация blueprint'ов
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(views_bp)

# Запуск фоновых задач
start_cleanup_scheduler()

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')