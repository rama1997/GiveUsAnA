import scipy
import numpy as np
import torch
import tensorflow as tf
import scipy.signal
import cv2

# Discounting function used to calculate discounted returns.
def discount(x, gamma):
    return scipy.signal.lfilter([1], [1, -gamma], x[::-1], axis=0)[::-1]

def resize(image):
    return cv2.cvtColor(cv2.resize(image, (84, 84)), cv2.COLOR_RGB2GRAY)

def getPixels(frame):
    width = frame.width
    height = frame.height
    channels = frame.channels
    pixels = np.array(frame.pixels, dtype=np.uint8)
    img = np.reshape(pixels, (height, width, channels))
    return img

def process_pixels(frame, video_height, video_width):
    s2 = np.frombuffer(frame.pixels, dtype=np.uint8)
    s2 = s2.reshape((video_height, video_width, 3))
    s3 = resize(getPixels(frame))
    s1 = s3.reshape([84 * 84 * 1])
    return s1, s2, s3

# Copies one set of variables to another.
# Used to set worker network parameters to those of global network.
def update_target_graph(from_scope,to_scope):
    from_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, from_scope)
    to_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, to_scope)
    op_holder = []
    for from_var,to_var in zip(from_vars,to_vars):
        op_holder.append(to_var.assign(from_var))
    return op_holder

#Used to initialize weights for policy and value output layers
def normalized_columns_initializer(std=1.0):
    def _initializer(shape, dtype=None, partition_info=None):
        out = np.random.randn(*shape).astype(np.float32)
        out *= std / np.sqrt(np.square(out).sum(axis=0, keepdims=True))
        return tf.constant(out)
    return _initializer
