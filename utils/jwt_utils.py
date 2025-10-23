import os
import jwt
from flask_jwt_extended import JWTManager, decode_token
from flask import current_app
import time
import datetime
from data.main import *

jwt_manager = JWTManager()
# Черный список токенов
def add_to_blacklist(token: str) -> None:
    '''Добавляет токен в черный список'''
    if token and token != 'None':
        payload = decode_token(token)
        exp_timestamp = datetime.fromtimestamp(payload.get('exp'))
        DataBase.add_token(Tokens(token, exp_timestamp))

@jwt_manager.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload) -> bool:
    """Проверка, находится ли токен в черном списке"""
    jti = jwt_payload["jti"]
    for token in DataBase.get_all_tokens():
        if token.token == jti:
            return True 
    return False

@jwt_manager.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload) -> tuple[dict, int]:
    """Обработчик истечения access token"""
    return {
        'error': 'access_token_expired',
        'message': 'Access token истек. Используйте refresh token для получения нового.'
    }, 401

@jwt_manager.invalid_token_loader
def invalid_token_callback(error) -> tuple[dict, int]:
    """Обработчик невалидного токена"""
    return {
        'error': 'invalid_token',
        'message': 'Токен невалиден.'
    }, 401

@jwt_manager.unauthorized_loader
def missing_token_callback(error):
    """Обработчик отсутствия токена"""
    print("Error", "нет токена")
    return {
        'error': 'authorization_required',
        'message': 'Требуется аутентификация.'
    }, 401

def is_token_expired(token) -> tuple[bool, dict]:
    """
    Проверяет, просрочен ли JWT токен
    
    Args:
        token (str): JWT токен
    
    Returns:
        bool: True если токен просрочен, False если валиден
        dict: Дополнительная информация об ошибке (если есть)
    """
    try:
        # Декодируем токен без проверки срока действия
        payload = decode_token(token)
        # Проверяем срок действия вручную
        current_time = time.time()
        exp_timestamp = payload.get('exp')
        
        if exp_timestamp is None:
            return True, {'error': 'Токен не содержит срока действия'}
        
        if current_time > exp_timestamp:
            return True, {'expired_at': datetime.fromtimestamp(exp_timestamp).isoformat()}
        else:
            return False, {'expires_at': datetime.fromtimestamp(exp_timestamp).isoformat()}
            
    except jwt.ExpiredSignatureError:
        return True, {'error': 'Токен просрочен'}
    except jwt.InvalidTokenError as e:
        return True, {'error': f'Невалидный токен: {str(e)}'}
    except Exception as e:
        return True, {'error': f'Ошибка при проверке токена: {str(e)}'}
    
def cleanup_expired_tokens() -> int:
    '''Очищает черный список от просроченных токенов'''
    count_invalid_tokens = 0
    tokens = DataBase.get_all_tokens()
    for token in tokens:
        if is_token_expired(token.token):
            count_invalid_tokens += 1
            DataBase.delete_token(token)
    return count_invalid_tokens