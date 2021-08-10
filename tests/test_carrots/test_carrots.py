import os

import pandas
import pytest

from GreyNsights.client import VirtualWorker
from GreyNsights.config import Config


@pytest.fixture
def init_pointer():
    data_path = os.path.join(os.path.dirname(__file__), "animals_and_carrots.csv")
    config_path = os.path.join(os.path.dirname(__file__), "test_config.yaml")

    dataset = pandas.read_csv(data_path, sep=",", names=["animal", "carrots_eaten"])

    config = Config()
    config.load(config_path)
    owner = VirtualWorker("Bob", config, data=dataset)

    init_pointer = owner.data.init_pointer()

    return init_pointer, dataset


def test_describe(init_pointer):
    df, dataset = init_pointer
    assert (df.describe().get() == dataset.describe())["carrots_eaten"].all()


def test_mean(init_pointer):
    df, dataset = init_pointer
    assert (df["carrots_eaten"].mean().get() == dataset.mean())["carrots_eaten"].all()


def test_sum(init_pointer):
    df, dataset = init_pointer
    assert (df["carrots_eaten"].sum().get() == dataset.sum())["carrots_eaten"].all()


def test_sum_gt(init_pointer):
    df, dataset = init_pointer
    assert ((df["carrots_eaten"] > 70).sum().get()) == (
        dataset["carrots_eaten"] > 70
    ).sum()


def test_sum_lt(init_pointer):
    df, dataset = init_pointer
    assert ((df["carrots_eaten"] < 70).sum().get()) == (
        dataset["carrots_eaten"] < 70
    ).sum()


def test_max(init_pointer):
    df, dataset = init_pointer
    assert df["carrots_eaten"].max().get() == dataset["carrots_eaten"].max()
