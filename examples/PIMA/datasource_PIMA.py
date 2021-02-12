import socket
import codecs
import pickle
import pandas
import random
from GreyNsights.config import Config
from GreyNsights.analyst import Pointer
from GreyNsights.host import Dataset, DataOwner


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
