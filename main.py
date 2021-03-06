import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.examples.tutorials.mnist import input_data
import time
from PIL import Image
import random
import sys
from random import choice
import keras
from keras import backend as K
from skimage.io import imsave
from keras.callbacks import ModelCheckpoint,ReduceLROnPlateau,LearningRateScheduler
#按顺序构成的模型，一层之后接一层，最简单的模型
from keras.models import Sequential,Model
#Dense全连接层
from keras.layers import Dense,Activation,Dropout,Convolution2D,MaxPooling2D,Flatten,Conv2D,MaxPool2D,Conv2DTranspose,UpSampling2D,Deconvolution2D,Input,Lambda,add,concatenate
from keras.layers.recurrent import SimpleRNN,LSTM,GRU
from keras.optimizers import SGD,Adam
from keras.layers.advanced_activations import PReLU
from keras.datasets import mnist
from keras.utils import np_utils
from keras.regularizers import l2
from keras.models import load_model,save_model
from keras.models import model_from_json
from keras.utils.vis_utils import plot_model
from keras.applications.vgg16 import VGG16
from scipy.optimize import fmin_l_bfgs_b
import pydot_ng as pydot
import json
import cv2
import h5py
import math
import warnings
from keras.applications import vgg19,VGG16
from keras.preprocessing.image import ImageDataGenerator,array_to_img,img_to_array,load_img,save_img
import os
warnings.filterwarnings("ignore")
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

# 行
img_nrows = 200
# 列
img_ncols = 200

f_outputs=[]
#图片预处理
def preprocess_image(image_path):
    img = load_img(image_path, target_size=(img_nrows, img_ncols))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = vgg19.preprocess_input(img)
    return img

def deprocess_image(x):
    if K.image_data_format() == 'channels_first':
        x = x.reshape((3, img_nrows, img_ncols))
        x = x.transpose((1, 2, 0))
    else:
        x = x.reshape((img_nrows, img_ncols, 3))
    # 加上颜色均值
    x[:, :, 0] += 103.939
    x[:, :, 1] += 116.779
    x[:, :, 2] += 123.68
    # 'BGR'->'RGB'
    x = x[:, :, ::-1]
    x = np.clip(x, 0, 255).astype('uint8')
    return x




def gram_matrix(x):
    assert K.ndim(x) == 3
    if K.image_data_format() == 'channels_first':
        features = K.batch_flatten(x)
    else:
        features = K.batch_flatten(K.permute_dimensions(x, (2, 0, 1)))
    gram = K.dot(features, K.transpose(features))
    return gram

def style_loss(style, combination):
    assert K.ndim(style) == 3
    assert K.ndim(combination) == 3
    S = gram_matrix(style)
    C = gram_matrix(combination)
    channels = 3
    size = img_nrows * img_ncols
    return K.sum(K.square(S - C)) / (4.0 * (channels ** 2) * (size ** 2))

def content_loss(base, combination):
    return K.sum(K.square(combination - base))

def total_variation_loss(x):
    assert K.ndim(x) == 4
    if K.image_data_format() == 'channels_first':
        a = K.square(
            x[:, :, :img_nrows - 1, :img_ncols - 1] - x[:, :, 1:, :img_ncols - 1])
        b = K.square(
            x[:, :, :img_nrows - 1, :img_ncols - 1] - x[:, :, :img_nrows - 1, 1:])
    else:
        a = K.square(
            x[:, :img_nrows - 1, :img_ncols - 1, :] - x[:, 1:, :img_ncols - 1, :])
        b = K.square(
            x[:, :img_nrows - 1, :img_ncols - 1, :] - x[:, :img_nrows - 1, 1:, :])
    return K.sum(K.pow(a + b, 1.25))




