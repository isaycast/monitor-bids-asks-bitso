import asyncio
import hashlib
import hmac
import time
from aiohttp import ClientSession
import json
import os 

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
BASE_API_URL = os.getenv('BASE_API_URL')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

http_method = os.getenv('http_method')
request_path = os.getenv('request_path')
json_payload = ''
requested_books = os.getenv('requested_books').split(",")

def generate_signature_auth_header(http_method: str, request_path: str, json_payload=''):
    """
    Generates an authentication header for Bitso API requests.

    This method creates an authentication header using the API key, API secret, 
    and the provided parameters. The authentication header is constructed following 
    the format required by the Bitso API.

    Args:
        http_method (str): The HTTP method used in the request (e.g., 'GET', 'POST').
        request_path (str): The request path (endpoint) of the API.
        json_payload (str, optional): The JSON payload for POST requests. Defaults to an empty string.

    Returns:
        str: The authentication header in the format required by the Bitso API.

    """
    
    nonce = str(int(time.time() * 1000))
    message = nonce + http_method + request_path + json_payload
    signature = hmac.new(API_SECRET.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

    auth_header = f'Bitso {API_KEY}:{nonce}:{signature}'
    return auth_header


def process_api_response (response:dict):
    """

    This function processes the response from the Bitso API to extract the best bid and ask prices.
    It calculates the spread as the difference between the best ask and best bid prices.

    Args:
        response (dict): The JSON response from the Bitso API.

    Returns:
        dict: A dictionary containing the best bid and ask prices, as well as the calculated spread.
    """
    bids_object_list = response["payload"]["bids"]
    asks_object_list = response["payload"]["asks"]
    best_bid = round(float(bids_object_list[0]["price"]), 2)
    best_ask = round(float(asks_object_list[0]["price"]), 2)
    book_name = response["payload"]["bids"][0]["book"]
    updated_at = response["payload"]["updated_at"]
    record = {
            "orderbook_timestamp": str(updated_at),
            "book": book_name,
            "bids": best_bid,
            "asks": best_ask,
            "spread": round(((best_ask - best_bid) * 100 / best_bid), 2)
            }
    

    return record

async def get_book_data(session, base_api_url: str, book: str, request_path: str, json_payload: str):
    """
    Fetches order book data for a specific book from the Bitso API and sends it to a webhook.

    This asynchronous function constructs the request URL and headers, sends the GET request,
    processes the response to extract the best bid and ask prices, and calculates the spread. 
    If the request is successful, the data is sent to a webhook.

    Args:
        session: An aiohttp.ClientSession object to perform the HTTP requests.
        base_api_url (str): The base URL of the Bitso API.
        book (str): The specific book for which data is being requested.
        request_path (str): The path of the request endpoint.
        json_payload (str): The JSON payload for the request.

    Returns:
        tuple: A tuple containing the record dictionary and the response status code. 
        If the request fails, returns (None, None).
    """

    request_book = f"{request_path}{book}"
    url = f"{base_api_url}{request_book}"
    headers = {
        'Authorization': generate_signature_auth_header(http_method, request_book, json_payload),
        'Content-Type': 'application/json'
    }
    try:
        async with session.get(url, headers=headers) as response:
            return await response.json()
    except Exception as e:
        print(f"Failed to fetch data for {book}: {e}")
        return None, None

async def post_data_to_webhook(session, data):
    """
    Sends data to a specified webhook.

    This asynchronous function sends JSON-formatted data to a webhook using an HTTP POST request. 
    It handles the response status and prints the appropriate message based on whether the request was successful or not.

    Args:
        data (dict): The data to be sent to the webhook.
    """
    headers = {
            'Content-Type': 'application/json'
        }
    payload = json.dumps(data)
    try:
        async with session.post(WEBHOOK_URL, headers=headers, data=payload) as response:
            if response.status == 200:
                    print("Data sent successfully.")
            else:
                    print(f"Failed to send data: {response.status}")
            return await response.json()
    except Exception as e:
            print(f"Failed to send data to webhook: {e}")


async def process_tasks(session,tasks):
    """
    Process completed tasks in a separate coroutine to avoid blocking the main loop.
    """
    while True:
        completed_tasks = [t for t in tasks if t.done()]
        for task_completed in completed_tasks:
            tasks.remove(task_completed)

            try:
                result = task_completed.result()
                result = process_api_response(result)

                if result is not None:
                    asyncio.create_task(post_data_to_webhook(session, data=result))
            except Exception as e:
                print(f"Error processing data: {e}")
        
        await asyncio.sleep(0.1)  # Sleep briefly before checking again

async def start_request():
    """
    Starts a periodic request to fetch order book data for multiple books and send it to a webhook.

    This asynchronous function creates a session and continuously fetches data for the specified books
    from the Bitso API at regular intervals.
    """
    async with ClientSession() as session:
        start_time = time.time()
        # duration = 10 * 60  # 10 minutos
        tasks = []
        async_process_task = asyncio.create_task(process_tasks(session, tasks))
        while True:
            for book in requested_books:
                async_book_task = asyncio.create_task(get_book_data(session, BASE_API_URL, book, request_path, json_payload))
                tasks.append(async_book_task)

            await asyncio.sleep(1 - ((time.time() - start_time) % 1))  

        # This code need to be executed if we pass a duration to while loop
        # await asyncio.gather(*tasks)
        # await async_process_task


# Principal funcion
async def main():
    await start_request()

if __name__ == "__main__":
    asyncio.run(main())
