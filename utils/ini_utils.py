from configparser import ConfigParser
import os

config = ConfigParser()
user_settings_folder = os.path.join(os.path.split(os.path.split(__file__)[0])[0], 'data/user_settings')
room_settings_folder = os.path.join(os.path.split(os.path.split(__file__)[0])[0], 'data/rooms_settings')
room_messages_folder = os.path.join(os.path.split(os.path.split(__file__)[0])[0], 'data/messages')

if not os.path.isdir(user_settings_folder):
    os.mkdir(user_settings_folder)
if not os.path.isdir(room_settings_folder):
    os.mkdir(room_settings_folder)
if not os.path.isdir(room_messages_folder):
    os.mkdir(room_messages_folder)

def create_user_setting_file(title: str) -> str:
    '''Создает файл настроек пользователя с заданным названием в папке data/user_settings
    Args: 
        title (str): название файла, который нужно создать
        Returns:
        filename (str): название файла с расширением'''
    try:
        config.add_section("Settings")
        config.add_section("Visual")
        config.add_section("Privacy")
    except Exception as ex:
        print(f'ERROR: {ex} in create_user_setting_file({title})')
 
    #TODO: Собрать файл с настройками пользователей
    ...

    with open(f'{user_settings_folder}/{title}.ini', mode='w', encoding='utf-8') as file:
        config.write(file)
    return f'{title}.ini'


def create_room_setting_file(title: str) -> str:
    '''Создает файл настроек пользователя с заданным названием в папке data/user_settings
    Args: 
        title (str): название файла, который нужно создать
    Returns:
        filename (str): название файла с расширением'''
    try:
        config.add_section("Settings")
        config.add_section("Visual")
        config.add_section("Privacy")
    except Exception as ex:
        print(f'ERROR: {ex} in create_room_setting_file({title})')
 
    #TODO: Собрать файл с настройками комнат
    ...

    with open(f'{room_settings_folder}/{title}.ini', mode='w', encoding='utf-8') as file:
        config.write(file)
    return f'{title}.ini'


def create_message_file(title: str) -> str:
    '''Создает файл настроек пользователя с заданным названием в папке data/user_settings
    Args: 
        title (str): название файла, который нужно создать
    Returns:
        filename (str): название файла с расширением'''
 
    #TODO: Собрать файл с настройками пользователей
    ...

    with open(f'{room_messages_folder}/{title}.MES', mode='w', encoding='utf-8') as file:
        config.write(file)
    return f'{title}.MES'
