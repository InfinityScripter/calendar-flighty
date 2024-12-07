# Flight Calendar Importer

## Описание
Скрипт для импорта информации о рейсе из текстового файла в формат iCalendar (.ics).

## Возможности
- Парсинг информации о рейсе из текстового файла
- Конвертация времени с учетом часовых поясов
- Создание .ics файла для импорта в календарь

## Требования
- Python 3.7+
- Библиотеки: 
  - icalendar
  - pytz

## Установка
1. Клонируйте репозиторий
2. Установите зависимости:
   ```
   pip install icalendar pytz
   ```

## Использование
1. Подготовьте текстовый файл с информацией о рейсе
2. Запустите скрипт:
   ```
   python script.py
   ```

## Пример формата входного файла
```
Yamal Airlines 850 on 08.12.2024

Nojabrxsk to Saint Petersburg
↗ 17:40 GMT+5 NOJ (On time)
↘ 19:00 GMT+3 LED (On time)

Flight length 3 hr, 20 min

Arriving at Terminal 1 • Gate -- at 19:00 GMT+3

Updates: https://live.flighty.app/c9d2255a-929b-4779-ab56-c5ee7fbd21e3
```

## Лицензия
MIT
