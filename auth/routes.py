from flask import Blueprint, request, jsonify, Response, redirect
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies
)
from utils.jwt_utils import add_to_blacklist
from models import user_manager, rooms_manager
from datetime import datetime
import os

auth_bp = Blueprint('auth', __name__, template_folder=os.path.dirname(os.path.abspath(__file__)) + '/../../insightroom-frontend/pages')

@auth_bp.route('/register', methods=['POST'])
def register() -> Response:
    """Регистрация нового пользователя"""
    try:
        data = request.json
        
        # Проверяем обязательные поля
        required_fields = ['username', 'email', 'password', 'login', 'tel']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Поле {field} обязательно'}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        login = data['login']
        phone_number = data['tel']
        print(username, email, password, login, phone_number)
        # Регистрируем пользователя
        ans = user_manager.user_manager.register_user(username, email, password, login, phone_number)

        success, result = ans
        if success and result is str:
            user_data = result
            access_token = create_access_token(
                identity=user_data.user_id,
                additional_claims={
                    'verified': user_data.verified
                }
            )
            refresh_token = create_refresh_token(identity=user_data.user_id)
            print(f"REG: {login}", access_token, refresh_token, sep='\n')

            response = redirect('/')
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response
        else:
            return jsonify({'error': result}), 401
            
    except Exception as e:
        print(f'ERROR: `{e}` in /register')
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login() -> Response:
    """Аутентификация пользователя"""
    try:
        login = request.json.get('login', None)
        email = request.json.get('email', None)
        phone = request.json.get('phone', None)
        password = request.json.get('password', None)
        print(login, email, phone, password)

        if not (login or email or phone) or not password:
            return jsonify({'error': 'Логин и пароль обязательны'}), 400
        
        if email:
            user = user_manager.user_manager.get_user_by_email(email)
            login = user_manager.user_manager.get_auth(user.user_id).login
        elif phone:
            user = user_manager.user_manager.get_user_by_phone(phone)
            login = user_manager.user_manager.get_auth(user.user_id).login

        success, result = user_manager.user_manager.authenticate_user(login, password)
        if success:
            user_data = result
            access_token = create_access_token(
                identity=str(user_data.user_id)
            )
            refresh_token = create_refresh_token(identity=str(user_data.user_id))
            print(f"LOG IN: {login}", access_token, refresh_token, sep='\n')

            response = jsonify({
                'message': 'Login successful',
                'access_expires_in': 900,  
                'refresh_expires_in': 604800
            })
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response
        else:
            print(result)
            return jsonify({'error': result}), 401
            
    except Exception as e:
        print(f'ERROR {e} in /login POST')
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh() -> Response:
    """Обновление access token"""
    print('LOG: Start refreshing...')
    current_user = get_jwt_identity()
    new_access_token = create_access_token(
        identity=current_user,
        additional_claims={'verified': user_manager.user_manager.get_user(current_user).verified}
    )
    response = jsonify({'msg': 'Token refreshed'})
    set_access_cookies(response, new_access_token)
    return response

@auth_bp.route('/check-auth')
@jwt_required(optional=True)
def check_auth():
    current_user = get_jwt_identity()
    if current_user:
        return jsonify({'authenticated': True, 'user_id': current_user})
    else:
        return jsonify({'authenticated': False}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout() -> Response:
    """Выход из системы"""
    access_token = request.cookies.get('access_token_cookie')
    refresh_token = request.cookies.get('refresh_token_cookie')
    print(access_token, refresh_token, sep='\n')
    add_to_blacklist(access_token)
    add_to_blacklist(refresh_token)
    response = jsonify({'message': 'Logged out successfully'})
    unset_jwt_cookies(response)
    return response


'''!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Блок работы с комнатами и прочим!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'''
@auth_bp.route('/create-room', methods=['POST'])
@jwt_required(optional=True)
def create_room() -> Response:
    """Создание комнаты"""
    try:
        user_id = get_jwt_identity()
        room_name = request.json.get('room.name')
        description = request.json.get('room.description', None)
        if description == '(empty)': description = '';
        if (time := request.json.get('room.activation_time')) == 'now':
            activation_time = time
        else:
            activation_time = int(datetime.timestamp(datetime.fromisoformat(time)))
        url = rooms_manager.rooms_manager.create_room(user_id, room_name, description, activation_time)
        return jsonify({'url': url}), 200
    except Exception as ex:
        print(f'ERROR: {ex} in /create_room')
        return jsonify({'error': str(ex)}), 500


@auth_bp.route('/refactor_room', methods=['PUT'])
@jwt_required()
def refactor_room() -> Response:
    """Изменение комнаты"""
    try:
        room_url = request.json.get('room.id')
        room_id = rooms_manager.rooms_manager.get_room_id_by_url(room_url)
        room = rooms_manager.DataBase.get_room(room_id)
        room_info = rooms_manager.DataBase.get_room_info(room_id)
        room_info.room_name = request.json.get('room.name')
        description = request.json.get('room.description', None)
        if description == '(empty)': description = '';
        if description: room_info.description = description
        if (time := request.json.get('room.activation_time')) == 'T':
            activation_time = None
        else:
            activation_time = time.replace('T', ' ')
        if activation_time: room.activation_time = activation_time
        rooms_manager.DataBase.update_room(room)
        rooms_manager.DataBase.update_room_info(room_info)
        return jsonify({'room_id': room_id}), 200
    except Exception as ex:
        print(f'ERROR: {ex} in /refactor_room')
        return jsonify({'error': str(ex)}), 500


@auth_bp.route('/add_contact', methods=['POST'])
@jwt_required(optional=True)
def add_contact() -> Response:
    """Добавление контакта"""
    try:
        user_id = get_jwt_identity()
        contact_name = request.json.get('contact.name')
        contact_login = request.json.get('contact.login')
        user_manager.user_manager.add_contact(user_id, contact_name, contact_login)
        return jsonify({'contact_name': contact_name, 'contact_login': contact_login}), 200
    except Exception as ex:
        print(f'ERROR: {ex} in /add_contact')
        return jsonify({'error': str(ex)}), 500
    
@auth_bp.route('/edit_contact', methods=['PUT'])
@jwt_required()
def edit_contact() -> Response:
    '''Изменение контакта'''
    try:
        contact_id = request.json.get('contact.id')
        contact_name = request.json.get('contact.name')
        rooms_manager.DataBase.update_contact(rooms_manager.Contact(contact_id=contact_id, contact_name=contact_name))
        return jsonify({'contact_id': contact_id}), 200
    except Exception as ex:
        print(f'ERROR: {ex} in /edit_contact')
        return jsonify({'error': str(ex)}), 500
