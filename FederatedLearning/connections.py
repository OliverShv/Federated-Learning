import asyncio
import websockets
import json
    
class Connection():
    def __init__(self, address, key, port = None):
        self.address = address
        self.key = key
        if port != None:
            self.address+=":"+str(port)
        self.uri = f"ws://{self.address}"  # Construct the WebSocket URI

        self.status = "Not connected"
        
    async def connect_client(self):
        msg = {
            "header":"connection",
            "body": {"key":self.key}
        }
        await self.send_message(msg)

    async def set_admin(self):
        msg = {
            "header":"set_admin",
            "body": {"key":self.key}
        }
        await self.send_message(msg)

    async def send_model(self, model):
        try:
            # Attempt to check if the 'model' parameter is valid JSON
            json.loads(model)
            
            # If parsing succeeds, it's a legitimate JSON string
            msg = {
                "header": "distribute_model",
                "body": {"model":model,
                         "key": self.key}  # Assuming 'model' is already a valid JSON string
            }
            
            # Send the JSON message to the server
            await self.send_message(msg)
        except json.JSONDecodeError as e:
            # If parsing fails, 'model' is not a valid JSON string
            print(f"Error: 'model' parameter is not a valid JSON string. {e}")

    async def send_message(self, message):
        message = json.dumps(message)
        try:
            async with websockets.connect(self.uri) as websocket:
                self.status = "Sending message"

                await websocket.send(message)  # Send the key to the server

                response = await websocket.recv()  # Receive a response from the server

                # Handle the response from the server as needed
                self.status = f"Received: {response}"

        except websockets.exceptions.ConnectionClosed as e:
            self.status = f"Connection closed: {e}"
            print(f"Connection closed: {e}")
        except Exception as e:
            self.status = f"An error occurred: {e}"
            print(f"An error occurred: {e}")

    def connect(self):
        asyncio.create_task(self.connect_to_server())