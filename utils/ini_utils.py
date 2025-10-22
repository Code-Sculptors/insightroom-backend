from configparser import ConfigParser
import os

config = ConfigParser()
folder = os.path.join(os.path.split(os.path.split(__file__)[0])[0], 'data/user_settings')

if not os.path.isdir(folder):
    os.mkdir(folder)

def create_user_setting_file(title: str) -> None:
    '''Создает файл настроек пользователя с заданным названием в папке data/user_settings
    Args: 
        title (str): название файла, который нужно создать'''
    config.add_section("Settings")
    config.add_section("Visual")
    config.add_section("Privacy")

    #TODO: Собрать файл с настройками пользователей
    ...

    with open(f'{folder}/{title}.ini', mode='w', encoding='utf-8') as file:
        config.write(file)

