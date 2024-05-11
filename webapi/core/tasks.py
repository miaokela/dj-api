from datetime import datetime

from celery import shared_task


@shared_task
def add():
    print('start add task')
    return 1 + 2


# @shared_task(rate_limit='1/s')
@shared_task
def test_limited_api(params):
    print(f'限制1s只能执行一次{datetime.now()}')
    # 调用API
    # API请求失败该如何处理?
