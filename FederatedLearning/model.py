import tensorflow as tf
import json
from ast import literal_eval
import numpy as np


#Allow data to be selected
class Model:
    def __init__(self):
        self.model = None
        self.loss_function = None
        self.optimiser = None

    def load_model(self, model_str):
        model_json = json.load(model_str)
        self.model = tf.keras.load(model_json)

        self.start_training_session()

    def set_optimiser(self, optimiser_name):
        try:
            # Instantiate the optimizer using TensorFlow's built-in get method
            self.optimiser = tf.keras.optimizers.get(optimiser_name)
        except ValueError as e:
            # Handle the case where the optimizer name is invalid
            raise ValueError(f"Invalid optimizer name: {optimiser_name}") from e
        
    def set_loss_function(self, loss_function_name):
        try:
            # Instantiate the loss function using TensorFlow's built-in get method
            self.loss_function = tf.keras.losses.get(loss_function_name)
        except ValueError as e:
            # Handle the case where the loss function name is invalid
            raise ValueError(f"Invalid loss function name: {loss_function_name}") from e
    
    def apply_weights(self, weights_str):
        # Convert the string to Python objects (use ast.literal_eval as a safer alternative to eval)
        try:
            from ast import literal_eval
            weights = literal_eval(weights_str)
        except Exception as e:
            raise ValueError(f"Failed to parse weights string: {e}")

        # Convert the lists to numpy arrays
        weights = [np.array(w) for w in weights]

        # Set the weights to the model
        self.model.set_weights(weights)

    def calculate_graidents(self, x = None , y = None):
        self.model.compile(optimizer=self.optimizer, loss=self.loss_function)
        
        with tf.GradientTape() as tape:
            # Forward pass
            predictions = self.model(x)
            loss = self.loss_function(y, predictions)

        # Calculate gradients with respect to every trainable variable
        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.apply_graidents(gradients)

    def compile_model(self):
        # Compile the model once with the specified optimizer and loss function
        self.model.compile(optimizer=self.optimizer, loss=self.loss_function)

    def train_on_batch(self, x, y):
        with tf.GradientTape() as tape:
            predictions = self.model(x, training=True)
            loss = self.loss_function(y, predictions)
        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.apply_gradients(gradients)

    def apply_gradients(self, gradients):
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))

    # Call this method to train the model, similar to model.fit
    def train_model(self, data, epochs):
        for epoch in range(epochs):
            for x_batch, y_batch in data:
                self.train_on_batch(x_batch, y_batch)

    ################ Difference in weights approach #####################

    def start_training_session(self):
        # Store the initial weights at the beginning of a training session
        self.initial_weights = [tf.identity(w) for w in self.model.trainable_variables]

    def end_training_session(self):
        # Get the final weights at the end of a training session
        final_weights = self.model.trainable_variables

        # Compute the difference between the final and initial weights
        weight_differences = [final - initial for final, initial in zip(final_weights, self.initial_weights)]
        return weight_differences

