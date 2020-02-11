# -*- coding: utf-8 -*-
import configparser
import os
import sqlite3
import time
import datetime
import vk_api
from vk_api import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from urllib.request import urlretrieve
from PIL import Image


def create_config(path, name):
    config = configparser.ConfigParser()
    config.add_section(name)
    config.set(name, 'group_token', 'value')
    config.set(name, 'group_id', 'value')
    config.set(name, 'api_ver', 'value')
    config.set(name, 'wait_time', 'value')
    config.set(name, 'img_format', 'value')
    config.set(name, 'database_update_time', 'value')
    config.set(name, 'vertical_frame_offset', 'value')
    with open(path, 'w') as config_file:
        config.write(config_file)


def get_config(path):
    if not os.path.exists(path):
        create_config(path, cfg_name)
        print(
            '[Бот] Файл конфигурации config.ini не был найден, поэтому создан заново.\n'
            'Откройте его и замените все value на ваши данные без ковычек и скобок.\n'
            'После этого можете заново запустить бота.')
        quit()
    config = configparser.ConfigParser()
    config.read(path)
    return config


def get_setting(path, section, setting):
    config = get_config(path)
    value = config.get(section, setting)
    return value


def rand():
    value = int(time.time())
    return value


def create_database(path):
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute('CREATE TABLE users (user_id integer, user_state integer, user_timeout integer, primary key (user_id))')
    con.commit()
    print('[БД] База данных не найдена и создана заново.')
    return con, cur


def get_database(path):
    if not os.path.exists(path):
        con, cur = create_database(path)
    else:
        con = sqlite3.connect(path)
        cur = con.cursor()
        print('[БД] Связь с базой данных установлена.')
    return con, cur


# Создание пользователя
def create_user_data_in_database(user_id, user_state):
    now = datetime.datetime.now()
    if now.hour == 23:
        now = now.replace(hour=0, day=now.day + 1)
    else:
        now = now.replace(hour=now.hour + 1)
    user_data = (user_state, now.strftime('%d/%m/%Y %H:%M:%S'))
    cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (user_id, user_data[0], user_data[1]))
    connection.commit()
    print('[БД] Создан новый пользователь:\nID: %s\nСостояние: %s\nТаймаут: %s' % (user_id, user_data[0], user_data[1]))
    return user_data


# Возвращает данные пользователя. Если пользователя не существует, создаётся новый пользователь с данным user_id
def get_user_data_from_database(user_id):
    user_data = cursor.execute('SELECT user_state, user_timeout FROM users WHERE user_id = ?', (user_id,)).fetchone()
    if user_data is None:
        user_data = create_user_data_in_database(user_id, 0)
    else:
        print('[БД] Найден существующий пользователь:\nID: %s\nСостояние: %s\nТаймаут: %s' % (
            user_id, user_data[0], user_data[1]))
    return user_data


# Изменение данных пользователя
def set_user_data_in_database(user_id, user_data):
    cursor.execute('UPDATE users SET user_state = ? WHERE user_id = ?', (user_data[0], user_id,))
    print('[БД] Изменен пользователь:\nID: %s\nСостояние: %s' % (user_id, user_data[0]))
    connection.commit()


def delete_users():
    users_data = cursor.execute('SELECT user_id, user_timeout FROM users ').fetchall()
    now = datetime.datetime.now()
    print('[БД] Обновление базы данных')
    for users in range(len(users_data)):
        print(users_data[users][1])
        if now > datetime.datetime.strptime(users_data[users][1], '%d/%m/%Y %H:%M:%S'):
            cursor.execute('DELETE FROM users WHERE user_id = ?', (users_data[users][0],))
            connection.commit()
            downloaded = 'downloads/' + str(users_data[users][0]) + '.' + img_format
            edited = 'edited/' + str(users_data[users][0]) + '.' + img_format
            if os.path.exists(downloaded):
                os.remove(downloaded)
            if os.path.exists(edited):
                os.remove(edited)
            print('[БД] Удалён пользователь:\nID:%s' % users_data[users][0])


def send_photo(vk, vk_upload, event, path, message, keyboard=None):
    photo = vk_upload.photo_messages(path, event.peer_id)
    if keyboard is None:
        vk.messages.send(user_id=event.user_id, message=message, attachment='photo%s_%s' % (photo[0]['owner_id'], photo[0]['id']), random_id=rand())
    elif keyboard is not None:
        vk.messages.send(user_id=event.user_id, message=message, attachment='photo%s_%s' % (photo[0]['owner_id'], photo[0]['id']), keyboard=keyboard.get_keyboard(), random_id=rand())


