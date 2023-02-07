#import packages (constraints)
import asyncio
import aiofiles
import json
import aiohttp
from aiohttp import web

routes = web.RouteTableDef()

async def process_data(client, code):
    print(f"{client} - average number of letters in python code: "
          f"{sum(len(word) for word in code.split()) / len(code.split())}")

@routes.get("/dataJson")
async def json_data(request):
    try:
        async with aiohttp.ClientSession() as session:
            #read .json file (by lines)
            async with aiofiles.open('file-000000000040.json', mode = 'r') as file_data:
                read_data = [await file_data.readline() for _ in range(10)]
                whole_data = [json.loads(line) for line in read_data]
                client_ids = [f"Client {i+1}" for i in range(10)]

                #empty dict and list - ready for receiving data
                database = {}
                tasks = []

                #content - python code for each client in .json data
                for i, item in enumerate(whole_data):
                    db_item = {"python_code": item["content"]}
                    database[client_ids[i]] = db_item
                    task = asyncio.create_task(process_data(client_ids[i], db_item["python_code"]))
                    tasks.append(task)
                await asyncio.gather(*tasks)
            return web.json_response(database, status = 200)

    except Exception as ex:
        return web.json_response({"Name": "client", "error": str(ex)}, status = 500)

app = web.Application()
app.router.add_routes(routes)
web.run_app(app, port = 8091)