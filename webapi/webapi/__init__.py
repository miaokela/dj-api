import pymysql
from webapi.celery import app as celery_app

__all__ = ('celer_app',)

pymysql.install_as_MySQLdb()
