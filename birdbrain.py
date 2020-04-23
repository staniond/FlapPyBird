import tensorflow as tf
from tensorflow.keras import layers


class BirdBrain:
    def __init__(self):
        # NN with 5 input nodes, 8 hidden nodes and 2 output nodes
        self.model = tf.keras.Sequential()
        self.model.add(layers.Dense(8, input_shape=(5,), activation='sigmoid', kernel_initializer='random_uniform',
                                    bias_initializer='random_uniform'))
        self.model.add(layers.Dense(2, activation='softmax', kernel_initializer='random_uniform',
                                    bias_initializer='random_uniform'))

    def predict(self, world_data):
        return self.model.predict([world_data])[0]

    def clone(self):
        new_brain = BirdBrain()
        new_brain.model.set_weights(self.model.get_weights())
        return new_brain

    def mutate(self, probability):
        pass

    @staticmethod
    def crossover(brain1, brain2):
        return brain1, brain2
