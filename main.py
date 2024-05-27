import argparse
import logging

from environs import Env

from bots.tg_bot import start_tg_bot
from bots.vk_bot import start_vk_bot
from settings import get_redis_db

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        prog="Start telegram and vk quiz bots",
    )
    parser.add_argument('--only_tg',
                        action='store_true',
                        help='Start only tg bot',
                        )
    parser.add_argument('--only_vk',
                        action='store_true',
                        help='Start only vk bot',
                        )
    parser.add_argument('--file',
                        default='../quizBot/quiz_content.txt',
                        help='Path to file with quiz content',
                        )

    return parser


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    parser = create_parser()
    args = parser.parse_args()

    REDIS_HOST = env.str('REDIS_HOST')
    REDIS_PORT = env.int('REDIS_PORT')
    REDIS_PASSWORD = env.str('REDIS_PASSWORD')

    redis_db = get_redis_db(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)

    try:
        tg_bot_token = env('TG_BOT_API')
        vk_api_token = env('VK_BOT_API')

        if args.only_tg:
            start_tg_bot(tg_bot_token, logger, redis_db, filepath=args.file)
        elif args.only_vk:
            start_vk_bot(vk_api_token, logger, redis_db, filepath=args.file)
        else:
            start_tg_bot(tg_bot_token, logger, redis_db, filepath=args.file)
            start_vk_bot(vk_api_token, logger, redis_db, filepath=args.file)
    except Exception as error:
        logger.exception(error)


if __name__ == '__main__':
    main()
