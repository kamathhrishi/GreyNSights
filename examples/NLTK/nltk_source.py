import socket
import codecs
import pickle
import pandas
import random
from analyst import Pointer
from host import Dataset, DataOwner


# load data
filename = "metamorphosis_clean.txt"
file = open(filename, "rt")
text = file.read()
file.close()


owner = DataOwner("Bob", port=65441, host="127.0.0.1")

dataset = Dataset(owner, "Sample Data", text, whitelist={"Alice": None})
dataset.listen()
