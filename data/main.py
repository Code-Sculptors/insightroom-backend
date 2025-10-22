import psycopg2
from psycopg2 import connect
from datetime import datetime


class User:
    def __init__(self, user_id=None, username=None, avatar_url=None, email=None,
                 phone=None, last_online=None, settings_file=None, verified=False):
        self.user_id = user_id
        self.username = username
        self.avatar_url = avatar_url
        self.email = email
        self.phone = phone
        self.last_online = last_online
        self.settings_file = settings_file
        self.verified = verified

    def __str__(self) -> str:
        """Строковое представление класса"""
        return f"User(user_id={self.user_id}, username={self.username}, avatar_url={self.avatar_url}, email={self.email}, phone={self.phone})"


class Notification:
    def __init__(self, notification_id=None, notification_time=None, description=None, room_url=None):
        self.notification_id = notification_id
        self.notification_time = notification_time
        self.description = description
        self.room_url = room_url


class Contact:
    def __init__(self, contact_id=None, user_id=None, contact_name=None):
        self.user_id = user_id
        self.contact_id = contact_id
        self.contact_name = contact_name


class RoomInfo:
    def __init__(self, room_id=None, description=None, room_name=None, room_url=None):
        self.room_id = room_id
        self.description = description
        self.room_name = room_name
        self.room_url = room_url


class Room:
    def __init__(self, room_id=None, activation_time=None, message_file=None, settings_file=None):
        self.room_id = room_id
        self.activation_time = activation_time
        self.message_file = message_file
        self.settings_file = settings_file


class UserRole:
    def __init__(self, room_id=None, user_id=None, user_role=None, join_time=None, leave_time=None):
        self.room_id = room_id
        self.user_id = user_id
        self.user_role = user_role
        self.join_time = join_time
        self.leave_time = leave_time

class UserAndRoom:
    def __init__(self, user_id=None, room_id = None):
        self.user_id = user_id
        self.room_id = room_id

class UserAndNotif:
    def __init__(self, user_id=None, notification_id = None):
        self.user_id = user_id
        self.notification_id = notification_id

class Auth:
    def __init__(self, user_id=None, login=None, hash=None):
        self.user_id = user_id
        self.login = login
        self.hash = hash

    def __str__(self) -> str:
        """Строковое представление класса"""
        return f'Auth(user_id={self.user_id}, login={self.login}, hash={self.hash})'


class File:
    def __init__(self, file_id=None, file_path=None):
        self.file_id = file_id
        self.file_path = file_path


class Tokens:
    def __init__(self, token=None, expiration_time=None):
        self.token = token
        self.expiration_time = expiration_time


class DataBaseException(Exception):
    pass


