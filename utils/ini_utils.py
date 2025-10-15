from configparser import ConfigParser
import os

config = ConfigParser()
if not os.path.isdir('./data/user_settings'):
    os.mkdir('./data/user_settings')

def create_user_setting_file(title: str) -> None:
    '''Создает файл настроек пользователя с заданным названием в папке data/user_settings
    Args: 
        title (str): название файла, который нужно создать'''
    config.add_section("Settings")
    config.add_section("Visual")
    config.add_section("Privacy")

    #TODO: Собрать файл с настройками пользователей
    ...

    with open(f'./data/user_settings/{title}.ini', mode='w', encoding='utf-8') as file:
        config.write(file)

