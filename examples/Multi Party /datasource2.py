import pandas
from GreyNsights.host import Dataset, DataOwner
from GreyNsights.config import Config

dataset = pandas.read_csv("week_data.csv")

owner = DataOwner("Bob", port=65446, host="127.0.0.1")

config = Config(owner)
config.load("test_config.yaml")

dataset = Dataset(owner, "Sample Data2", dataset, config, whitelist={"Alice": None})
dataset.listen()
