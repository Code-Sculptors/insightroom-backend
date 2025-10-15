import re
import os
import hashlib
import secrets
import json

class UserManager:
    '''Класс для работы с пользователями через БД'''
    def __init__(self):
        default_users = {
            'user1': {
                'password': self.hash_password('password1'),
                'email': 'user1@example.com',
                'role': 'user',
                'created_at': '2024-01-01'
            },
            'admin': {
                'password': self.hash_password('admin123'),
                'email': 'admin@example.com',
                'role': 'admin',
                'created_at': '2024-01-01'
            }
        }
        try:
            db = open(os.path.dirname(os.path.abspath(__file__)) + '/../data/db.json', mode='r', encoding='utf-8')
            if db.read().strip() == '':
                self.users = default_users
            else:
                db.seek(0)
                self.users : dict = json.load(db)
            db.close()
        except json.decoder.JSONDecodeError:
            self.users = dict()
        except FileNotFoundError:
            with open(os.path.dirname(os.path.abspath(__file__)) + '/../data/db.json', mode='w') as _:
                self.users = dict()
        if not self.users.get('user1', False):
            self.users['user1'] = {
                'password': self.hash_password('password1'),
                'email': 'user1@example.com',
                'role': 'user',
                'created_at': '2024-01-01'
            }
        
        if not self.users.get('admin', False):
            self.users['admin'] = {
                'password': self.hash_password('admin123'),
                'email': 'admin@example.com',
                'role': 'admin',
                'created_at': '2024-01-01'
            }
            
    
    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        # Используем простое хеширование для демонстрации
        # В реальном приложении используйте bcrypt или аналоги
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.hash_password(password) == hashed_password
    
    def validate_username(self, username: str) -> tuple[bool, str]:
        """Валидация имени пользователя"""
        if len(username) < 3 or len(username) > 20:
            return False, "Имя пользователя должно быть от 3 до 20 символов"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Имя пользователя может содержать только буквы, цифры и подчеркивания"
        
        if username in self.users:
            return False, "Имя пользователя уже занято"
        
        return True, "OK"
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Валидация пароля"""
        if len(password) < 6:
            return False, "Пароль должен содержать минимум 6 символов"
        
        return True, "OK"
    
    def validate_email(self, email: str) -> tuple[bool, str]:
        """Валидация email"""
        # Простая проверка формата email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False, "Некорректный формат email"
        
        # Проверка уникальности email
        for user_data in self.users.values():
            if user_data.get('email') == email:
                return False, "Email уже используется"
        
        return True, "OK"
    
    def register_user(self, username: str, email: str, password: str, role: str='user') -> tuple[bool, str]:
        """Регистрация нового пользователя"""
        # Валидация данных
        valid, message = self.validate_username(username)
        if not valid:
            return False, message
        
        valid, message = self.validate_email(email)
        if not valid:
            return False, message
        
        valid, message = self.validate_password(password)
        if not valid:
            return False, message
        
        # Добавление пользователя
        self.users[username] = {
            'password': self.hash_password(password),
            'email': email,
            'role': role,
            'created_at': '2024-01-01'  # В реальном приложении используйте datetime
        }
        
        self.database_update()

        return True, "Пользователь успешно зарегистрирован"
    
    def authenticate_user(self, username: str, password: str) -> tuple[bool, str]:
        """Аутентификация пользователя"""
        if username not in self.users:
            return False, "Пользователь не найден"
        
        if not self.verify_password(password, self.users[username]['password']):
            return False, "Неверный пароль"
        
        return True, self.users[username]
    
    def get_user(self, username: str) -> dict:
        """Получение информации о пользователе"""
        return self.users.get(username)
    
    def get_all_users(self) -> dict:
        """Получение списка всех пользователей (для админа)"""
        return {
            username: {k: v for k, v in data.items() if k != 'password'}
            for username, data in self.users.items()
        }
    
    def database_update(self) -> None:
        """Отправка данных в бд"""
        with open('./data/db.json', mode='w', encoding='utf-8') as db:
            json.dump(self.users, db)
        print('База данных обновлена')
        

# Глобальный экземпляр менеджера пользователей
user_manager = UserManager()