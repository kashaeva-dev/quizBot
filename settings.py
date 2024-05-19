import redis

from environs import Env

env = Env()
env.read_env()

redis_db = redis.Redis(host=env.str('REDIS_HOST'),
                        port=17869,
                        db=0,
                        password=env.str('REDIS_PASSWORD'),
                        )
