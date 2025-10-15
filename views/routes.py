from flask import Blueprint, render_template
import os

views_bp = Blueprint('views', __name__, template_folder=os.path.dirname(os.path.abspath(__file__)) + '/../../insightroom-frontend/pages')

@views_bp.route('/')
def index() -> str:
    """Главная страница"""
    return render_template('index.html')

@views_bp.route('/login')
def login_page() -> str:
    """Страница входа"""
    return render_template('auth.html')

@views_bp.route('/dashboard')
def dashboard() -> str:
    """Личный кабинет"""
    return render_template('dashboard.html')

@views_bp.route('/register')
def register_page() -> str:
    """Страница регистрации"""
    return render_template('register.html')

@views_bp.route('/create_meeting')
def create_meet_page() -> str:
    """Страница создания видеоконференции"""
    return render_template('create-meeting.html')

@views_bp.route('/join_meeting')
def join_meet_page() -> str:
    """Страница присоединения к видеоконференции"""
    return render_template('join-meeting.html')

@views_bp.route('/schedule_meeting')
def schedule_meet_page() -> str:
    """Страница планирования конференции"""
    return render_template('schedule-meeting.html')