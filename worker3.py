#import packages (constraints)
from aiohttp import web
import random
import asyncio
import re
import string

routes = web.RouteTableDef()

@routes.get("/")
async def fun(request):
	try:
		#network delay 0.1 - 0.3 s (simulation)
		requestTime = random.random() * 0.2 + 0.1
		await asyncio.sleep(requestTime)

		#counter of words
		jsonData = await request.json()
		result = len(re.sub("[" + string.punctuation + "]", "", jsonData.get("data")).split())

		#network delay 0.1 - 0.3 s (simulation)
		responseTime = random.random() * 0.2 + 0.1
		await asyncio.sleep(responseTime)

		return web.json_response({"Name": "worker", "Status": "OK", "Number of words": result}, status = 200)

	except Exception as ex:
		return web.json_response({"Name": "worker", "Error": str(ex)}, status = 500)

app = web.Application()
app.router.add_routes(routes)
web.run_app(app, port = 8083)