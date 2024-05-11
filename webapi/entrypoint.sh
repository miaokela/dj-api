#!/bin/bash

# 启动 Django 服务
uwsgi --http :8000 --module your_project.wsgi &

# 启动 Celery worker，并将日志输出到指定文件
celery -A webapi worker --loglevel=info >> /var/log/celery_worker.log 2>&1 &

# 启动 Celery beat，并将日志输出到指定文件
celery -A webapi beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info >> /var/log/celery_beat.log 2>&1 &

# 启动 Flower，并将日志输出到指定文件
celery -A webapi flower --address=0.0.0.0 --port=5555 >> /var/log/celery_flower.log 2>&1 &

# 等待所有后台任务完成
wait