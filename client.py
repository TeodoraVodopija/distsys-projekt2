#import packages (constraints)
import aiohttp
import asyncio
import json

#generate list of 10000 client IDs
client_IDs = [f"Client {i+1}" for i in range(10000)]

#reading data from .json file
with open("file-000000000040.json", "r") as file:
    #reading first 10000 lines from .json file
    code = [json.loads(line)['content'] for line in file.readlines()[:10000]]

#dividing the content of codes evenly among the 10000 clients
lines_per_client = len(code) // len(client_IDs)

#creating a dictionary of client IDs and the lines assigned to each client
clients_data = {}
for i, client_id in enumerate(client_IDs):
    clients_data[client_id] = code[(i * lines_per_client):((i * lines_per_client) + lines_per_client)]

#calculate the average number of letters in python code for every client
async def calculate_average_number_of_letters(client_ID, client_code):
    average_letters = (sum(len(line) for line in client_code)) / len(client_code)
    print(f"{client_ID} - average number of letters in python code: {average_letters}.")

async def data_send():
    #send database to master
    db = clients_data

    tasks = [calculate_average_number_of_letters(client_ID, client_code) for client_ID, client_code in clients_data.items()]
    await asyncio.gather(*tasks)

    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:8080/data_send", json = db) as res:
            print(res.status)

asyncio.run(data_send())