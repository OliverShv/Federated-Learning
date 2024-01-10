import asyncio
import websockets
import json

class WebSocketServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.server = None
        self.clients = dict() # Store connected clients
        self.admin_key = None
        self.keys = ["aaa","bbb"]

        self.header_methods = {"set_admin": self.set_admin,
                              "distribute_model": self.distribute_model,
                              "connection": self.initial_connection}

    async def handle_client(self, websocket):
        print(f"New connection from {websocket.remote_address}")
        try:
            async for message in websocket:
                #Check for a Valid Key
                message = json.loads(message)
                key = message["body"]["key"]
                print(message)
                if key in self.keys:

                    #Check if websocket and key match or if key in unassigned
                    if key not in self.clients.keys():
                        self.clients[key] = websocket# Add the client to the set of connected clients
                    elif self.clients[key] == websocket:
                            
                        print("key valid")
                        #Check if method exists
                        if message["header"] in self.header_methods.keys():
                            print("header valid")
                            await self.header_methods[message["header"]](message["body"])
                        else:
                            await websocket.send(f"Request not found: {message['header']}")
                    else:
                        await websocket.send(f"Key already in use: {message['header']}")
                else:
                    pass
                    break
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")
        finally:
            self.clients.remove(websocket)  # Remove the client from the set upon disconnection
    
    async def initial_connection(self, parameters):
        print("Client connection")
        await self.clients[parameters["body"]["key"]].send("Connection made")

    async def set_admin(self, parameters):
        if self.admin_key in [None, parameters["key"]]:
            self.admin_key = parameters["key"]
            print("Admin key overriden")

    async def distribute_model(self, parameters):

        if parameters["key"] == self.admin_key:
            msg = {
                    "header": "update_model",
                    "body": parameters["model"]  # Assuming 'model' is already a valid JSON string
                }
            print("Model attempted to send")
            await self.send_to_clients(msg)

    async def send_to_clients(self, message):
        # Send a message to all connected clients
        for client in self.clients:
            try:
                await client.send(f"Broadcast: {message}")
            except websockets.exceptions.ConnectionClosed:
                pass  # Handle exceptions for disconnected clients

    async def start(self):
        if self.server is None:
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            print(f"WebSocket server started on {self.host}:{self.port}")

    async def stop(self):
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            print("WebSocket server stopped")
            self.server = None

if __name__ == "__main__":
    server = WebSocketServer(host="localhost", port=8765)
    
    async def run_server():
        await server.start()
        try:
            await asyncio.Future()  # Run the server indefinitely
        except KeyboardInterrupt:
            await server.stop()

    asyncio.run(run_server())
