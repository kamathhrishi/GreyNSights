import os
import pandas
from GreyNsights.data_client import VirtualWorker
from GreyNsights.config import Config


def test_example():

    data_path = os.path.join(os.path.dirname(__file__), "animals_and_carrots.csv")
    config_path = os.path.join(os.path.dirname(__file__), "test_config.yaml")

    dataset = pandas.read_csv(data_path, sep=",", names=["animal", "carrots_eaten"])

    config = Config()
    config.load(config_path)
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
