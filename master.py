#import packages (constraints)
import aiohttp
from aiohttp import web
import asyncio
import logging
import random

logging.basicConfig(level = logging.INFO)

NO_workers = random.randint(5, 10) #random 5-10 workers
sample_size = 1000 #sample size, task for worker
max_NO_requests = 10000 #max number of data
received_requests = 0
received_responses = 0
sent_tasks = 0
received_tasks = 0

#number of workers
workers = {"Worker " + str(id): [] for id in range(0, NO_workers)}

routes = web.RouteTableDef()

@routes.get("/")
async def handler_of_tasks(request):
    try:
        global received_responses
        global sent_tasks
        logging.info(f"Current requests status: {int(received_requests / max_NO_requests)}")

        client_data = await request.json()

        codes = "\n".join(client_data.get("Python code"))
        code_split_newline = codes.split("\n")
        client_data["Python code"] = ["\n".join(code_split_newline[i : i + sample_size])
            for i in range(0, len(code_split_newline), sample_size)]

        tasks = []
        results = []
        async with aiohttp.ClientSession() as session:
            active_worker = 1
            for i in range(len(client_data.get("Python code"))):
                task = asyncio.create_task(
                    session.get(f"http://localhost: {8080 + active_worker} /worker_ {active_worker}",
                        json = {"ID": client_data.get("client_ID"), "Python code": client_data.get("Python code")[i]},
                    )
                )
                sent_tasks += 1
                tasks.append(task)
                workers["Worker - ID: " + str(active_worker)].append(tasks)

                if active_worker != NO_workers: active_worker += 1

            results = await asyncio.gather(*tasks)
            results = [await data.json() for data in results]

            AVG_number_of_words = [result.get("number_of_words") for result in results]
            AVG_number_of_words = int(sum(AVG_number_of_words) / len(client_data.get("code")))

            received_responses += 1

        return web.json_response({"Name": "master", "Status": "OK", "Average words per client": AVG_number_of_words}, status = 200)

    except Exception as ex:
        return web.json_response({"Name": "master", "Error": str(ex)}, status = 500)

app = web.Application()
app.router.add_routes(routes)
web.run_app(app, port = 8080)
