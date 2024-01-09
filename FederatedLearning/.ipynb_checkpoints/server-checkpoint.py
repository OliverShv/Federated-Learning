import asyncio
import websockets

class WebSocketServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.server = None

    async def handle_client(self, websocket, path):
        print(f"New connection from {websocket.remote_address}")
        try:
            async for message in websocket:
                print(f"Received message: {message}")
                await websocket.send(f"Echo: {message}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")

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