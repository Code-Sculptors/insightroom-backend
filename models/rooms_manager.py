import time
from datetime import datetime
if __name__ == '__main__':
    from ..data.main import *
    from ..utils import ini_utils
else:
    from data.main import *
    from utils import ini_utils

import hashlib

def generate_room_url_deterministic(room_id, room_name, prefix="ir"):
    """
    Генерирует уникальный URL для комнаты без случайной соли
    """
    # Данные для хэширования
    data = f"{room_id}:{room_name}:{int(time.time())}"
    
    # Создаем SHA256 хэш
    hash_object = hashlib.sha256(data.encode())
    hash_hex = hash_object.hexdigest()
    
    # Берем первые 8 символов хэша
    url_part = hash_hex[:8]
    
    # Создаем простую контрольную сумму
    checksum = hashlib.md5(url_part.encode()).hexdigest()[:2]
    
    # Формируем окончательный URL
    room_url = f"{prefix}-{url_part}-{checksum}"
    
    return room_url

def validate_room_url(url, room_id, room_name, prefix="ir"):
    """
    Проверяет, соответствует ли URL данной комнате
    """
    # Генерируем ожидаемый URL
    expected_url = generate_room_url_deterministic(room_id, room_name, prefix)
    
    # Сравниваем
    return url == expected_url


class Rooms_manager():
    def __init__(self):
        pass

    def create_room(self, user_id: int, room_name: str, description: str, activation_time: str) -> str:
        """Функция для создания комнаты и всего, что с ней связано
        Args:
            user_id (int): ID создателя комнаты,
            room_name (str): Название комнаты, 
            description (str): Описание комнаты, 
            activation_time (str): Время активации ["now" | timestamp], 
        Returns:
            URL (str): Ссылка на комнату"""
        if activation_time == 'now':
            activation_time = int(datetime.timestamp(datetime.now()))

        url = generate_room_url_deterministic(user_id, room_name)

        new_room = Room(activation_time=activation_time,
                        message_file=ini_utils.create_message_file(url),
                        settings_file=ini_utils.create_room_setting_file(url))
        new_room.room_id = DataBase.add_room(new_room)

        room_info = RoomInfo(room_id=new_room.room_id,
                             description=description,
                             room_name=room_name,
                             room_url=url)
        DataBase.add_room_info(room_info)

        DataBase.add_user_and_room(user_id, new_room.room_id)

        user_role = UserRole(new_room.room_id, user_id, 'Creator')
        DataBase.add_user_role(user_role)

        return url

    def get_user_rooms(self, user_id: int) -> list:
        rooms = DataBase.get_all_rooms()
        user_roles = DataBase.get_all_user_roles()
        # user_roles = [user_role for user_role in user_roles if user_role.user_id == user_id]
        rooms = list(filter(lambda x: x.room_id in [role.room_id for role in user_roles], rooms))
        answer = [DataBase.get_room_info(room.room_id) for room in rooms]
        return answer


rooms_manager = Rooms_manager()