class DataBase:
    '''По сути статический класс для работы с БД'''
    dbname = None
    host = None
    user = None
    password = None
    port = None


    def __init__(self, dbname="my_test", host="localhost", user="aliska", password="boss", port="5432"):
        self.setup_db_connection(dbname, host, user, password, port)

    @classmethod
    def setup_db_connection(cls, dbname="my_test", host="localhost", user="aliska", password="boss", port="5432"):
        cls.dbname = dbname
        cls.host = host
        cls.user = user
        cls.password = password
        cls.port = port


    def __init__(self, dbname = "my_test", host = "localhost", user = "aliska", password = "boss", port = "5432"):
        if dbname:
            DataBase.dbname = dbname
        if host:
            DataBase.host = host
        if user:
            DataBase.user = user
        if password:
            DataBase.password = password
        if port:
            DataBase.port = port

    @classmethod
    def get_connection(cls):
        """
        Создает и возвращает соединение с базой данных

        Returns:
            psycopg2.connection: объект соединения с БД
        """
        return psycopg2.connect(
            dbname=cls.dbname,
            host=cls.host,
            user=cls.user,
            password=cls.password,
            port=cls.port
        )

    @staticmethod
    def get_user(user_id: int) -> User | None:
        """
        Возвращает объект пользователя по его идентификатору
        Args:
            user_id (int): ID пользователя, объект которого хотим получить
        Returns:
            User: искомый пользователь, если найдена такая запись
            None: если запись о пользователе не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users.users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()

            if result:
                return User(*result)
            else:
                return None
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_users()-> list[User]:
        """
        Возвращает список всех пользователей

        Returns:
            list[User]: список объектов User, пустой, если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users.users")
            results = cursor.fetchall()
            if results:
                return [User(*row) for row in results]
            else:
                return []
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_user(user_id: int) -> None:
        """
        Удаляет пользователя из базы данных
        Args:
            user_id (int): user_id для удаления
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users.users WHERE user_id = %s", (user_id,))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def update_user(user: User) -> None:
        """
        Обновляет данные пользователя в базе данных

        Args:
            user (User): объект User с установленным user_id и новыми данными
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users.users 
                SET username=%s, avatar_url=%s, email=%s, phone=%s, 
                    last_online=%s, settings_file=%s, verified=%s 
                WHERE user_id=%s
            """, (user.username, user.avatar_url, user.email, user.phone,
                  user.last_online, user.settings_file, user.verified, user.user_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def add_user(user: User) -> None:
        """
        Добавляет нового пользователя в базу данных

        Args:
            user (User): объект User с данными для добавления и установленным user_id
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users.users 
                (user_id, username, avatar_url, email, phone, last_online, settings_file, verified) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user.user_id, user.username, user.avatar_url, user.email, user.phone,
                  user.last_online, user.settings_file, user.verified))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_notification(notification_id: int) -> Notification | None:
        """
        Возвращает объект уведомления по его идентификатору

        Args:
            notification_id (int): id уведомления, которое нужно получить

        Returns:
            Notification: искомое уведомление, если найдена запись
            None: если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users.notification WHERE notification_id = %s",
                           (notification_id,))
            result = cursor.fetchone()

            if result:
                return Notification(*result)
            else:
                return None
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_notifications() -> list[Notification]:
        """
        Возвращает список всех уведомлений

        Returns:
            list[Notification]: список объектов Notification
            list: пустой список, если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users.notification")
            results = cursor.fetchall()
            if results:
                return [Notification(*row) for row in results]
            else:
                return []
        except Exception as ex:
            raise DataBaseException(ex)

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_notification(notification_id: int) -> None:
        """
        Удаляет уведомление по id из базы данных

        Args:
            notification_id (int): ID уведомнения, которое нужно удалить
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users.notification WHERE notification_id = %s", (notification_id,))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def update_notification(notification: Notification) -> None:
        """
        Обновляет данные уведомления в базе данных

        Args:
            notification (Notification): объект Notification с установленным notification_id и новыми данными
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                    UPDATE users.notification 
                    SET notification_time=%s, description=%s, room_url=%s
                    WHERE notification_id=%s
                """, (notification.notification_time, notification.description, notification.room_url,
                      notification.notification_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def add_notification(notification: Notification) -> int|None:
        """
        Добавляет новое уведомление в базу данных

        Args:
            notification (Notification): объект Notification с данными для добавления
        Returns:
             (int | None): возвращает ID созданного уведомления или None, в случае ошибки
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                    INSERT INTO users.notification 
                    (notif_datetime, description, room_url) 
                    VALUES (%s, %s, %s)
                    RETURNING notification_id
                """, (notification.notification_time, notification.description, notification.room_url))
            notification_id = cursor.fetchone()[0]
            conn.commit()
            return notification_id
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_contact(contact_id: int) -> Contact | None:
        """
        Возвращает объект контакта по его идентификатору

        Args:
            contact_id (int): ID контакта, который нужно получить

        Returns:
            Contact: искомый контакт, если найдена запись
            None: если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users.contacts WHERE contact_id = %s", (contact_id,))
            result = cursor.fetchone()

            if result:
                return Contact(*result)
            else:
                return None
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        # def get_user_contact(user_id: int) -> list[Contact]:
        #     """
        #     Возвращает объект список контактов для юзера по его идентификатору user_id
        #
        #     Args:
        #         user_id (int): ID пользователя,для которого нужно получить список контактов
        #
        #     Returns:
        #         list[Contact]: искомый список контактов, если они найдены
        #     """
        #     conn = None
        #     cursor = None
        #     try:
        #         conn = DataBase.get_connection()
        #         cursor = conn.cursor()
        #         cursor.execute("SELECT * FROM users.contacts WHERE user_id = %s", (user_id,))
        #         results = cursor.fetchall()
        #         if results:
        #             return [Contact(*row) for row in results]
        #         else:
        #             return []
        #     except Exception as ex:
        #         raise DataBaseException(ex)
        #     finally:
        #         if cursor:
        #             cursor.close()
        #         if conn:
        #             conn.close()

    @staticmethod
    def get_all_contacts() -> list[Contact]:
        """
        Возвращает список всех контактов

        Returns:
            list[Contact]: список объектов Contact
            list: пустой список, если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users.contacts")
            results = cursor.fetchall()
            if results:
                return [Contact(*row) for row in results]
            else:
                return []
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def update_contact(contact: Contact) -> None:
        """
        Обновляет данные контакта в базе данных

        Args:
            contact (Contact): объект Contact с установленным contact_id и новыми данными
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users.contacts 
                SET user_id=%s, contact_name=%s
                WHERE contact_id=%s
            """, (contact.user_id, contact.contact_name, contact.contact_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def add_contact(contact: Contact) -> int|None:
        """
        Добавляет новый контакт в базу данных

        Args:
            contact (Contact): объект Contact с данными для добавления
        Returns:
            (int|None): возвращает ID созданного контакта или None, в случае ошибки
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users.contacts 
                (user_id, contact_name) 
                VALUES (%s, %s)
                RETURNING contact_id
            """, (contact.user_id, contact.contact_name))
            contact_id = cursor.fetchone()[0]
            conn.commit()
            return contact_id
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_contact(contact: Contact) -> None:
        """
        Удаляет контакт из базы данных

        Args:
            contact (Contact): объект Contact с установленным contact_id для удаления
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users.contacts WHERE contact_id = %s", (contact.contact_id,))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_room(room_id: int) -> Room | None:
        """
        Возвращает объект комнаты по его идентификатору

        Args:
            room_id (int): ID комнаты, объект которой нужно получить

        Returns:
            Room: искомая комната, если найдена запись
            None: если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms.rooms WHERE room_id = %s", (room_id,))
            result = cursor.fetchone()

            if result:
                return Room(*result)
            else:
                return None
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_rooms() -> list[Room]:
        """
        Возвращает список всех комнат

        Returns:
            list[Room]: список объектов Room
            list: пустой список, если запись не найена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms.rooms")
            results = cursor.fetchall()
            if results:
                return [Room(*row) for row in results]
            else:
                return []
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def update_room(room: Room) -> None:
        """
        Обновляет данные комнаты в базе данных

        Args:
            room (Room): объект Room с установленным room_id и новыми данными
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE rooms.rooms 
                SET activation_time=%s, message_file=%s, settings_file=%s 
                WHERE room_id=%s
            """, (room.activation_time, room.message_file, room.settings_file, room.room_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def add_room(room: Room) -> int|None:
        """
        Добавляет новую комнату в базу данных

        Args:
            room (Room): объект Room с данными для добавления
        Returns:
            (int|None): возвращает ID созданной комнаты или None, в случае ошибки
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                    INSERT INTO rooms.rooms 
                    (activation_time, message_file, settings_file) 
                    VALUES (%s, %s, %s)
                    RETURNING room_id
                """, (room.activation_time, room.message_file, room.settings_file))
            room_id = cursor.fetchone()[0]
            conn.commit()
            return room_id
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_room(room_id: int) -> None:
        """
        Удаляет комнату из базы данных

        Args:
            room_id (int): установленный room_id для удаления объекта комнаты
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rooms.rooms WHERE room_id = %s", (room_id,))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_room_info(room_id: int) -> RoomInfo | None:
        """
        Возвращает объект информации о комнате по его идентификатору

        Args:
            room_id (int): ID комнаты, информацию о которой нужно получить

        Returns:
            RoomInfo: искомая информация о комнате, если найдена запись
            None: если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms.rooms_info WHERE room_id = %s", (room_id,))
            result = cursor.fetchone()

            if result:
                return RoomInfo(*result)
            else:
                return None
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_rooms_info() -> list[RoomInfo]:
        """
        Возвращает список всей информации о комнатах

        Returns:
            list[RoomInfo]: список объектов RoomInfo
            list: пустой список, если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms.rooms_info")
            results = cursor.fetchall()
            if results:
                return [RoomInfo(*row) for row in results]
            else:
                return []
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def update_room_info(room_info: RoomInfo) -> None:
        """
        Обновляет информацию о комнате в базе данных

        Args:
            room_info (RoomInfo): объект RoomInfo с установленным room_id и новыми данными
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                   UPDATE rooms.rooms_info 
                   SET description=%s, room_name=%s, room_url=%s 
                   WHERE room_id=%s
               """, (room_info.description, room_info.room_name, room_info.room_url, room_info.room_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def add_room_info(room_info: RoomInfo) -> None:
        """
        Добавляет новую информацию о комнате в базу данных

        Args:
            room_info (RoomInfo): объект RoomInfo с данными для добавления и установленным room_id
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                    INSERT INTO rooms.rooms_info 
                    (room_id, description, room_name, room_url) 
                    VALUES (%s,%s, %s, %s)
                """, (room_info.room_id,room_info.description, room_info.room_name, room_info.room_url))
            #room_info.room_id = cursor.fetchone()[0]
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_room_info(room_id: int) -> None:
        """
        Удаляет информацию о комнате из базы данных

        Args:
            room_id (int): ID комнаты, объект которой нужно удалить

        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rooms.rooms_info WHERE room_id = %s", (room_id,))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    #####ПОСМОТРЕТЬ SQL ЗАПРОС ЕСЛИ ПЕРЕДАВАТЬ ЮЗЕРА А НЕ ЮЗЕРРОЛ
    @staticmethod
    def get_user_role(user_role: UserRole) -> UserRole | None:
        """
        Возвращает объект роли пользователя по идентификаторам комнаты и пользователя

        Args:
            user_role (UserRole): объект UserRole с установленными room_id и user_id

        Returns:
            UserRole: искомая роль пользователя, если найдена запись
            None: если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms.user_roles WHERE room_id = %s AND user_id = %s",
                           (user_role.room_id, user_role.user_id))
            result = cursor.fetchone()

            if result:
                return UserRole(*result)
            else:
                return None
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_user_roles() -> list[UserRole]:
        """
        Возвращает список всех ролей пользователей

        Returns:
            list[UserRole]: список объектов UserRole
            list: пустой список, если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms.user_roles")
            results = cursor.fetchall()
            return [UserRole(*row) for row in results]
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def update_user_role(user_role: UserRole) -> None:
        """
        Обновляет роль пользователя в базе данных

        Args:
            user_role (UserRole): объект UserRole с установленными room_id, user_id и новыми данными
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE rooms.user_roles 
                SET user_role=%s, join_time=%s, leave_time=%s 
                WHERE room_id=%s AND user_id=%s
            """, (user_role.user_role, user_role.join_time, user_role.leave_time,
                  user_role.room_id, user_role.user_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def add_user_role(user_role: UserRole) -> None:
        """
        Добавляет новую роль пользователя в базу данных

        Args:
            user_role (UserRole): объект UserRole с данными для добавления и установленными user_id, room_id
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rooms.user_roles 
                (room_id, user_id, user_role, join_time, leave_time) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user_role.room_id, user_role.user_id, user_role.user_role,
                  user_role.join_time, user_role.leave_time))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod  ###тоже посмотреть с джоином
    def delete_user_role(user_role: UserRole) -> None:
        """
        Удаляет роль пользователя из базы данных

        Args:
            user_role (UserRole): объект UserRole с установленными room_id и user_id для удаления
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rooms.user_roles WHERE room_id = %s AND user_id = %s",
                           (user_role.room_id, user_role.user_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    #######ПРО ПАРОЛЬ ПОСМОТРЕТЬ

    @staticmethod
    def get_auth(user_id: int) -> Auth | None:
        """
        Возвращает объект аутентификации по идентификатору пользователя

        Args:
            user_id (int): ID пользователя, объект Auth которого нужно получить


        Returns:
            Auth: искомая запись аутентификации, если найдена
            None: если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM technical.auth WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()

            if result:
                return Auth(*result)
            else:
                return None
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_auth() -> list[Auth]:
        """
        Возвращает список всех записей аутентификации

        Returns:
            list[Auth]: список объектов Auth
            list: пустой список, если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM technical.auth")
            results = cursor.fetchall()
            if results:
                return [Auth(*row) for row in results]
            else:
                return []
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def update_auth(auth: Auth) -> None:
        """
        Обновляет данные аутентификации в базе данных

        Args:
            auth (Auth): объект Auth с установленным user_id и новыми данными
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE technical.auth 
                SET login=%s, hash=%s 
                WHERE user_id=%s
            """, (auth.login, auth.hash, auth.user_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod  ## not change yet ТУТ ПАРОЛЬ
    def add_auth(auth: Auth) -> int | None:
        """
        Добавляет новую запись аутентификации в базу данных

        Args:
            auth (Auth): объект Auth с данными для добавления
        Returns:
            (int | None): возвращает ID созданного пользователя или None, в случае ошибки
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO technical.auth 
                (login, password) 
                VALUES ( %s, %s)
                RETURNING user_id
            """, (auth.login, auth.hash))
            user_id = cursor.fetchone()[0]  # fetchone МНОЖЕСТВО ИЗ ОДНОГО ЭЛЕМНТА ВОЗВРАЩАЕТ БЛИН
            conn.commit()
            return user_id
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_auth(user_id: int) -> None:
        """
        Удаляет запись аутентификации из базы данных

        Args:
            user_id (int): установленныq user_id для удаления объекта Auth
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM technical.auth WHERE user_id = %s", (user_id,))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_token(token: Tokens) -> Tokens | None:
        """
        Возвращает объект токена по его значению

        Args:
            token (Tokens): объект Tokens с установленным token

        Returns:
            Tokens: искомый токен, если найдена запись
            None: если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM technical.tokens WHERE token = %s", (token.token,))
            result = cursor.fetchone()

            if result:
                return Tokens(*result)
            else:
                return None
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_tokens() -> list[Tokens]:
        """
        Возвращает список всех токенов

        Returns:
            list[Tokens]: список объектов Tokens
            list: пустой список, если токен не найден
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM technical.tokens")
            results = cursor.fetchall()
            if results:
                return [Tokens(*row) for row in results]
            else:
                return []
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def is_token_expired(token: str) -> tuple[bool, dict]:
        """
        Проверяет, просрочен ли токен на основе данных из базы данных

        Args:
            token (str): Токен для проверки

        Returns:
            bool: True если токен просрочен или не найден, False если токен валиден
            dict: Дополнительная информация о статусе токена
        """

        error_info = {
            'is_expired': True,
            'error_type': None,
            'message': '',
            'expiration_time': None,
            'token_found': False
        }

        try:
            token_obj = Tokens(token=token)

            found_token = DataBase.get_token(token_obj)

            if not found_token:
                error_info.update({
                    'error_type': 'TOKEN_NOT_FOUND',
                    'message': 'Токен не найден в базе данных'
                })
                return True, error_info

            error_info['token_found'] = True
            error_info['expiration_time'] = found_token.expiration_time

            if found_token.expiration_time is None:
                error_info.update({
                    'error_type': 'NO_EXPIRATION_TIME',
                    'message': 'Токен не имеет установленного времени expiration'
                })
                return True, error_info
            current_time = datetime.now()

            if current_time > found_token.expiration_time:
                error_info.update({
                    'error_type': 'TOKEN_EXPIRED',
                    'message': f'Токен просрочен. Время истечения: {found_token.expiration_time}'
                })
                return True, error_info
            else:
                error_info.update({
                    'is_expired': False,
                    'error_type': None,
                    'message': 'Токен валиден',
                    'time_remaining': found_token.expiration_time - current_time
                })
                return False, error_info

        except Exception as ex:
            raise DataBaseException(ex)

    @staticmethod
    def delete_token(token: Tokens) -> None:
        """
        Удаляет токен из базы данных

        Args:
            token (Tokens): объект Tokens с установленным token для удаления
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM technical.tokens WHERE token = %s", (token.token,))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # @staticmethod
    # def update_token(token: Tokens) -> None:
    #     """
    #     Обновляет данные токена в базе данных
    #
    #     Args:
    #         token (Tokens): объект Tokens с установленным token и новыми данными
    #     """
    #     conn = None
    #     cursor = None
    #     try:
    #         conn = DataBase.get_connection()
    #         cursor = conn.cursor()
    #         cursor.execute("""
    #             UPDATE technical.tokens
    #             SET expiration_time=%s
    #             WHERE token=%s
    #         """, (token.expiration_time, token.token))
    #         conn.commit()
    #     except Exception as ex:
    #         raise DataBaseException(ex)
    #     finally:
    #         if cursor:
    #             cursor.close()
    #         if conn:
    #             conn.close()

    @staticmethod
    def add_token(token: Tokens) -> None:
        """
        Добавляет новый токен в базу данных

        Args:
            token (Tokens): объект Tokens с данными для добавления
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO technical.tokens 
                (token, expiration_time) 
                VALUES (%s, %s)
            """, (token.token, token.expiration_time))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_file(file_id: int) -> File | None:
        """
        Возвращает объект файла по его идентификатору

        Args:
            file_id (int): ID файла, данные которого необходимо получить

        Returns:
            File: искомый файл, если найдена запись
            None: если запись не найдена
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM technical.files WHERE file_id = %s", (file_id,))
            result = cursor.fetchone()

            if result:
                return File(*result)
            else:
                return None
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_files() -> list[File]:
        """
        Возвращает список всех файлов

        Returns:
            list[File]: список объектов File
            list: пустой список, если файл не найден
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM technical.files")
            results = cursor.fetchall()
            if results:
                return [File(*row) for row in results]
            else:
                return []
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def update_file(file: File) -> None:
        """
        Обновляет данные файла в базе данных

        Args:
            file (File): объект File с установленным file_id и новыми данными
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                    UPDATE technical.files 
                    SET file_path=%s 
                    WHERE file_id=%s
                """, (file.file_path, file.file_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def add_file(file: File) -> int|None:
        """
        Добавляет новый файл в базу данных

        Args:
            file (File): объект File с данными для добавления
         Returns:
            (int|None): возвращает ID созданного файла или None, в случае ошибки
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                    INSERT INTO technical.files 
                    (file_path) 
                    VALUES (%s)
                    RETURNING file_id
                """, (file.file_path,))
            file_id = cursor.fetchone()[0]
            conn.commit()
            return file_id
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_file(file: File) -> None:
        """
        Удаляет файл из базы данных

        Args:
            file (File): объект File с установленным file_id для удаления
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM technical.files WHERE file_id = %s", (file.file_id,))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


    @staticmethod
    def add_user_and_room(user_id:int, room_id:int)->None:
        '''
            Создает объект, связывающий пользователя с комнатой по переданным ID
            Args:
                user_id(int): ID пользователя, которого связываем с комнатой
                room_id(int): ID комнаты, которую связываем с переданным пользователем

        '''
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                            INSERT INTO rooms.user_and_room 
                            (user_id, room_id) 
                            VALUES (%s, %s)
                        """, (user_id,room_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_user_and_room(user_id:int,  room_id:int) -> None:
        """
        Удаляет связь пользователя и комнаты

        Args:
            user_id(int): ID пользователя, которого связываем с комнатой
            room_id(int): ID комнаты, которую связываем с переданным пользователем

        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rooms.user_and_room WHERE room_id = %s AND user_id = %s",
                           (room_id, user_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def add_user_and_notif(user_id: int, notification_id: int) -> None:
        '''
            Создает объект, связывающий пользователя с комнатой по переданным ID
            Args:
                user_id(int): ID пользователя, которого связываем с уведомлением
                notification_id(int): ID уведомления, которое связываем с переданным пользователем

        '''
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                                INSERT INTO users.user_and_notif 
                                (user_id, notification_id) 
                                VALUES (%s, %s)
                            """, (user_id, notification_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def delete_user_and_notification(user_id: int, notification_id: int) -> None:
        """
        Удаляет связь пользователя и комнаты

        Args:
            user_id(int): ID пользователя, которого связываем с уведомлением
            notification_id(int): ID уведомления, которое связываем с переданным пользователем

        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rooms.user_and_notif WHERE notification_id = %s AND user_id = %s",
                           (notification_id, user_id))
            conn.commit()
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def serch_contact_id(email:str) -> int|None:
        """
        Ищет ID пользователя по установленной почте, которого хотим добавить в контакты

        Args:
            email(str): Почта пользователя, которого хотим добавить в контакты
        Returns:
            int: ID пользователя, если таковой найден
            None: если пользователя найти не удалось
        """
        conn = None
        cursor = None
        try:
            conn = DataBase.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users.users WHERE email = %s",(email,))
            user_id = cursor.fetchone()[0]
            return user_id
        except Exception as ex:
            raise DataBaseException(ex)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()





if __name__ == '__main__':
    DataBase.setup_db_connection(dbname='my_pi_db', host='10.147.19.249', user='khomek',
                                 password='pos86de34@T')
    '''id = DataBase.add_auth(Auth(login='test_login', hash='123'))
    print(type(id))
    DataBase.add_user(User(user_id=id, username='test_username', email='test@yandex.ru', phone='+79870742725', settings_file='user_test_login.ini'))'''
    '''id = DataBase.add_auth(Auth(user_id='None', login='JOJO', hash='7c6e5b6dcd5f3af8a3495cccf2a630964572840e3b2f61706be05dc0c988d8b5'))
    DataBase.add_user(User(user_id=id, username='JOJO', avatar_url=None, email='JOJO@JOJO.JOJO', phone='+79870742726'))'''
    # id = DataBase.add_auth(Auth(user_id=None, login='barbushka37', hash='pupupu'))
    # print(type(id))
    # DataBase.add_user(User(user_id=id, username='poh', email = 'fhhghhf@hhh', phone='555'))
    # au=DataBase.get_auth(id)
    # print(vars(au))

    #tok = Tokens('fhgjkdk', datetime.now())
    #DataBase.add_token(tok)
    #tok = DataBase.get_token(tok)
    #DataBase.is_token_expired(tok) чет фигня какая то потом подумаю
    #DataBase.delete_token(tok)

    # id = DataBase.add_file(File(file_id=None, file_path='users/swaga/hype'))
    # file = DataBase.get_file(file_id=id)
    # print(vars(file))
    # DataBase.delete_file(file)
    #DataBase.delete_file(File(file_id=1))

    #id = DataBase.add_auth(Auth(user_id=None, login='хихик', hash='pupupu'))
    #another_user = User(user_id=37, username='хихик', email='WW@w.com', phone='8(800)555-35-35')
    #DataBase.delete_auth(another_user.user_id)
    # new_room = Room(activation_time= datetime.now(),message_file= 'aaa',settings_file= 'хихик')
    # id_roo = DataBase.add_room(new_room)
    # #print(id_roo)
    # new_room.room_id=id_roo
    # new_room.activation_time = '3:33:33'
    # new_room.message = 'qqqq'
    # DataBase.update_room(new_room)
    # new_room_info = RoomInfo(room_id=new_room.room_id, description='хихик', room_name='тутту',room_url='hype')
    # DataBase.add_room_info(new_room_info)
    # new_room_info.description = 'rururruru'
    # DataBase.update_room_info(new_room_info)
    #пока нет соединения юзера с комнатой
    #
    # DataBase.add_user_and_room(user_id=another_user.user_id,room_id=new_room.room_id)
    # new_role = UserRole(room_id=new_room.room_id, user_id= another_user.user_id, user_role='хихик', join_time=datetime.now())
    # DataBase.add_user_role(new_role)

    #НЕ ПОЙМУ ПОЧЕМУ СТРАННО ОБНОВЛЯЕТ АЙДИШНИК В РУМ ИНФО ТИПА У МЕНЯ ОЗДАВАЛАС КОМНАТА С АЙДИШНИКОМ 9 А ИНФОРМАЦИЯ О НЕЙ БЫЛА ПОД 7 АЙДИШНИКОМ ПОЧЕМУ ТО

    #DataBase.delete_room(id_roo)
#КОНКРЕТНАЯ КОМНАТА
    #id = DataBase.add_auth(Auth(user_id=None, login='uuu', hash='pupupu'))
    #id_another = DataBase.add_auth(Auth(user_id=None, login='vvv', hash='яя'))
    #new_user = User(user_id=54, username='хихик', email='WW@w.com', phone='8(800)555-35-35')
   # DataBase.add_user(new_user)
    #another_user = User(user_id=55, username='дану', email='QQ@w.com', phone='8(800)555')
    #DataBase.add_user(another_user)
    #DataBase.delete_auth(another_user.user_id)
    #new_room = Room(activation_time= datetime.now(),message_file= 'комната страха',settings_file= 'окак')
    #id_room = DataBase.add_room(new_room)
    #new_room.room_id = 32
    #print(id_roo)

    # new_room_info = RoomInfo(room_id=new_room.room_id, description='хихик', room_name='тутту',room_url='hype')
    # DataBase.add_room_info(new_room_info)
    # new_room_info.description = 'rururruru'
    # DataBase.update_room_info(new_room_info)

    #DataBase.add_user_and_room(user_id=new_user.user_id,room_id=new_room.room_id)
    #DataBase.add_user_and_room(user_id=another_user.user_id,room_id=new_room.room_id)
    #new_role = UserRole(room_id=new_room.room_id, user_id= new_user.user_id, user_role='я главный', join_time=datetime.now())
    # DataBase.add_user_role(new_role)
    #another_role = UserRole(room_id=new_room.room_id, user_id= another_user.user_id, user_role='яяяяяяяя', join_time=datetime.now())
    # DataBase.add_user_role(another_role)
    # another_role = UserRole(room_id=new_room.room_id, user_id= another_user.user_id, user_role='дадада', join_time=datetime.now())
    # DataBase.update_user_role(another_role)
    #DataBase.delete_user_role(another_role)
    #DataBase.delete_user_and_room(another_user.user_id, new_room.room_id)

    #new_notif = Notification(notification_id=None, notification_time=datetime.now(), description='уведомляю', room_url='ссылаюсь')
    #id_notif = DataBase.add_notification(new_notif)
    #new_notif.notification_id=
    #DataBase.delete_user(another_user.user_id)
    #DataBase.delete_notification(new_notif.notification_id)
    #new_usernot = UserAndNotif(new_user.user_id,new_notif.id)
    # DataBase.add_user_and_notif(user_id=new_user.user_id, notification_id=new_notif.notification_id)
    # DataBase.add_user_and_notif(user_id=another_user.user_id,  notification_id=new_notif.notification_id)

    #Контакты
    # id = DataBase.add_auth(Auth(user_id=None, login='8', hash='pupupu'))
    # id_another = DataBase.add_auth(Auth(user_id=None, login='=', hash='яя'))
    # id_third = DataBase.add_auth(Auth(user_id=None, login='*', hash='tt'))
    #
    # new_user = User(user_id=id, username='хихик', email='g@w.com', phone='8(800)555-35-35')
    # DataBase.add_user(new_user)
    # another_user = User(user_id=id_another, username='дану', email='fp@w.com', phone='8(800)555')
    # DataBase.add_user(another_user)
    # third_user = User(user_id=id_third, username='дану', email='f-.com', phone='888888')
    # DataBase.add_user(third_user)
    #
    # id_want1 = DataBase.serch_contact_id(another_user.email)
    # new_contact = Contact(user_id=id_want1, contact_name='я хороший', contact_id=None)
    # id_newc = DataBase.add_contact(new_contact)
    # new_contact.contact_id=id_newc
    # id_want2 = DataBase.serch_contact_id(third_user.email)
    # sec_contact = Contact(user_id=id_want2, contact_name='я злой', contact_id=None)
    # id_trc = DataBase.add_contact(sec_contact)
    # sec_contact.contact_id=id_trc
    # sec_contact.contact_name='ben'
    # DataBase.update_contact(sec_contact)
    #
    # DataBase.delete_contact(new_contact)




    db = DataBase()
    new_user = User(user_id=6)
    new_user = db.get_user(new_user)
    new_user.username = 'www'
    db.update_user(new_user)
    if new_user:
        print(vars(new_user))

