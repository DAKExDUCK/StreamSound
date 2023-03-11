import aioredis
from aioredis.client import Redis

from config import DB_LINK


class Database():
    redis: Redis = None

    async def init_connection():
        Database.redis = await aioredis.from_url(f"redis://{DB_LINK}", decode_responses=True)


    async def _set_key(name: str, key: str, value):
        await Database.redis.hset(name, key, value)


    async def _get_key(name: str, key: str):
        return await Database.redis.hget(name, key)


    async def _set_keys(name: str, dict: dict):
        await Database.redis.hmset(name, dict)


    async def _get_keys(name: str, *keys) -> tuple:
        return await Database.redis.hmget(name, *keys)


    async def _get_dict(name: str) -> dict:
        return await Database.redis.hgetall(name)


    async def if_user(user_id: int) -> bool:
        if await Database.redis.exists(user_id) == 0:
            return False
        else:
            return True

    async def is_registered_moodle(user_id: int) -> bool:
        if await Database.redis.hget(user_id, 'barcode'):
            return True
        else:
            return False
        
    async def get_users_list() -> list[str]:
        return await Database.redis.keys()
    
    async def create_user(data:dict):
        await Database.redis.hset(data['id'], mapping=data)

    async def get_user(user_id):
        user = await Database.redis.hgetall(user_id)
        del user['password']
        return user

    async def close():
        await Database.redis.close()
