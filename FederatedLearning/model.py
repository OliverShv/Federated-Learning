import tensorflow as tf
import json

class Model:
    def __init__(self):
        self.model = None
        self.loss_function = None
        self.optimiser = None

        self.avg_graidents= None
        self.gradients = None
        self.gradients_applied = 0

    async def load_model(self, model_str):
        model_json = json.load(model_str)
        self.model = tf.keras.load(model_json)
    
    async def apply_weights(self, weights_str):
        pass

    async def calculate_graidents(self, x = None , y = None):
        self.model.compile(**self.complier_settings)
        
        with tf.GradientTape() as tape:
            # Forward pass
            predictions = self.model(x)
            loss = self.loss_function(y, predictions)

        # Calculate gradients with respect to every trainable variable
        gradients = tape.gradient(loss, self.model.trainable_variables)

    async def apply_graidents(self, gradients):
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
