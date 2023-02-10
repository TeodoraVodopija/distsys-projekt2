#import packages (constraints)
import asyncio
import aiohttp
import pandas as pd

#generate the list od IDs - 10000
client_IDs = list(range(1, 10001))

#reading .json file (dataset)
data = pd.read_json("file-000000000040.json", lines = True)

#calculate the number of rows per client
rows_per_client = int(len(data) / len(client_IDs))

#assigning IDs to clients
clients = {id: [] for id in client_IDs}

#assigning each client python code
for client_ID, py_code in clients.items():
    for _, row in data.iloc[((client_ID - 1) * rows_per_client) + 1 : (((client_ID - 1) * rows_per_client) + rows_per_client) + 1].iterrows():
        py_code.append(row.get("content")) #content - python code

#initial empty lists
tasks = []
results = []

async def request_code_process():
    async with aiohttp.ClientSession() as session:
        for client_ID, py_code in clients.items():
            tasks.append(asyncio.create_task(
                session.get("http://127.0.0.1:8080/", json = {"Client": client_ID, "Python code": py_code})))
        results = await asyncio.gather(*tasks)
        results = [await result.json() for result in results]

        #print average number of words in python files for each client
        for result in results:
            print("Average python code length for client with ID ", result.get("client"), " is ", result.get("averageWordcount"), ".")

asyncio.get_event_loop().run_until_complete(request_code_process())