import codecs
import pickle
import random
import socket

import pandas

import GreyNsights
from GreyNsights.analyst import Pointer
from GreyNsights.config import Config
from GreyNsights.host import DataOwner, Dataset

dataset = pandas.read_csv("US_Accidents_June20.csv")

owner = DataOwner("Bob", port=65441, host="127.0.0.1")

config = Config(owner)
config.load("test_config.yaml")

dataset = Dataset(owner, "Sample Data", dataset, config, whitelist={"Alice": None})
dataset.listen()
