import socket
import codecs
import pickle
import pandas
import random
from GreyNsights.analyst import VirtualWorker
from GreyNsights.host import Dataset, DataOwner
from GreyNsights.config import Config

dataset = pandas.read_csv(
    "animals_and_carrots.csv", sep=",", names=["animal", "carrots_eaten"]
)

config = Config()
config.load("test_config.yaml")
owner = VirtualWorker("Bob", config, data=dataset)
# owner = DataOwner("Bob", port=None, host=None,data=dataset)

df = owner.data.init_pointer()

print(df)

print(df.describe().get())

print(df["carrots_eaten"].mean().get())

print(df["carrots_eaten"].sum().get())

print((df["carrots_eaten"] > 70).sum().get())

print(df["carrots_eaten"].max().get())
