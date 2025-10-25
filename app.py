import os
from flask import Flask
from auth.routes import auth_bp
from views.routes import views_bp
from utils.jwt_utils import jwt_manager
from utils.scheduler import start_cleanup_scheduler
from flask_cors import CORS


app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)) + '../insightroom-frontend/pages', 
            static_folder=os.path.dirname(os.path.abspath(__file__)) + '/../insightroom-frontend/static')

# Конфигурация
app.config['JWT_SECRET_KEY'] = 'QpKwDx2bnFSNaSpm0J72Dfw0'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 900
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token_cookie'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Для разработки
app.config['JWT_COOKIE_SECURE'] = False  # True в production с HTTPS
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/'

# Инициализация расширений
jwt_manager.init_app(app)

CORS(app, 
     supports_credentials=True,
     origins=["http://localhost:5000", "http://127.0.0.1:5000"])

# Регистрация blueprint'ов
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(views_bp)

# Запуск фоновых задач
start_cleanup_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')