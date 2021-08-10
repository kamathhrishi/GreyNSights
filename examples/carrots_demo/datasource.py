import codecs
import pickle
import random
import socket

import pandas

from GreyNsights.analyst import Pointer
from GreyNsights.config import Config
from GreyNsights.host import DataOwner, Dataset

dataset = pandas.read_csv(
    "animals_and_carrots.csv", sep=",", names=["animal", "carrots_eaten"]
)


owner = DataOwner("Bob", port=6544, host="127.0.0.1")

config = Config(owner)
config.load("test_config.yaml")

dataset = Dataset(owner, "Sample Data", dataset, config, whitelist={"Alice": None})
dataset.listen()
