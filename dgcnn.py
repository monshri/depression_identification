# -*- coding: utf-8 -*-
"""DGCNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1c2te9aioGheoiVqPY-JADuwsx-RxrPgP
"""

!pip install stellargraph

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from sklearn.utils import shuffle
import pandas as pd

import stellargraph as sg
from stellargraph.mapper import PaddedGraphGenerator
from stellargraph.layer import DeepGraphCNN
from stellargraph import StellarGraph

from stellargraph import datasets

from sklearn import model_selection

from tensorflow.keras import Model
from tensorflow.keras.optimizers import Adam, SGD
from tensorflow.keras.layers import Dense, Conv1D, MaxPool1D, Dropout, Flatten
from tensorflow.keras.losses import binary_crossentropy
import tensorflow as tf
from tqdm import tqdm

#Loads Adjacency Matrices
A = sio.loadmat('Adjacency_Full_.mat')
A = A['Full_Chunked']
#Loads Graph Signal Vector X
X = sio.loadmat('X_vector_Full_.mat')
X = X['X_vec']
#Create Labels
Y = np.append(np.zeros(shape=(3648,1)), np.ones(shape=(2156,1))) #First 3648 entries of A & X are healthy, rest 2156 are depressed

A, X, Y = shuffle(np.reshape(A, (5804,62,62)), np.reshape(X, (5804, 62, 2)), np.reshape(Y, (5804,1,1))) #Shuffle to randomize order and reshape for consistent shuffle across A, X & Y
Y = np.reshape(Y, (5804,))
graph_labels = pd.DataFrame(Y)  #Store labels in a pd DataFrame

# Format input data (A, X) for GCN input as StellarGraph object 
graphs = []
for participant in tqdm(range(len(X))):
  G = nx.from_numpy_matrix(A[participant])  #Create networkx graph object from ath Adjacency Matrix
  for node in range(62): #For each graph
    G.nodes[node]['x'] = X[participant, node, :]  #Add node features to networkx Graph
  graphs.append(StellarGraph.from_networkx(G, node_features="x")) #Create and store StellarGraph objects for training

generator = PaddedGraphGenerator(graphs=graphs)

k = 10  # the number of rows for the output tensor
layer_sizes = [64, 32, 16, 8, 4, 2, 1]  #GCN Layer Size

dgcnn_model = DeepGraphCNN(
    layer_sizes=layer_sizes,
    activations=["relu", "relu", "tanh", "tanh", "tanh","tanh","tanh"],
    k=k,
    bias=True,
    generator=generator,
)

x_inp, x_out = dgcnn_model.in_out_tensors()
x_out = Conv1D(filters=128, kernel_size=sum(layer_sizes), strides=sum(layer_sizes))(x_out)
x_out = MaxPool1D(pool_size=2)(x_out)
x_out = Conv1D(filters=64, kernel_size=5, strides=1)(x_out)
#x_out = SortPooling(k, flatten_output=True)
x_out = Flatten()(x_out)
#x_out = Dense(units=512, activation="relu")(x_out)
x_out = Dense(units=64, activation="relu")(x_out)
x_out = Dropout(rate=0.5)(x_out)
predictions = Dense(units=1, activation="sigmoid")(x_out)

model = Model(inputs=x_inp, outputs=predictions)
model.compile(optimizer=Adam(lr=0.0001), loss=binary_crossentropy, metrics=["acc"],)

train_graphs, test_graphs = model_selection.train_test_split(graph_labels, train_size=0.8, test_size=None, stratify=graph_labels,)

gen = PaddedGraphGenerator(graphs=graphs)
train_gen = gen.flow(
    list(train_graphs.index - 1),
    targets=train_graphs.values,
    batch_size=32,
    symmetric_normalization=False,
)

test_gen = gen.flow(
    list(test_graphs.index - 1),
    targets=test_graphs.values,
    batch_size=1,
    symmetric_normalization=False,
)

epochs = 20

history = model.fit(
    train_gen, epochs=epochs, verbose=1, validation_data=test_gen, shuffle=True,
)

sg.utils.plot_history(history)

test_metrics = model.evaluate(test_gen)
print("\nTest Set Metrics:")
for name, val in zip(model.metrics_names, test_metrics):
    print("\t{}: {:0.4f}".format(name, val))