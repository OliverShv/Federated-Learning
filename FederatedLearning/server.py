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
                              "connection": self.initial_connection,
                              "distribute_weights": self.distribute_weights}

    async def handle_client(self, websocket):
        try:
            #Receive message
            async for message in websocket:
                
                #Check that key and websocket address are valid
                message = json.loads(message)
                key = message["body"]["key"]
                success, response = self.validate_credentials(key, websocket)

                print(f"Message from {websocket.remote_address}")
                print(message)

                if success:
                    #Check that request is valid
                    if message["header"] in self.header_methods.keys():
                        await self.header_methods[message["header"]](message["body"])
                    else:
                        await websocket.send(f"Request not found: {message['header']}")

                else:
                    await websocket.send(f"Request not found: {response}")

        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")
        finally:
            print("Connection ended")
            pass

    def validate_credentials(self, key, websocket):
        if key in self.keys:
            #Check if websocket and key match or if key in unassigned
            if key not in self.clients.keys():
                self.clients[key] = websocket# Add the client to the set of connected clients
            elif self.clients[key] != websocket:
                error = "Key already in use"
                return [False, error]  
        else:
            error = "Key does not exist"
            return [False, error]
        
        return [True, "Success"]
    
    async def initial_connection(self, parameters):
        print("Client connection")
        print(parameters["key"])
        print(self.clients[parameters["key"]])
        await self.clients[parameters["key"]].send("Connection made")

    async def set_admin(self, parameters):
        if self.admin_key in [None, parameters["key"]]:
            self.admin_key = parameters["key"]
            print("Admin key overriden")
            await self.clients[parameters["key"]].send("Admin key overriden")
        else:
            await self.clients[parameters["key"]].send("Admin key failed to be overriden")

    async def distribute_model(self, parameters):

        if parameters["key"] == self.admin_key:
            msg = {
                    "header": "set_model",
                    "body": parameters["model"]  # Assuming 'model' is already a valid JSON string
                }
            print("Model attempted to send")
            await self.send_to_clients(msg, [parameters["key"]])
            await self.clients[parameters["key"]].send("Model Distributed")

    async def distribute_weights(self, parameters):

        if parameters["key"] == self.admin_key:
            msg = {
                    "header": "set_weights",
                    "body": parameters["weights"]  # Assuming 'model' is already a valid JSON string
                }
            print("Weights attempted to send")
            await self.send_to_clients(msg, [parameters["key"]])
            await self.clients[parameters["key"]].send("Weights Distributed")

    async def send_to_clients(self, message, do_not_send = []):
        # Send a message to all connected clients
        message = json.dumps(message)

        for key, client in self.clients.items():
            if key not in do_not_send:
                try:
                    print("Message sent to: ", key, client)
                    await client.send(message)
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
