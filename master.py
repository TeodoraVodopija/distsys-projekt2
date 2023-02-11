#import packages (constraints)
import aiohttp
import asyncio
import random
import time
from aiohttp import web

max_number_of_workers = 10
start_time = time.monotonic_ns()

routes = web.RouteTableDef()

@routes.post("/data_send")
async def receive_data(request):
    #receiving incoming request data from client
    data = await request.json()

    #extracting all the lines from json
    lines = list(data.values())

    #list of worker ports
    worker_ports = [8081, 8082, 8083, 8084, 8085, 8086, 8087, 8088, 8089, 8090]

    #listen for signals from the worker nodes if they are ready
    workers = {}
    async with aiohttp.ClientSession() as session:
        worker_ready = [session.get(f"http://localhost:{port}/worker_ready") for port in worker_ports]
        worker_ready = await asyncio.gather(*worker_ready)
        for port, resp in zip(worker_ports, worker_ready):
            if resp.status == 200:
                #if worker is ready, add it to the list of workers, assign ID based on port number
                worker_id = f"server {port}"
                workers[worker_id] = port
        print(f"Received worker ready signals from: {list(workers.keys())}")

        #selecting 3 to 5 workers randomly
        select_workers = random.sample(list(workers.keys()), random.randint(3, 5))
        print(f"Selected workers: {select_workers}")

        #send data to selected workers
        if workers:
            task_count = {}  #empty dict to keep track of the number of sent tasks for each worker
            while lines:
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for worker_id in select_workers:
                        port = workers[worker_id]
                        index = worker_ports.index(port)
                        data_to_send = lines[index * 1000: index * 1000 + 1000]  #select 1000 lines of data
                        if data_to_send:  #check if data_to_send is not empty
                            start_time = time.monotonic_ns()  #start a timer for each task
                            task = asyncio.create_task(session.post(
                                f"http://localhost:{port}/receive_data",
                                json = {"data": data_to_send, "worker_id": worker_id}))  #create task to send data
                            tasks.append(task)
                    await asyncio.gather(*tasks)
                    for port in task_count:
                        print(f"Total tasks sent to worker{port}: {task_count[port]}")
                    lines = lines[3:]
        else:
            print("No workers are ready.")

        #if all data has been sent, print a message
        if not lines:
            print("No more data to send.")

    #return a response to the client indicating that the data has been received
    return web.Response(text = "Data received.")

#define a dictionary to store the word counts received from the worker nodes
word_counts = {}

@routes.post("/receive_worker_word_count")
async def receive_word_count(request):
    #receive the word count data from the worker
    data = await request.json()
    #extract the worker port and word count from the received data
    worker_port = data["worker_port"]
    word_count = data["word_count"]

    # Log the current time when receiving the word count from the worker
    current_time = time.monotonic_ns()  #timer ends here
    print(f"Received word count from {worker_port} : {word_count} words counted.")
    elapsed_time = current_time - start_time  #calculate the elapsed time
    # print(f"Elapsed time between sending and receiving data: {elapsed_time} ns")
    print(f"Elapsed time between sending and receiving data: {elapsed_time} ns ({elapsed_time / 1000000:.2f} ms)")

    #increment the count of completed tasks from the worker
    if worker_port in word_counts:
        word_counts[worker_port] += 1
    else:
        word_counts[worker_port] = 1

    #print the total number of completed tasks from the worker
    print(f"Total tasks returned {worker_port}: {word_counts[worker_port]}")

    return web.Response(status = 200)


app = web.Application(client_max_size = 1024 * 1024 * 200)
app.add_routes(routes)
web.run_app(app, port = 8080)
