import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapi.settings")

app = Celery("webapi")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.timezone = 'Asia/Shanghai'
app.autodiscover_tasks()