def eval_loss_and_grads(x):
    if K.image_data_format() == 'channels_first':
        x = x.reshape((1, 3, img_nrows, img_ncols))
    else:
        x = x.reshape((1, img_nrows, img_ncols, 3))
    outs = f_outputs([x])
    loss_value = outs[0]
    if len(outs[1:]) == 1:
        grad_values = outs[1].flatten().astype('float64')
    else:
        grad_values = np.array(outs[1:]).flatten().astype('float64')
    return loss_value, grad_values



class Evaluator(object):

    def __init__(self):
        self.loss_value = None
        self.grads_values = None

    def loss(self, x):
        assert self.loss_value is None
        loss_value, grad_values = eval_loss_and_grads(x)
        self.loss_value = loss_value
        self.grad_values = grad_values
        return self.loss_value

    def grads(self, x):
        assert self.loss_value is not None
        grad_values = np.copy(self.grad_values)
        self.loss_value = None
        self.grad_values = None
        return grad_values









def run(a,b):
    # 设置参数
    # base_image = '1.jpg'
    # style_image = '2.png'

    global img_nrows

    global img_ncols

    global f_outputs
    base_image = a
    style_image = b
    result_image = 'result/'
    iterations = 400
    total_variation_weight = 8.5e-5
    style_weight = 1.0
    content_weight = 0.025


    # 设置产生图片的大小(缩放）
    width, height = load_img(base_image).size
    # 行
    img_nrows = 600
    # 列
    img_ncols = int(width * img_nrows / height)

    # 读入内容和风格图，包装为Keras张量
    base_image_K = K.variable(preprocess_image(base_image))
    style_reference_image = K.variable(preprocess_image(style_image))

    # 初始化一个待优化的占位符
    if K.image_data_format() == 'channels_first':
        combination_image = K.placeholder((1, 3, img_nrows, img_ncols))
    else:
        combination_image = K.placeholder((1, img_nrows, img_ncols, 3))

    # 将3个张量串联在一起
    input_tensor = K.concatenate([base_image_K,
                                  style_reference_image,
                                  combination_image], axis=0)

    model = vgg19.VGG19(input_tensor=input_tensor,
                        weights='imagenet', include_top=False)
    print('Model loaded.')

    # get the symbolic outputs of each "key" layer (we gave them unique names).
    outputs_dict = dict([(layer.name, layer.output) for layer in model.layers])

    # combine these loss functions into a single scalar
    loss = K.variable(0.0)
    layer_features = outputs_dict['block5_conv2']
    base_image_features = layer_features[0, :, :, :]
    combination_features = layer_features[2, :, :, :]
    loss = loss + content_weight * content_loss(base_image_features,
                                                combination_features)

    feature_layers = ['block1_conv1', 'block2_conv1',
                      'block3_conv1', 'block4_conv1',
                      'block5_conv1']
    for layer_name in feature_layers:
        layer_features = outputs_dict[layer_name]
        style_reference_features = layer_features[1, :, :, :]
        combination_features = layer_features[2, :, :, :]
        sl = style_loss(style_reference_features, combination_features)
        loss = loss + (style_weight / len(feature_layers)) * sl
    loss = loss + total_variation_weight * total_variation_loss(combination_image)

    # get the gradients of the generated image wrt the loss
    grads = K.gradients(loss, combination_image)

    outputs = [loss]
    if isinstance(grads, (list, tuple)):
        outputs += grads
    else:
        outputs.append(grads)

    f_outputs = K.function([combination_image], outputs)

    evaluator = Evaluator()

    x = preprocess_image(base_image)

    for i in range(iterations):
        start_time = time.time()
        x, min_val, info = fmin_l_bfgs_b(evaluator.loss, x.flatten(),
                                         fprime=evaluator.grads, maxfun=20)
        print('Current loss value:', min_val)
        # save current generated image
        img = deprocess_image(x.copy())
        fname = result_image + '_at_iteration_%d.png' % i
        if i % 10 == 0:
            save_img(fname, img)
        end_time = time.time()
        print('Iteration %d completed in %ds' % (i, end_time - start_time))