# обработка фото
def process_photo(event):
    original = Image.open('downloads/' + str(event.user_id) + '.' + img_format, 'r')
    frame = Image.open('frames/' + event.text + '.' + img_format, 'r')
    original = original.convert('RGBA')
    frame = frame.convert('RGBA')
    # изменение размеров фото и рамки в зависимости от размера фото
    new_original_size, new_frame_size = (), ()
    if original.size[0] > frame.size[0]:
        new_original_size = (frame.size[0], int(frame.size[0] * original.size[1] / original.size[0]))
        new_frame_size = frame.size
        original = original.resize(new_original_size, Image.BICUBIC)
    elif original.size[0] == frame.size[0]:
        new_original_size = original.size
        new_frame_size = frame.size
    elif original.size[0] < frame.size[0]:
        new_original_size = original.size
        new_frame_size = (original.size[0], int(original.size[0] * frame.size[1] / frame.size[0]))
        frame = frame.resize(new_frame_size, Image.BICUBIC)
    # смещение фото и рамки
    original_offset = (0, 0)
    frame_offset = (0, new_original_size[1] - vertical_frame_offset)
    # общее изображение для фото и рамки
    new_image_size = (new_original_size[0], new_original_size[1] + new_frame_size[1] - vertical_frame_offset)
    new_image = Image.new('RGBA', new_image_size, (255, 255, 255, 0))
    new_image.paste(original, original_offset)
    new_image.paste(frame, frame_offset, mask=frame)
    new_image.save('edited/' + str(event.user_id) + '.' + img_format)
    original.close()
    frame.close()
    new_image.close()


