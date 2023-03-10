import asyncio, time, uuid, aioredis
from unittest import IsolatedAsyncioTestCase
from httpx import Response, AsyncClient
from unittest.mock import patch, AsyncMock
from parse_xml import parse_xml_currency

BASE_URL = 'http://airflow:9000'



async def request(method: str, url: str, *args, **kwargs) -> Response:
    client: AsyncClient
    async with AsyncClient(base_url=BASE_URL) as client:
        return await client.request(method, url, *args, **kwargs)

class SearchAsync(IsolatedAsyncioTestCase):
    async def test_search(self):
        response = await request('post', '/search')
        self.assertEqual(response.status_code, 200)


class CurrencyAsync(IsolatedAsyncioTestCase):
    async def test_currency(self):
        response_search = await request('post', '/search')
        search_id = response_search.json().get("search_id", uuid.uuid4())
        currency = "EUR"
        response = await request('get', f"/results/{search_id}/{currency}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], "PENDING")
        await asyncio.sleep(60)
        response = await request('get', f"/results/{search_id}/{currency}")
        self.assertEqual(response.json()['status'], "COMPLETED")


class TestTaskCurrency(IsolatedAsyncioTestCase):
    async def test_task_currency(self):
        redis = await aioredis.from_url("redis://redis:6379")
        await redis.set('currency', parse_xml_currency(), ex=60 * 60 * 24,)
        await redis.close()
        res = await redis.get("currency")
        self.assertTrue(res is not None)