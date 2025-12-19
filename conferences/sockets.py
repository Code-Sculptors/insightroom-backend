from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import logging

# Будет инициализировано в app.py
socketio = None

def init_socketio(socketio_instance):
    global socketio
    socketio = socketio_instance
    register_handlers()

# Хранилище активных подключений
active_connections = {}

def register_handlers():
    """Регистрация обработчиков WebSocket событий"""
    
    @socketio.on('connect')
    def handle_connect():
        logging.info(f"Клиент подключился: {request.sid}")
        emit('connected', {'status': 'connected', 'sid': request.sid})

    @socketio.on('disconnect')
    def handle_disconnect():
        logging.info(f"Клиент отключился: {request.sid}")
        
        # Удаляем пользователя из всех комнат
        for room_url, users in list(active_connections.items()):
            if request.sid in users:
                user_info = users.pop(request.sid)
                
                # Уведомляем других участников
                emit('user-left', {
                    'userId': request.sid,
                    'userName': user_info.get('name', 'Участник')
                }, room=room_url, include_self=False)
                
                # Если комната пустая, удаляем ее
                if not users:
                    active_connections.pop(room_url, None)
                
                logging.info(f"Пользователь {request.sid} удален из комнаты {room_url}")
                break

    @socketio.on('join-room')
    def handle_join_room(data):
        """Присоединение к комнате конференции"""
        try:
            room_url = data.get('roomUrl')
            user_name = data.get('userName', 'Участник')
            
            if not room_url:
                emit('error', {'message': 'Room URL is required'})
                return
            
            logging.info(f"Пользователь {request.sid} присоединяется к комнате {room_url}")
            
            # Добавляем в комнату
            join_room(room_url)
            
            # Инициализируем хранилище для комнаты
            if room_url not in active_connections:
                active_connections[room_url] = {}
            
            # Сохраняем информацию о пользователе
            active_connections[room_url][request.sid] = {
                'name': user_name,
                'id': request.sid,
                'room_url': room_url
            }
            
            # Отправляем список текущих участников новому пользователю
            users_in_room = list(active_connections[room_url].values())
            emit('room-users', {
                'users': users_in_room,
                'yourId': request.sid
            }, room=request.sid)
            
            # Уведомляем других участников о новом пользователе
            emit('user-joined', {
                'userId': request.sid,
                'userName': user_name
            }, room=room_url, include_self=False)
            
            logging.info(f"Пользователь {user_name} ({request.sid}) присоединился к комнате {room_url}")
            
        except Exception as e:
            logging.error(f"Ошибка при присоединении к комнате: {str(e)}")
            emit('error', {'message': 'Internal server error'})

    @socketio.on('webrtc-offer')
    def handle_webrtc_offer(data):
        """Пересылка WebRTC offer"""
        try:
            target_user = data.get('to')
            offer = data.get('offer')
            
            if target_user and offer:
                emit('webrtc-offer', {
                    'offer': offer,
                    'from': request.sid
                }, room=target_user)
        except Exception as e:
            logging.error(f"Ошибка пересылки offer: {str(e)}")

    @socketio.on('webrtc-answer')
    def handle_webrtc_answer(data):
        """Пересылка WebRTC answer"""
        try:
            target_user = data.get('to')
            answer = data.get('answer')
            
            if target_user and answer:
                emit('webrtc-answer', {
                    'answer': answer,
                    'from': request.sid
                }, room=target_user)
        except Exception as e:
            logging.error(f"Ошибка пересылки answer: {str(e)}")

    @socketio.on('ice-candidate')
    def handle_ice_candidate(data):
        """Пересылка ICE candidate"""
        try:
            target_user = data.get('to')
            candidate = data.get('candidate')
            
            if target_user and candidate:
                emit('ice-candidate', {
                    'candidate': candidate,
                    'from': request.sid
                }, room=target_user)
        except Exception as e:
            logging.error(f"Ошибка пересылки ICE candidate: {str(e)}")

    @socketio.on('leave-room')
    def handle_leave_room(data):
        """Выход из комнаты"""
        try:
            room_url = data.get('roomUrl')
            
            if room_url and room_url in active_connections:
                user_info = active_connections[room_url].pop(request.sid, None)
                
                if user_info:
                    leave_room(room_url)
                    
                    # Уведомляем других участников
                    emit('user-left', {
                        'userId': request.sid,
                        'userName': user_info.get('name', 'Участник')
                    }, room=room_url, include_self=False)
                    
                    # Если комната пустая, удаляем ее
                    if not active_connections[room_url]:
                        active_connections.pop(room_url, None)
                    
                    logging.info(f"Пользователь {request.sid} покинул комнату {room_url}")
                    
        except Exception as e:
            logging.error(f"Ошибка при выходе из комнаты: {str(e)}")