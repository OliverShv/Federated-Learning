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