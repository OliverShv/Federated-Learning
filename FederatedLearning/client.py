import asyncio
import websockets
import json
from .connection import Connection
from .model import Model
import numpy as np

class Client(Connection, Model):
    def __init__(self, address:str, key:str, port=None):
        Model.__init__(self)
        Connection.__init__(self, address, key, port)

        self.methods  = {"set_model": self.set_model,
                         "set_optimiser": self.set_optimiser,
                         "set_loss_function": self.set_loss_function,
                         "set_weights": self.set_weights}

    #################### SERVER COMMUNCIATION #######################
        
    async def send_message(self, message):
        if self.websocket is None or not self.websocket.open:
            # Reconnect if the connection is closed or doesn't exist
            await self.connect_client()
        print(2)
        try:
            message = json.dumps(message)
        except Exception as e:
            self.status = f"An error occurred: {e}"
            print(f"An error occurred: {e}")
        print(3)
        try:
            self.status = "Sending message"
            print(self.status)
            await self.websocket.send(message)  # Send the message to the server
            response = await self.websocket.recv()  # Receive a response from the server
            print("Message:", response)
            self.status = f"Received: {response}"
        except websockets.exceptions.ConnectionClosed as e:
            self.status = f"Connection closed: {e}"
            print(f"Connection closed: {e}")
        except Exception as e:
            self.status = f"An error occurred: {e}"
            print(f"An error occurred: {e}")

    async def receive_message(self):
        print("Test")
        async for message in self.websocket:
            message = json.loads(message)
            print(message["header"])
            if message["header"] in self.methods.keys():
                await self.methods[message["header"]](message["body"])
        
    ###################### ADMIN METHODS ############################
        
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
    
    async def send_weights(self, weights):
        try:
            # Attempt to check if the 'model' parameter is valid JSON
            # If parsing succeeds, it's a legitimate JSON string
    
            print(1)
            weights = self.convert_numpy_arrays_to_lists(weights)

            print(2)
            msg = {
                "header": "distribute_weights",
                "body": {"weights": weights,
                         "key": self.key}  # Assuming 'model' is already a valid JSON string
            }

            # Send the JSON message to the server
            
            await self.send_message(msg)
        except json.JSONDecodeError as e:
            # If parsing fails, 'model' is not a valid JSON string
            print(f"Error: 'model' parameter is not a valid JSON string. {e}")

    ######################  METHODS ########################
            
    def convert_numpy_arrays_to_lists(self, data):
        if isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, list):
            return [self.convert_numpy_arrays_to_lists(item) for item in data]
        else:
            return data  # For other data types, just return as is

    #TODO this
    ###
    #async def send_model(self):
    #    msg = {
    #        "header": "set_admin",
    #        "body": {"key": str(self.end_training_session())}
    #    }
    