РСО VK Бот
========================================================================================================================================

> Вставляет в изображения рамки в честь дня РСО.

> До безобразия простой Синхронный LongPoll

> Работает в обёртке [vk_api](https://github.com/python273/vk_api)

---

## Установка

- Убедитесь, что у вас установлен интерпретатор Python версии 3.7 или новее;
- Убедитесь в том, что интерпретатор добавлен в PATH;
- Клонируйте или загрузите этот репозиторий;
- Не забудьте заменить ресурсы (в папках examples и frames, но с теми же именами файлов и их расширениями). Например: Вожатый.png => Вожатый.png

> Установите все зависимости

```
pip3 install -r requirements.txt
```

---

## Настройка

- Откройте файл config.ini. Если вы его удалили, то запустите бота (см. след. пункт): он сам сгенерирует файл конфигурации.

> config.ini будет выглядеть так:

```
[Group bot config]
group_token = value
group_id = value
api_ver = value
wait_time = value
img_format = value
database_update_time = value
vertical_frame_offset = value
```

>Значения прописываются без ковычек и скобок.
>Пример правильного файла конфигурации:

```
[Group bot config]
group_token = value
group_id = value
api_ver = value
wait_time = value
img_format = value
database_update_time = value
vertical_frame_offset = value
```

---

## Запуск

> Запустите единственный скрипт

```
python bot.py
```

---

## Обратная связь и пожертвования (при желании)

[Мой профиль ВКонтакте](vk.com/fl1ckje)

---

## Лицензия

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)
