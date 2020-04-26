from os import environ


bind = '127.0.0.1:8000'
max_requests = 100
workers = environ.get('GUNICORN_WORKERS', 10)
timeout = 20
user = 'www-data'
group = 'www-data'
