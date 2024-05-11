import redis
from datetime import datetime, timedelta

from django.conf import settings
from django.utils.timezone import make_aware

from core.tasks import test_limited_api


class RedisScheduler:
    """
    限制任务的执行频率
    """
    def __init__(self, key=settings.RATE_LIMIT_REDIS_KEY):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.RATE_LIMIT_REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
        self.key = key
        # 保证原子性
        self.lua_script = """
        local key = KEYS[1]
        local interval = tonumber(ARGV[1])
        local current_time = tonumber(ARGV[2])
        local next_time = redis.call('get', key)
        if next_time == false then
            next_time = current_time + interval
        else
            next_time = tonumber(next_time)
            if next_time == nil then
                next_time = current_time + interval
            else
                if current_time >= next_time then
                    next_time = current_time + interval
                else
                    next_time = next_time + interval
                end
            end
        end
        redis.call('set', key, next_time)
        return next_time
        """

    def schedule_next_run(self, interval_milliseconds=100):
        current_time = int(datetime.now().timestamp() * 1000)  # Convert to milliseconds
        next_run_time = self.client.eval(
            self.lua_script, 1, self.key, interval_milliseconds, current_time)
        next_run_time = datetime.fromtimestamp(next_run_time / 1000)  # Convert back to seconds
        return make_aware(next_run_time)
    
def run_limited_task(data, interval_milliseconds=1):
    scheduler = RedisScheduler()
    next_run_time = scheduler.schedule_next_run(interval_milliseconds=interval_milliseconds)
    print(f'下次执行任务时间{next_run_time}')
    test_limited_api.apply_async(args=[data], eta=next_run_time)
