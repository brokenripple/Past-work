# -*- coding: utf-8 -*-
"""CNN_GAP

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11Ash-thuc_3mMPxu7cNWlDzodT7Aqken
"""

from tensorflow.keras.datasets import cifar10 # cifar10 辨識十種物品的圖片
(x_train,y_train), (x_test,y_test) = cifar10.load_data()
trans = ["airplane", "car", "bird", "cat", "deer", "dog", "forg", "horse", "ship", "truck"]

import random
import matplotlib.pyplot as plt

print (x_train.shape)
print (y_train.shape)
print (x_test.shape)
print (y_test.shape)

idx = random.randint(0, x_train.shape[0]-1)
print ("answer:", trans[y_train[idx][0]])
plt.imshow (x_train[idx])

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import Dense, Dropout, Flatten, GlobalAveragePooling2D

#keras.layers.Conv1D(filters, kernel_size, strides=1, padding='valid', data_format='channels_last', dilation_rate=1, activation=None, use_bias=True, kernel_initializer='glorot_uniform', bias_initializer='zeros', kernel_regularizer=None, bias_regularizer=None, activity_regularizer=None, kernel_constraint=None, bias_constraint=None)
#keras.layers.MaxPooling1D(pool_size=2, strides=None, padding='valid', data_format='channels_last')
layers = [
      # 27 (1 filter) * 64 +64 = 1792  32,32,3 張 RGB to 32,32,64 張
      Conv2D (64, 3, padding = "same", activation = "relu", input_shape = (32,32,3)),       # kernel_size = 3 or 4
      MaxPooling2D (),
      # 576 (1 filter) * 128 +128 = 73856 
      Conv2D (128, 3, padding = "same", activation = "relu"),
      MaxPooling2D (),
      Conv2D (256, 3, padding = "same", activation = "relu"),
      MaxPooling2D (),
      #Conv2D (512, 3, padding = "same", activation = "relu"),
      #MaxPooling2D (),
      GlobalAveragePooling2D (),
      Dense (10, activation = "softmax") # 互斥的 softmax 可同時出現 sigmud

]
model = Sequential (layers)
model.summary ()

from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.optimizers import Adam
model.compile(loss=SparseCategoricalCrossentropy(),
       optimizer=Adam(),
       metrics=["accuracy"])

x_train_norm = x_train / 255
x_test_norm = x_test / 255

from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
callbacks = [
      ModelCheckpoint ("model.h5", save_best_only=True), # ModelCheckpoint 從 Goolge Drive 帶可以讀取保存
      EarlyStopping (patience = 5, restore_best_weights = True)]

model.fit(x_train_norm, y_train, batch_size = 100, epochs = 20, validation_split=0.1, callbacks = callbacks)# verbose > 不顯示進度條

model.evaluate(x_test_norm, y_test)

import pandas as pd
from sklearn.metrics import confusion_matrix
pre = model.predict_classes(x_test_norm)
mat = confusion_matrix(y_test, pre)
pd.DataFrame(mat,
      index=["{}(原本)".format(n) for n in trans],
      columns=["{}(預測)".format(n) for n in trans])

pre = model.predict_classes(x_test_norm)
print(pre.shape)
print(y_test.shape)
y_test_r = y_test.reshape(10000)
print(y_test_r.shape)
pre

# subplot(總高度, 總寬度, ith)
import numpy as np
idx = np.nonzero(pre != y_test_r)[0]
idx = idx[:200]
false_img = x_test[idx]
false_label = y_test_r[idx]
false_pre = pre[idx]

plt.figure(figsize=(14, 42))
width = 10
height = len(false_img) // width + 1
for i in range(len(false_img)):
    plt.subplot(height, width, i+1)
    title = "[O]:{}\n[P]:{}".format(trans[false_label[i]], trans[false_pre[i]])
    plt.title(title)
    plt.axis("off")
    plt.imshow(false_img[i])

# pip install pillow
import PIL
import requests
url = input("輸入網址:")
h = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}
response = requests.get(url, stream=True, verify=False, headers=h)
img = PIL.Image.open(response.raw).resize((32, 32))
img_np = np.array(img)
test = img_np.reshape(1, 32, 32, 3) / 255
probs = model.predict(test)[0]
for i, p in enumerate(probs):
    print(trans[i], "的機率是:", round(p, 3))
ans = model.predict_classes(test)[0]
print("應該是:", trans[ans])
plt.imshow(img_np)