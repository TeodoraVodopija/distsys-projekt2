#import packages (constraints)
import asyncio
import aiohttp
from aiohttp import web
import re
import string
import random
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO)

routes = web.RouteTableDef()

@routes.get("/worker_ready")
async def worker_ready(request):
    return web.Response(status = 200)

@routes.post("/receive_data")
async def receive_data(request):
    #network delay 0.1 - 0.3 s (simulation)
    await asyncio.sleep(random.uniform(0.1, 0.3))

    #receiving codes from master
    data = await request.json()

    #count the number of words in the file
    async def count_words(text: str) -> int:
        await asyncio.sleep(0)  #simulate an async operation
        return len(re.sub("[" + string.punctuation + "]", "", str(text)).split())

    number_of_words = await count_words(data)
    logging.info(f"Word count: {number_of_words}")

    #send the number of words back to master
    async with aiohttp.ClientSession() as session:
        #network delay 0.1 - 0.3 s (simulation)
        await asyncio.sleep(random.uniform(0.1, 0.3))
        await session.post("http://localhost:8080/receive_word_count",
                            json = {"Worker port": "worker" + str(request.transport.get_extra_info("sockname")[1]),
                                    "Number of words": number_of_words})

    return web.Response(status = 200)

app = web.Application(client_max_size = 1024 * 1024 * 200)
app.add_routes(routes)
web.run_app(app, port = 8084)