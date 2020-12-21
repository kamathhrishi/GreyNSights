import socket
import codecs
import pickle
import pandas
import random
from GreyNsights.analyst import Pointer
from GreyNsights.host import Dataset, DataOwner

dataset = pandas.read_csv(
    "animals_and_carrots.csv", sep=",", names=["animal", "carrots_eaten"]
)

owner = DataOwner("Bob", port=6544, host="127.0.0.1")

dataset = Dataset(owner, "Sample Data", dataset, whitelist={"Alice": None})
dataset.listen()
