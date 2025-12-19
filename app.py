import os
from flask import Flask
from auth.routes import auth_bp
from views.routes import views_bp
from conferences.routes import conferences_bp
from utils.jwt_utils import jwt_manager
from utils.scheduler import start_cleanup_scheduler
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'insightroom-frontend', 'pages'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'insightroom-frontend', 'static'))

# Конфигурация
app.config['JWT_SECRET_KEY'] = 'QpKwDx2bnFSNaSpm0J72Dfw0'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 900
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token_cookie'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/'
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Инициализация расширений
jwt_manager.init_app(app)

# Инициализация SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

CORS(app, 
     supports_credentials=True,
     origins=["http://localhost:5000", "http://127.0.0.1:5000"])

# Регистрация blueprint'ов
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(views_bp)
app.register_blueprint(conferences_bp)

# Инициализация WebSocket обработчиков
from conferences import sockets
sockets.init_socketio(socketio)

# Запуск фоновых задач
start_cleanup_scheduler()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, ssl_context='adhoc')