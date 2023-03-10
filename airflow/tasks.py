import aioredis
from parse_xml import parse_xml_currency


async def currency_cron_task():
    redis = await aioredis.from_url("redis://redis:6379")
    await redis.set('currency', parse_xml_currency(), ex=60 * 60 * 24, nx=True)
    await redis.close()
