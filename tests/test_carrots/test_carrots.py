import socket
import codecs
import pickle
import pandas
import random
from GreyNsights.data_client import VirtualWorker
from GreyNsights.host import Dataset, DataOwner
from GreyNsights.config import Config


def test_example():

    dataset = pandas.read_csv(
        "animals_and_carrots.csv", sep=",", names=["animal", "carrots_eaten"]
    )

    config = Config()
    config.load("test_config.yaml")
    owner = VirtualWorker("Bob", config, data=dataset)
    # owner = DataOwner("Bob", port=None, host=None,data=dataset)

    df = owner.data.init_pointer()

    assert (df.describe().get() == dataset.describe())["carrots_eaten"].all()
    assert (df["carrots_eaten"].mean().get() == dataset.mean())["carrots_eaten"].all()
    assert (df["carrots_eaten"].sum().get() == dataset.sum())["carrots_eaten"].all()
    assert ((df["carrots_eaten"] > 70).sum().get()) == (
        dataset["carrots_eaten"] > 70
    ).sum()
    assert df["carrots_eaten"].max().get() == dataset["carrots_eaten"].max()
