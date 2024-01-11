import tensorflow as tf
import json

class Model:
    def __init__(self):
        self.model = None
        self.complier_settings = None
        self.fit_settings = None

    def string_to_model(self, model_str):
        model_json = json.load(model_str)
        self.model = tf.keras.load(model_json)

    def train(self):
        self.model.compile(**self.complier_settings)
        self.model.fit(**self.fit_settings)
