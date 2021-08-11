import codecs
import pickle
import random
import socket

import pandas
import numpy as np

from GreyNsights.client import VirtualWorker
from GreyNsights.config import Config
from GreyNsights.host import DataOwner, Dataset

dataset = np.array([1,2,3,4,5])

config = Config()
config.load("test_config.yaml")
owner = VirtualWorker("Bob", config, data=dataset)
# owner = DataOwner("Bob", port=None, host=None,data=dataset)

df = owner.data.init_pointer()

print(df)

#print(df.describe().get())

print(df.mean().get())

print(df.sum().get())

#print((df > 70).sum().get())

print(df.max().get())
