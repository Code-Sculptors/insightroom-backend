import psycopg2
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

    @staticmethod
    def get_connection():
        return psycopg2.connect(
            dbname="my_test",
            host="localhost",
            user="aliska",
            password="boss",
            port="5432"
        )

    @staticmethod
    def get_user_by_id(user_id):
        conn = None
        cursor = None
        try:
            conn = User.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users.users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()

            if result:
                return User(*result)
            else:
                return None

        except Exception as ex:
            print(f"Ошибка при получении пользователя {user_id}: {ex}")
            return None

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_users():
        conn = User.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users.users")
            results = cursor.fetchall()
            return [User(*row) for row in results]
        except Exception:
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def delete_user_by_id(id):
        conn = User.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users.users WHERE user_id = %s", (id,))
            conn.commit()
        except Exception:
            return []
        finally:
            cursor.close()
            conn.close()

    def add_or_update_user(self):
        conn = User.get_connection()
        cursor = conn.cursor()
        if self.user_id:
            cursor.execute("""UPDATE users.users 
                   SET username=%s, avatar_url=%s, email=%s, phone=%s, 
                    last_online=%s, settings_file=%s, verified=%s 
                   WHERE user_id=%s
               """, (self.username, self.avatar_url, self.email, self.phone,
                     self.last_online, self.settings_file, self.verified, self.user_id))
        else:
            cursor.execute("""
                   INSERT INTO users.users 
                   (username, avatar_url, email, phone, last_online, settings_file, verified) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
               """, (self.username, self.avatar_url, self.email, self.phone,
                     self.last_online, self.settings_file, self.verified))
            self.user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
    def delete(self):
        if self.user_id:
            User.delete_user_by_id(self.user_id)
            self.user_id = None

    def update_last_online(self):
        self.last_online = datetime.now()
        self.add_or_update_user()


    # def add_user(self):
    # conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    # cursor = conn.cursor()
    # cursor.execute("INSERT INTO users.users VALUES(%s,%s, %s, %s, %s, %s,%s, %s)", (7 ,username, avatar_url, email, phone, last_online, settings_file, verified))
    # conn.commit()
    # cursor.close()
    # conn.close()

    #add_user('biba', 'eeed', 'ghjfk', '8(456)987-9900','2025-01-19 03:14:07.000', 'ddd','1')




#delete_user_id(7)

class Notification:
    def __init__(self, notification_id=None, notification_time=None, description=None, room_url=None):
        self.notification_id = notification_id
        self.notification_time = notification_time
        self.description = description
        self.room_url = room_url

    @staticmethod
    def get_connection():
        return psycopg2.connect(
            dbname="my_test",
            host="localhost",
            user="aliska",
            password="boss",
            port="5432"
        )
    @staticmethod
    def get_notif_id(id):
        conn =  Notification.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users.notification WHERE notification_id = %s", (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return Notification(*result)
        else:
            return None #ну типа по факту вроде можно без этого потому что фетчоне возвращает ноне

    @staticmethod
    def get_all_notific():
        conn = Notification.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users.notification")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [Notification(*row) for row in results]
        # else:
        #     print(f"Пользователь с ID {id} не найден")

    @staticmethod
    def delete_notific_id(id):
        conn = Notification.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users.notification WHERE notification_id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()

    def add_or_update_notif(self):
        conn = Notification.get_connection()
        cursor = conn.cursor()
        try:
            if self.notification_id:
                cursor.execute("""
                            UPDATE users.notification 
                            SET notification_time=%s, description=%s, room_url=%s
                            WHERE notification_id=%s
                        """, (self.notification_time, self.description, self.room_url, self.notification_id))
            else:
                cursor.execute("""
                            INSERT INTO users.notification 
                            (notification_time, description, room_url) 
                            VALUES (%s, %s, %s)
                        """, (self.notification_time, self.description, self.room_url))
                self.notification_id = cursor.fetchone()[0]
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении уведомления: {e}")
            return False
        finally:
            cursor.close()
            conn.close()




