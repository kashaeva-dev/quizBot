import redis

from environs import Env

env = Env()
env.read_env()

redis_db = redis.Redis(host=env.str('REDIS_HOST'),
                       port=env.int('REDIS_PORT'),
                       db=0,
                       password=env.str('REDIS_PASSWORD'),
                       )