# Основная функция
def main(timer):
    vk_session = vk_api.VkApi(token=group_token, api_version=api_ver)
    # vk_session.auth_token(reauth=False)
    vk_longpoll = VkLongPoll(vk=vk_session, group_id=group_id, wait=wait_time)
    # КЛАВИАТУРЫ
    # state = 0
    vk_keyboard_0 = VkKeyboard(one_time=False)
    vk_keyboard_0.add_button('Начать', color=VkKeyboardColor.PRIMARY)
    # state = 1
    vk_keyboard_1 = VkKeyboard(one_time=False)
    vk_keyboard_1.add_button('Да, конечно!', color=VkKeyboardColor.PRIMARY)
    professions1 = ('Вожатые', 'Проводники', 'Сервис')
    professions2 = ('Мед. отряды', 'Сельхоз', 'Строители')
    commons = ('Общая 1', 'Общая 2', 'Общая 3')
    back = 'Назад'
    get_avatar = 'Хочу себе аватарку!🔥'
    entry_advice = 'Есть несколько фоторамок.\nПосмотри заранее, как будет выглядеть ' \
                   'твоя аватарка с той или иной рамкой, а потом нажми кнопку «Хочу себе аватарку!🔥»'
    vk_keyboard_2 = VkKeyboard(one_time=False)
    vk_keyboard_4 = VkKeyboard(one_time=False)
    for button_name in professions1:
        vk_keyboard_2.add_button(button_name, color=VkKeyboardColor.POSITIVE)
        vk_keyboard_4.add_button(button_name, color=VkKeyboardColor.POSITIVE)
    vk_keyboard_2.add_line()
    vk_keyboard_4.add_line()
    for button_name in professions2:
        vk_keyboard_2.add_button(button_name, color=VkKeyboardColor.POSITIVE)
        vk_keyboard_4.add_button(button_name, color=VkKeyboardColor.POSITIVE)
    vk_keyboard_2.add_line()
    vk_keyboard_4.add_line()
    for button_name in commons:
        vk_keyboard_2.add_button(button_name, color=VkKeyboardColor.DEFAULT)
        vk_keyboard_4.add_button(button_name, color=VkKeyboardColor.DEFAULT)
    vk_keyboard_2.add_line()
    vk_keyboard_2.add_button(get_avatar, color=VkKeyboardColor.PRIMARY)
    vk_keyboard_2.add_line()
    vk_keyboard_2.add_button(back, color=VkKeyboardColor.NEGATIVE)
    vk_keyboard_4.add_line()
    vk_keyboard_4.add_button(back, color=VkKeyboardColor.NEGATIVE)
    vk_keyboard_3 = VkKeyboard(one_time=False)
    vk_keyboard_3.add_button('Не кнопки жми, а фото отправляй!', color=VkKeyboardColor.DEFAULT)
    vk_keyboard_3.add_line()
    vk_keyboard_3.add_button(back, color=VkKeyboardColor.NEGATIVE)
    vk_keyboard_5 = VkKeyboard(one_time=False)
    vk_keyboard_5.add_button('Попробовать другую', color=VkKeyboardColor.POSITIVE)
    vk_keyboard_5.add_line()
    vk_keyboard_5.add_button(back, color=VkKeyboardColor.NEGATIVE)
    # КЛАВИАТУРЫ
    vk = vk_session.get_api()
    vk_upload = VkUpload(vk=vk_session)
    for event in vk_longpoll.listen():
        if time.time() - timer > database_update_time:
            delete_users()
            timer = time.time()
        if event.type == VkEventType.MESSAGE_NEW:
            if not event.from_me and event.from_user:
                user_data = get_user_data_from_database(event.user_id)
                print('[Бот] Получено сообщение от пользователя:\nID: %s\nТекст: %s\nСостояние: %s'
                      % (event.user_id, event.message, user_data[0]))
                # USER_STATE = 0
                if user_data[0] == 0:
                    if event.text == 'Начать':
                        vk.messages.send(user_id=event.user_id, message='Привет! Хочешь аватарку в стиле «Дня РСО»?', keyboard=vk_keyboard_1.get_keyboard(), random_id=rand())
                        set_user_data_in_database(user_id=event.user_id, user_data=(1,))
                    else:
                        vk.messages.send(user_id=event.user_id, message='Напиши или нажми кнопку «Начать», чтобы начать переписку со мной.', random_id=rand())
                # USER_STATE = 1
                elif user_data[0] == 1:
                    if event.text == 'Да, конечно!':
                        vk.messages.send(user_id=event.user_id, message=entry_advice, keyboard=vk_keyboard_2.get_keyboard(), random_id=rand())
                        set_user_data_in_database(user_id=event.user_id, user_data=(2,))
                    else:
                        vk.messages.send(user_id=event.user_id, message='Нажми кнопку «Да, конечно!», чтобы продолжить.', random_id=rand())
                # USER_STATE = 2
                elif user_data[0] == 2:
                    if event.text in professions1 or event.text in professions2 or event.text in commons:
                        send_photo(vk=vk, vk_upload=vk_upload, event=event, path='examples/' + event.text + '.' + img_format, message='Пример фото с рамкой  «' + event.text + '»')
                    elif event.text == get_avatar:
                        vk.messages.send(user_id=event.user_id,
                                         message='Прекрасно! Всё очень просто: отправь нам свою фотографию (вертикальную) '
                                                 'и выбери кнопкой нужную тебе рамку. Если всё хорошо - ты получишь новую аватарку!\n'
                                                 'Отправляй нам скорее фото!', keyboard=vk_keyboard_3.get_keyboard(), random_id=rand())
                        set_user_data_in_database(user_id=event.user_id, user_data=(3,))
                    elif event.text == back:
                        vk.messages.send(user_id=event.user_id, message='Пока!', keyboard=vk_keyboard_0.get_keyboard(), random_id=rand())
                        set_user_data_in_database(user_id=event.user_id, user_data=(0,))
                    elif event.attachments:
                        vk.messages.send(user_id=event.user_id, message='Не торопись. Сначала нажми кнопку «Хочу себе аватарку!🔥»', random_id=rand())
                    else:
                        vk.messages.send(user_id=event.user_id, message='Используй кнопки клавиатуры, чтобы взаимодействовать со мной.', random_id=rand())
                # USER_STATE = 3
                elif user_data[0] == 3:
                    if event.attachments:
                        print('Получено сообщение с медиа вложением.\nID:{}\nТип вложения:\n{}'.format(event.user_id, event.attachments['attach1_type']))
                        if event.attachments['attach1_type'] == 'photo':
                            if len(vk.messages.getById(message_ids=event.message_id)['items'][0]['attachments']) > 1:
                                vk.messages.send(user_id=event.user_id,
                                                 message='Ты отправил(а) мне несколько фото. Я возьму первое из них.',
                                                 random_id=rand())
                            message = vk.messages.getById(message_ids=event.message_id)
                            # photo_size = (int(message['items'][0]['attachments'][0]['photo']['sizes'][4]['width']),
                            #               int(message['items'][0]['attachments'][0]['photo']['sizes'][4]['height']))
                            # print('Размер фото (ширина, высота):\n' + str(photo_size))
                            photo_url = message['items'][0]['attachments'][0]['photo']['sizes'][4]['url']
                            photo_path = 'downloads/' + str(event.user_id) + '.' + img_format
                            urlretrieve(photo_url, photo_path)
                            original = Image.open(photo_path)
                            if original.size[1] <= original.size[0]:
                                original.close()
                                if os.path.exists(photo_path):
                                    os.remove(photo_path)
                                vk.messages.send(user_id=event.user_id,
                                                 message='Ты отправил(а) мне не вертикальное фото. Фото считается вертикальным,'
                                                         ' если его ширина меньше высоты. Попробуй ещё раз.',
                                                 keyboard=vk_keyboard_3.get_keyboard(), random_id=rand())
                                set_user_data_in_database(user_id=event.user_id, user_data=(3,))
                            elif original.size[1] > original.size[0]:
                                vk.messages.send(user_id=event.user_id,
                                                 message='Фотография была успешно загружена! Осталось выбрать, какую фоторамку использовать.',
                                                 keyboard=vk_keyboard_4.get_keyboard(), random_id=rand())
                                set_user_data_in_database(user_id=event.user_id, user_data=(4,))
                        elif not (event.attachments['attach1_type'] == 'photo'):
                            vk.messages.send(user_id=event.user_id,
                                             message='Ты отправил(а) мне что-то другое. Отправь мне фото.',
                                             random_id=rand())
                    elif event.text == back:
                        vk.messages.send(user_id=event.user_id, message=entry_advice, keyboard=vk_keyboard_2.get_keyboard(), random_id=rand())
                        set_user_data_in_database(user_id=event.user_id, user_data=(2,))
                    else:
                        vk.messages.send(user_id=event.user_id, message='Я жду от тебя фото.', random_id=rand())
                # USER_STATE = 4
                elif user_data[0] == 4:
                    if event.text in professions1 or event.text in professions2 or event.text in commons:
                        process_photo(event=event)
                        send_photo(vk=vk, vk_upload=vk_upload, event=event, path='edited/' + str(event.user_id) + '.' + img_format, message='Аватарка готова!\nМожно попробовать с другой рамочкой, если хочется, конечно.', keyboard=vk_keyboard_5)
                        set_user_data_in_database(user_id=event.user_id, user_data=(5,))
                    elif event.text == back:
                        vk.messages.send(user_id=event.user_id, message=entry_advice, keyboard=vk_keyboard_2.get_keyboard(), random_id=rand())
                        set_user_data_in_database(user_id=event.user_id, user_data=(2,))
                    else:
                        vk.messages.send(user_id=event.user_id, message='Используй кнопки клавиатуры, чтобы взаимодействовать со мной.', random_id=rand())
                # USER_STATE = 5
                elif user_data[0] == 5:
                    if event.text == 'Попробовать другую':
                        vk.messages.send(user_id=event.user_id, message='Выбери, какую фоторамку использовать.', keyboard=vk_keyboard_4.get_keyboard(), random_id=rand())
                        set_user_data_in_database(user_id=event.user_id, user_data=(4,))
                    elif event.text == back:
                        vk.messages.send(user_id=event.user_id, message=entry_advice, keyboard=vk_keyboard_2.get_keyboard(), random_id=rand())
                        set_user_data_in_database(user_id=event.user_id, user_data=(2,))
                    else:
                        vk.messages.send(user_id=event.user_id, message='Используй кнопки клавиатуры, чтобы взаимодействовать со мной.', random_id=rand())


# Начало
if __name__ == '__main__':
    cfg_path = 'config.ini'
    cfg_name = 'Group bot config'
    group_token = get_setting(cfg_path, cfg_name, 'group_token')
    group_id = int(get_setting(cfg_path, cfg_name, 'group_id'))
    api_ver = get_setting(cfg_path, cfg_name, 'api_ver')
    wait_time = int(get_setting(cfg_path, cfg_name, 'wait_time'))
    img_format = get_setting(cfg_path, cfg_name, 'img_format')
    database_update_time = int(get_setting(cfg_path, cfg_name, 'database_update_time'))
    vertical_frame_offset = int(get_setting(cfg_path, cfg_name, 'vertical_frame_offset'))
    print('[Бот] Файл конфигурации загружен успешно.')
    connection, cursor = get_database('users_states.db')
    main(timer=time.time())
    connection.commit()
    connection.close()
