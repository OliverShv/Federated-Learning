import asyncio
import websockets
import json
import requests
from flask import Flask, request

app = Flask(__name__)

class Connection:
    def __init__(self, address, key, port=None):

        self.address = address
        self.key = key
        if port is not None:
            self.address += ":" + str(port)
        self.uri = f"ws://{self.address}"  # Construct the WebSocket URI

        self.status = "Not connected"
        self.websocket = None  # Store the WebSocket connection

        asyncio.create_task(self.connect_client()) 
        self.run_hhtp()

    ###### Webcocket connection #####
    async def connect_client(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self.status = "Connected"
            msg = {
                "header": "connection",
                "body": {"key": self.key}
            }
            await self.send_message(msg)
            
        except Exception as e:
            self.status = f"Connection failed: {e}"

    def connect(self):
        asyncio.create_task(self.connect_client())

    async def close(self):
        if self.websocket is not None and self.websocket.open:
            await self.websocket.close()

    ####### HTTP connection ########
    #TODO admin sends files to server, server alerts clients of new file via websocket, clients downlaod file from websocket
    
    def download_file(self, file_url, local_file_path):
        try:
            # Send a GET request to the server to download the file
            response = requests.get(file_url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Open the local file in binary write mode and save the downloaded content
                with open(local_file_path, 'wb') as file:
                    file.write(response.content)
                print(f'File downloaded and saved as {local_file_path}')
            else:
                print(f'Failed to download file. Status code: {response.status_code}')

        except requests.exceptions.RequestException as e:
            print(f'An error occurred: {e}')

    def send_file(self,target_url, file_path):
        try:
            # Open the file in binary mode and read its content
            with open(file_path, 'rb') as file:
                file_data = file.read()

            # Create a dictionary to represent the file data
            files = {'file': (file_path, file_data)}

            # Send the file in a POST request to the target URL using requests
            response = requests.post(target_url, files=files)

            # Check the response status code and content
            if response.status_code == 200:
                print(f'Success: {response.text}')
            else:
                print(f'Error: {response.status_code}')

        except Exception as e:
            print(f'Error: {str(e)}')