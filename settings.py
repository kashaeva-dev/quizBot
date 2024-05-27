import redis


def get_redis_db(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD):
    return redis.Redis(host=REDIS_HOST,
                       port=REDIS_PORT,
                       db=0,
                       password=REDIS_PASSWORD,
                       )
