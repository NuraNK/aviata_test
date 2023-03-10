import uvicorn, asyncio, json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

@app.post("/search")
async def search():
    with open("{}/files_b/response_b.json".format(BASE_DIR), "r") as file:
        await asyncio.sleep(60)
        return JSONResponse(json.load(file))



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9002, reload=True)
