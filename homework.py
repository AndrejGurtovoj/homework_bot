import logging
import os
import requests
import sys
import telegram
import time

from http import HTTPStatus
from requests import RequestException
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Функция отправляет сообщение в Telegram чат."""
    try:
        logger.info('Начата отправка сообщения')
        bot.send_message(
            TELEGRAM_CHAT_ID,
            text=message)
        logger.info(f'Сообщение {message} отправлено')
    except Exception as error:
        logger.error(f'Ошибка при отправке {message} сообщения: {error}')
        raise False


def get_api_answer(current_timestamp):
    """Функция делает запрос к API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except requests.exceptions.RequestException as error:
        logger.error(f'Ошибка, статус запроса {error}')
        raise Exception(error)
    if homework_statuses.status_code != HTTPStatus.OK:
        error_message = 'Ошибка Request'
        logger.error(error_message)
        raise RequestException(error_message)
    try:
        response = homework_statuses.json()
    except Exception as error:
        logger.error(f'Нет ожидаемого ответа сервера {error}')
        raise Exception(error)
    return response


def check_response(response):
    """Функция проверяет ответ API на корректность."""
    homeworks_list = response['homeworks']
    if not isinstance(response, dict):
        message = 'Ответ API представлен не в виде словаря'
        logger.error(message)
        raise ValueError(message)
    if not bool(response):
        message = 'Ответ API пришел в виде пустого словаря'
        logger.error(message)
        raise ValueError(message)
    if not isinstance(homeworks_list, list):
        message = 'Домашние задания представлены не в виде списка'
        logger.error(message)
        raise ValueError(message)
    if 'homeworks' not in response:
        return False
    return homeworks_list


def parse_status(homework):
    """Функция проверяет информацию о статусе домашней работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    try:
        all((homework_name, homework_status))
        if homework_status in HOMEWORK_STATUSES:
            verdict = HOMEWORK_STATUSES[homework_status]
            message = (f'Изменился статус проверки работы "{homework_name}". '
                       f'{verdict}')
            return message
        message = f'Статус {homework_status} недокументирован'
        logger.error(message)
        raise ValueError(message)
    except Exception:
        message = 'Ключи "homework_name" и "status" в списке отсутствуют'
        logger.error(message)
        raise ValueError(message)


def check_tokens():
    """Функция проверяет доступность переменных окружения."""
    return any((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        error_message = 'Токены недоступны'
        logger.error(error_message)
        raise Exception(error_message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    send_message(bot, 'Бот стартовал')
    current_timestamp = int(time.time())
    prev_error = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            homework = check_response(response)
            if homework:
                message = parse_status(homework[0])
                send_message(bot, message)
            else:
                logger.debug('Отсутствие в ответе новых статусов')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != prev_error:
                if send_message(bot, message) is False:
                    message = ('Бот остановлен с ошибкой')
                else:
                    prev_error = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s: %(levelname)s - %(message)s - %(name)s',
        level=logging.DEBUG,
        filename='homework_bot.log',
        filemode='w'
    )
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)
    main()
