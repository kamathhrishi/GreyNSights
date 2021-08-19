import codecs
import pickle
import random
import socket

import pandas

from GreyNsights.client import VirtualWorker
from GreyNsights.config import Config
from GreyNsights.host import DataOwner, Dataset
from GreyNsights.frameworks import framework

dataset = pandas.read_csv(
    "animals_and_carrots.csv", sep=",", names=["animal", "carrots_eaten"]
)

config = Config()
config.load("test_config.yaml")
owner = VirtualWorker("Bob", config, data=dataset)
# owner = DataOwner("Bob", port=None, host=None,data=dataset)

frameworks = framework(virtual_worker=owner)
pandas = frameworks.pandas

df = owner.data.init_pointer()

df = pandas.DataFrame(df)

print(df)

print(df.describe().get())

print(df["carrots_eaten"].mean().get())

print(df["carrots_eaten"].sum().get())

print((df["carrots_eaten"] > 70).sum().get())

print(df["carrots_eaten"].max().get())
