# homework_bot
Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.

## Технологии:

- __Python__
- __python-dotenv==0.19.0__
- __python-telegram-bot==13.7__

### Запуск проекта:

Клонировать репозиторий:
```
https://github.com/AndrejGurtovoj/homework_bot.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

Windows
```
python -m venv venv
source venv/Scripts/activate
```
Linux/macOS
```
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Записать в переменные окружения (файл .env) необходимые ключи:
- токен профиля на Яндекс.Практикуме
- токен телеграм-бота
- свой ID в телеграме

Запустить проект:

```
python homework.py
```
