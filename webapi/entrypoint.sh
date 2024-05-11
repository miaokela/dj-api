#!/bin/bash

# 启动 Django 服务
uwsgi --http :8000 --module webapi.wsgi &

# 启动 Celery worker
celery -A webapi worker --loglevel=info &

# 启动 Celery beat
celery -A webapi beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info &

# 启动 Flower
celery -A webapi flower --address=0.0.0.0 --port=5555 &

# 等待所有后台任务完成
wait