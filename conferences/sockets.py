from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import logging
from datetime import datetime
import time

socketio = None

def init_socketio(socketio_instance):
    global socketio
    socketio = socketio_instance
    register_handlers()

# Хранилище активных подключений: room_url -> {user_id: user_info}
active_connections = {}
# Хранилище сообщений чата: room_url -> list
chat_messages = {}

def register_handlers():
    @socketio.on('connect')
    def handle_connect():
        logging.info(f"✅ Клиент подключился: {request.sid}")
        emit('connected', {'status': 'connected', 'sid': request.sid})

    @socketio.on('disconnect')
    def handle_disconnect():
        logging.info(f"❌ Клиент отключился: {request.sid}")
        
        # Ищем пользователя во всех комнатах
        for room_url, users in list(active_connections.items()):
            for user_id, user_info in list(users.items()):
                if user_info.get('sid') == request.sid:
                    # Удаляем пользователя из комнаты
                    users.pop(user_id, None)
                    
                    # Уведомляем других участников
                    emit('user-left', {
                        'userId': user_id,
                        'userName': user_info.get('name', 'Участник')
                    }, room=room_url)
                    
                    logging.info(f"Удален пользователь {user_id} из комнаты {room_url}")
                    
                    # Если комната пустая, удаляем ее
                    if not users:
                        active_connections.pop(room_url, None)
                        chat_messages.pop(room_url, None)
                    
                    break

    @socketio.on('join-room')
    def handle_join_room(data):
        try:
            room_url = data.get('roomUrl')
            user_name = data.get('userName', 'Участник')
            user_id = data.get('userId')
            
            if not room_url:
                emit('error', {'message': 'Room URL is required'})
                return
            
            if not user_id:
                user_id = request.sid
            
            logging.info(f"👤 Пользователь {user_name} ({user_id}) присоединяется к комнате {room_url}")
            
            # Добавляем в комнату
            join_room(room_url)
            
            # Инициализируем хранилище для комнаты
            if room_url not in active_connections:
                active_connections[room_url] = {}
                chat_messages[room_url] = []
            
            # Проверяем, нет ли уже такого пользователя (предотвращаем дубликаты)
            if user_id in active_connections[room_url]:
                # Обновляем информацию о существующем пользователе
                active_connections[room_url][user_id]['sid'] = request.sid
                logging.info(f"Обновлено соединение для пользователя {user_id}")
            else:
                # Добавляем нового пользователя
                active_connections[room_url][user_id] = {
                    'id': user_id,
                    'sid': request.sid,
                    'name': user_name,
                    'room_url': room_url,
                    'joined_at': time.time()
                }
            
            # Подготавливаем список пользователей без текущего
            users_in_room = [
                {'id': uid, 'name': info['name'], 'sid': info['sid']}
                for uid, info in active_connections[room_url].items()
                if uid != user_id
            ]
            
            # Отправляем текущему пользователю список других участников
            emit('room-users', {
                'users': users_in_room,
                'yourId': user_id
            }, room=request.sid)
            
            # Уведомляем других участников о новом пользователе
            emit('user-joined', {
                'userId': user_id,
                'userName': user_name,
                'userSid': request.sid
            }, room=room_url, skip_sid=request.sid)
            
            logging.info(f"✅ Пользователь {user_name} успешно присоединился к комнате {room_url}")
            
        except Exception as e:
            logging.error(f"Ошибка при присоединении к комнате: {str(e)}")
            emit('error', {'message': f'Internal server error: {str(e)}'})

    @socketio.on('webrtc-offer')
    def handle_webrtc_offer(data):
        """Пересылка WebRTC offer"""
        try:
            target_user = data.get('to')
            offer = data.get('offer')
            from_user = data.get('from')
            
            if target_user and offer and from_user:
                # Находим sid целевого пользователя
                target_sid = None
                for room_url, users in active_connections.items():
                    for user_id, user_info in users.items():
                        if user_id == target_user:
                            target_sid = user_info.get('sid')
                            break
                    if target_sid:
                        break
                
                if target_sid:
                    emit('webrtc-offer', {
                        'offer': offer,
                        'from': from_user
                    }, room=target_sid)
                    logging.info(f"📨 Offer переслан от {from_user} к {target_user}")
                else:
                    logging.warning(f"Целевой пользователь {target_user} не найден")
        except Exception as e:
            logging.error(f"Ошибка пересылки offer: {str(e)}")

    @socketio.on('webrtc-answer')
    def handle_webrtc_answer(data):
        """Пересылка WebRTC answer"""
        try:
            target_user = data.get('to')
            answer = data.get('answer')
            from_user = data.get('from')
            
            if target_user and answer and from_user:
                # Находим sid целевого пользователя
                target_sid = None
                for room_url, users in active_connections.items():
                    for user_id, user_info in users.items():
                        if user_id == target_user:
                            target_sid = user_info.get('sid')
                            break
                    if target_sid:
                        break
                
                if target_sid:
                    emit('webrtc-answer', {
                        'answer': answer,
                        'from': from_user
                    }, room=target_sid)
                    logging.info(f"📨 Answer переслан от {from_user} к {target_user}")
        except Exception as e:
            logging.error(f"Ошибка пересылки answer: {str(e)}")

    @socketio.on('ice-candidate')
    def handle_ice_candidate(data):
        """Пересылка ICE candidate"""
        try:
            target_user = data.get('to')
            candidate = data.get('candidate')
            from_user = data.get('from')
            
            if target_user and candidate and from_user:
                # Находим sid целевого пользователя
                target_sid = None
                for room_url, users in active_connections.items():
                    for user_id, user_info in users.items():
                        if user_id == target_user:
                            target_sid = user_info.get('sid')
                            break
                    if target_sid:
                        break
                
                if target_sid:
                    emit('ice-candidate', {
                        'candidate': candidate,
                        'from': from_user
                    }, room=target_sid)
                    logging.info(f"🧊 ICE candidate переслан от {from_user} к {target_user}")
        except Exception as e:
            logging.error(f"Ошибка пересылки ICE candidate: {str(e)}")

    @socketio.on('media-state')
    def handle_media_state(data):
        """Пересылка состояния медиа"""
        try:
            user_id = data.get('userId')
            audio_enabled = data.get('audioEnabled', False)
            video_enabled = data.get('videoEnabled', False)
            room_url = data.get('roomUrl')
            
            if user_id and room_url and room_url in active_connections:
                # Пересылаем состояние всем в комнате, кроме отправителя
                emit('media-state', {
                    'userId': user_id,
                    'audioEnabled': audio_enabled,
                    'videoEnabled': video_enabled
                }, room=room_url, skip_sid=request.sid)
        except Exception as e:
            logging.error(f"Ошибка пересылки состояния медиа: {str(e)}")

    @socketio.on('chat-message')
    def handle_chat_message(data):
        """Обработка сообщений чата"""
        try:
            room_url = data.get('roomUrl')
            user_name = data.get('userName', 'Аноним')
            message = data.get('message', '')
            user_id = data.get('userId')
            
            if not room_url or not message:
                return
            
            # Сохраняем сообщение
            if room_url not in chat_messages:
                chat_messages[room_url] = []
            
            chat_data = {
                'id': len(chat_messages[room_url]) + 1,
                'user_id': user_id,
                'user_name': user_name,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'time': datetime.now().strftime('%H:%M')
            }
            
            chat_messages[room_url].append(chat_data)
            
            # Ограничиваем историю
            if len(chat_messages[room_url]) > 1000:
                chat_messages[room_url] = chat_messages[room_url][-1000:]
            
            # Отправляем сообщение всем в комнате
            emit('chat-message', chat_data, room=room_url)
            
        except Exception as e:
            logging.error(f"Ошибка обработки сообщения чата: {str(e)}")

    @socketio.on('leave-room')
    def handle_leave_room(data):
        """Выход из комнаты"""
        try:
            room_url = data.get('roomUrl')
            user_id = data.get('userId')
            
            if not room_url or not user_id:
                return
            
            if room_url in active_connections and user_id in active_connections[room_url]:
                user_info = active_connections[room_url].pop(user_id)
                leave_room(room_url)
                
                # Уведомляем других участников
                emit('user-left', {
                    'userId': user_id,
                    'userName': user_info.get('name', 'Участник')
                }, room=room_url)
                
                # Если комната пустая, удаляем ее
                if not active_connections[room_url]:
                    active_connections.pop(room_url, None)
                    chat_messages.pop(room_url, None)
                
                logging.info(f"Пользователь {user_id} покинул комнату {room_url}")
                
        except Exception as e:
            logging.error(f"Ошибка при выходе из комнаты: {str(e)}")