def get_contact_id(id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users.contacts WHERE contact_id = %s", (id,))
    result = cursor.fetchone()
    if result:
        print(result)
    else:
        print(f"Уведомление с ID {id} не найдено")
    cursor.close()
    conn.close()


def get_all_contacts():
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users.contacts")
    result = cursor.fetchall()
    if result:
        print(result)
    else:
        print(f"Пользователь с ID {id} не найден")

    cursor.close()
    conn.close()


def add_contact(user_id, contact_name):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users.contacts VALUES(default, %s, %s)", (user_id, contact_name))
    conn.commit()
    cursor.close()
    conn.close()


def delete_contact_id(id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users.contact WHERE contact_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_room_id(id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms.rooms WHERE room_id = %s", (id,))
    result = cursor.fetchone()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найдена")
    cursor.close()
    conn.close()


def get_all_rooms():
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms.rooms")
    result = cursor.fetchall()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найден")

    cursor.close()
    conn.close()


def add_room(activation_time, message_file, settings_file):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rooms.rooms VALUES(default, %s, %s)", (activation_time, message_file, settings_file))
    conn.commit()
    cursor.close()
    conn.close()


def delete_room_id(id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rooms.rooms WHERE room_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_rooms_info_id(id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms.rooms_info WHERE room_id = %s", (id,))
    result = cursor.fetchone()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найдена")
    cursor.close()
    conn.close()


def get_all_rooms_info():
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms.rooms_info")
    result = cursor.fetchall()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найден")

    cursor.close()
    conn.close()


def add_room(description, room_name, room_url):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rooms.rooms_info VALUES(default, %s, %s, %s)", (description, room_name, room_url))
    conn.commit()
    cursor.close()
    conn.close()


def delete_rooms_info_id(id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rooms.rooms_info WHERE room_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()


def get_user_role_id(user_id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms.user_roles WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найдена")
    cursor.close()
    conn.close()


def get_all_user_roles():
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms.user_roles")
    result = cursor.fetchall()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найден")

    cursor.close()
    conn.close()


def add_user_role(room_id, user_id, user_role, join_time, leave_time):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rooms.user_roles VALUES(%s, %s, %s, %s, %s)", (room_id,user_id, user_role, join_time, leave_time))
    conn.commit()
    cursor.close()
    conn.close()


def delete_user_role(room_id, user_id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rooms.user_roles WHERE room_id = %s and user_id = %s", (room_id,user_id))
    conn.commit()
    cursor.close()
    conn.close()


def get_auth_id(id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM technical.auth WHERE user_id = %s", (id,))
    result = cursor.fetchone()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найдена")
    cursor.close()
    conn.close()


def get_all_auth():
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM technical.auth")
    result = cursor.fetchall()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найден")

    cursor.close()
    conn.close()


def add_auth(login, password):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO technical.auth VALUES(default, %s, %s)", (login, password))
    conn.commit()
    cursor.close()
    conn.close()


def delete_auth(id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM technical.auth WHERE auth_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

# def get_token(id):
#     conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM rooms.rooms_info WHERE room_id = %s", (id,))
#     result = cursor.fetchone()
#     if result:
#         print(result)
#     else:
#         print(f"комната с ID {id} не найдена")
#     cursor.close()
#     conn.close()


def get_all_tokens():
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM technical.tokens")
    result = cursor.fetchall()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найден")

    cursor.close()
    conn.close()


def add_token(token, expirtion_time):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO technical.tokens VALUES( %s, %s)", (token, expirtion_time))
    conn.commit()
    cursor.close()
    conn.close()


def delete_token(token):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM technical.tokens WHERE token = %s", (token,))
    conn.commit()
    cursor.close()
    conn.close()

def get_file_id(id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM technical.files WHERE file_id = %s", (id,))
    result = cursor.fetchone()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найдена")
    cursor.close()
    conn.close()


def get_all_files():
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM technical.files")
    result = cursor.fetchall()
    if result:
        print(result)
    else:
        print(f"комната с ID {id} не найден")

    cursor.close()
    conn.close()


def add_file(file_path):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO technical.path VALUES(default, %s)", (file_path,))
    conn.commit()
    cursor.close()
    conn.close()


def delete_file(id):
    conn = psycopg2.connect(dbname="my_test", host="localhost", user="aliska", password="boss", port="5432")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM technical.files WHERE file_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()