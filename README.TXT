Описание
Проект получает события о состоянии известных хостов и сохраняет их в БД Influx.
Событие отправляется POST-запросом на /event/ c параметрами hostname, timestamp, is_online
Чтобы получить интервалы времени, в которые хост находился онлайн, нужно отправить GET-запрос на
/state/ c опциональными параметрами hostname, start (начало интервала), end(конец интервала)





Запуск
    1) make build
    2) make run
Требования:
    - docker
    - docker-compose
После запуска сервер доступен по адресу http://127.0.0.1:8000


Отправить событие:
    POST -> /event/
    {
        "hostname": "Host1",
        "is_online": "true",
        "timestamp": "1587916000"
    }


Получить статистику:
    GET -> /stats/?hostname=Host1&start=20-44-2020&end=29-04-2020


Запуск скрипта для генерации событий (для демонстрации работы)
    python generate_test_events.py
    Требования
        - python3.6+
        - asyncio
        - aiohttp


