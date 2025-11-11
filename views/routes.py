from flask import Blueprint, render_template
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt, verify_jwt_in_request
from data.main import *
import os
from models import user_manager, rooms_manager
import time, datetime

views_bp = Blueprint('views', __name__, template_folder=os.path.dirname(os.path.abspath(__file__)) + '/../../insightroom-frontend/pages')

@views_bp.route('/')
def index() -> str:
    """Главная страница"""
    return render_template('index.html')

@views_bp.route('/login')
def login_page() -> str:
    """Страница входа"""
    return render_template('auth.html')

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

@views_bp.route('/cabinet')
@jwt_required()
def cabinet_page() -> str:
    """Личный кабинет"""
    user = DataBase.get_user(get_jwt_identity())
    login = DataBase.get_auth(user_id=user.user_id).login
    
    created_rooms = rooms_manager.rooms_manager.get_created_rooms(get_jwt_identity())
    all_rooms = rooms_manager.rooms_manager.get_user_rooms(get_jwt_identity())
    
    contacts = user_manager.user_manager.get_user_contacts(get_jwt_identity())
    return render_template('personal-cabinet.html',
                           user_name=user.username,
                           user_login=login,
                           
                           sessions_count=len(created_rooms),
                           current_meetings=created_rooms,

                           all_meetings_count=len(all_rooms),
                           all_meetings=all_rooms,

                           contacts_count=len(contacts),
                           contacts=contacts
                        )

@views_bp.route('/schedule-meeting')
@jwt_required()
def schedule_meeting() -> str:
    """Запланировать встречу"""
    user = DataBase.get_user(get_jwt_identity())
    login = DataBase.get_auth(user_id=user.user_id).login
    
    return render_template('schedule-meeting.html',
                            user_name=user.username,
                              user_login=login                             
                              )