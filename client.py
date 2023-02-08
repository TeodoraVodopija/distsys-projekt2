import asyncio
import aiohttp
import pandas as pd

# Generate list of client IDs
client_ids = list(range(1, 101))

# Load the dataframe
df = pd.read_json("file-000000000040.json", lines=True)
print("Dataframe loaded.")

# Calculate rows per client
rows_per_client = len(df) // len(client_ids)

# Split the dataframe into chunks for each client
df_chunks = [df.iloc[i:i + rows_per_client] for i in range(0, len(df), rows_per_client)]

# Create a dict of client IDs and their code (by adding code from rows as value to ID property)
clients = {idx: chunk["content"].tolist() for idx, chunk in zip(client_ids, df_chunks)}

# Define an async function for processing codes
async def process_codes(client_id, codes):
    async with aiohttp.ClientSession() as session:
        response = await session.get("http://127.0.0.1:8080/", json={"client": client_id, "codes": codes})
        result = await response.json()
        return result

async def main():
    # Send requests for code processing
    print("Sending data...")
    tasks = [process_codes(client_id, codes) for client_id, codes in clients.items()]
    results = await asyncio.gather(*tasks)
    print("Results of data processing for all clients retrieved.")

    # Log the average number of letters for clients' code
    for result in results:
        print(f"Average code length for client with ID {result['client']} is {result['averageWordcount']}")

asyncio.run(main())