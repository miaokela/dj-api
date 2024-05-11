# dj-api

django api模板

## 依赖库

```text
django==3.1
djangorestframework==3.12
celery==5.0.5
redis==3.5.3
flower
django-celery-results==2.0.0
django-celery-beat==2.2.0
pyyaml
jinja2
pymysql
djangorestframework-simplejwt
```

## 基本功能

```text
1. 数据存储
2. 日志
3. 动态SQL
4. 统一响应结构
5. 统一错误处理
6. 常用api编写流程，包含序列化
7. jwt用户认证
8. 异步任务调用、定时任务配置
```


```
{
"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxNTQzMzA3NiwianRpIjoiZmI2YTBkOTVhZmI4NGNhNzhlODNkNDUyOWNkZDA0NTYiLCJ1c2VyX2lkIjoxfQ.HFo_HVY4xwqftCbAkyTrw6cM3FbywTThbebf4YFLKgk",
"access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE1MzQ2OTc2LCJqdGkiOiJhZWI1OGIxNWZlMGU0NjM5YTA1ZmI2N2ExYmUxODYyMyIsInVzZXJfaWQiOjF9.UGf71yioEQchk0E6sAlTGzIrm4hpgkdKESpWRhlw-v0"
}
```

## 创建admin超级管理员
```shell
python manage.py createsuperuser
```

## Celery使用
- 启动worker工人
> celery -A webapi worker --loglevel=info

- 启动beat定时任务
> celery -A webapi beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info

- 启动flower监控
> celery -A webapi flower --address=0.0.0.0 --port=5555
