from tasks import currency_cron_task
import uvicorn, aiohttp, uuid, asyncio, aioredis, pickle
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()


async def _search(search_id: str):
    redis = await aioredis.from_url("redis://redis:6379")
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.post('http://provider-a:9001/search'),
            session.post('http://provider-b:9002/search'),
        ]
        responses = await asyncio.gather(*tasks)
        result = None
        for response in responses:
            res = await response.json()
            if result is None:
                result = res.copy()
            else:
                result.extend(res)
        await redis.set(search_id, pickle.dumps(result), nx=True)
    await redis.close()


@app.post("/search")
async def search(background_tasks: BackgroundTasks):
    search_id = str(uuid.uuid4())
    background_tasks.add_task(_search, search_id)
    return {"search_id": search_id}


@app.get("/results/{search_id}/{currency}")
async def results(search_id: str, currency: str):
    redis = await aioredis.from_url("redis://redis:6379")
    if await redis.get("currency") is None:
        await currency_cron_task()
    if await redis.get(search_id) is None:
        return {
            "search_id": search_id,
            "status": "PENDING",
            "items": []
        }
    currency = currency.upper()
    _currency = pickle.loads(await redis.get("currency"))

    cur = float(_currency.get(currency, 1.0))
    items = pickle.loads(await redis.get(search_id))
    for count, item in enumerate(items):
        if items[count]['pricing']['currency'] != "KZT":
            total = float(items[count]['pricing']['total'])
            base = float(items[count]['pricing']['base'])
            taxes = float(items[count].get('pricing').get("taxes", 0))
            items[count]['pricing']['total'] = round(total * cur, 2)
            items[count]['pricing']['base'] = round(base * cur, 2)
            items[count]['pricing']['currency'] = "KZT"
            if taxes != 0 and taxes != "0.00":
                items[count]['pricing']['taxes'] = round(taxes * cur, 2)
    return {
        "search_id": search_id,
        "status": "COMPLETED",
        "items": items
    }


scheduler = AsyncIOScheduler()
scheduler.add_job(currency_cron_task, 'cron', hour=12, minute=0,
                  timezone=timezone('Asia/Almaty'))
scheduler.start()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
