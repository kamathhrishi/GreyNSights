import codecs
import pickle
import random
import socket

import pandas

from GreyNsights.analyst import Pointer
from GreyNsights.config import Config
from GreyNsights.host import DataOwner, Dataset


def run():

    dataset = pandas.read_csv("pima-indians-diabetes.csv")
    # syndata = SyntheticData(dataset, 0.4)
    # gen_data = syndata.fit()

    owner = DataOwner("Bob", port=65441, host="127.0.0.1")

    config = Config(owner)
    config.load("test_config.yaml")

    dataset = Dataset(owner, "Sample Data", dataset, config, whitelist={"Alice": None})
    dataset.listen()


if __name__ == "__main__":

    run()
