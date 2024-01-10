import asyncio
import websockets
import json
    
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

    async def connect_client(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self.status = "Connected"
            await self.initial_connection()  # Perform any initial connection setup
        except Exception as e:
            self.status = f"Connection failed: {e}"

    async def initial_connection(self):
        msg = {
            "header": "connection",
            "body": {"key": self.key}
        }
        await self.send_message(msg)

    async def set_admin(self):
        msg = {
            "header": "set_admin",
            "body": {"key": self.key}
        }
        await self.send_message(msg)

    async def send_model(self, model):
        try:
            # Attempt to check if the 'model' parameter is valid JSON
            json.loads(model)

            # If parsing succeeds, it's a legitimate JSON string
            msg = {
                "header": "distribute_model",
                "body": {"model": model,
                         "key": self.key}  # Assuming 'model' is already a valid JSON string
            }

            # Send the JSON message to the server
            await self.send_message(msg)
        except json.JSONDecodeError as e:
            # If parsing fails, 'model' is not a valid JSON string
            print(f"Error: 'model' parameter is not a valid JSON string. {e}")

    async def send_message(self, message):
        if self.websocket is None or not self.websocket.open:
            # Reconnect if the connection is closed or doesn't exist
            await self.connect_client()

        message = json.dumps(message)
        try:
            self.status = "Sending message"
            await self.websocket.send(message)  # Send the message to the server
            response = await self.websocket.recv()  # Receive a response from the server
            self.status = f"Received: {response}"
        except websockets.exceptions.ConnectionClosed as e:
            self.status = f"Connection closed: {e}"
            print(f"Connection closed: {e}")
        except Exception as e:
            self.status = f"An error occurred: {e}"
            print(f"An error occurred: {e}")

    def connect(self):
        asyncio.create_task(self.connect_client())

    async def close(self):
        if self.websocket is not None and self.websocket.open:
            await self.websocket.close()
