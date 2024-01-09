import asyncio
import websockets
    
class newConnection():
    def __init__(self, address, key, port = None):
        self.address = address
        self.key = key
        if port != None:
            self.address+=":"+str(port)
        self.uri = f"ws://{self.address}"  # Construct the WebSocket URI

        self.status = "Not connected"
    
    async def connect_to_server(self):
        try:
            async with websockets.connect(self.uri) as websocket:
                # Perform WebSocket communication here
                self.status = "Attempting to connect to server"
                await websocket.send(self.key)  # Send the key to the server
                response = await websocket.recv()  # Receive a response from the server
                
                # Handle the response from the server as needed
                self.status = "Received: {response}"
                print(f"Received: {response}")
        except websockets.exceptions.ConnectionClosed as e:
            # Handle connection closed exception
            self.status = "Connection closed: {e}"
            print(f"Connection closed: {e}")
        except Exception as e:
            # Handle other exceptions
            self.status = "An error occurred: {e}"
            print(f"An error occurred: {e}")

    def connect(self):
        asyncio.create_task(self.connect_to_server())