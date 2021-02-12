import pandas
from host import Dataset, DataOwner
from config import Config

dataset = pandas.read_csv("week_data.csv")

owner = DataOwner("Bob", port=65444, host="127.0.0.1")

config = Config(owner)
config.load("test_config.yaml")

dataset = Dataset(owner, "Sample Data1", dataset, config, whitelist={"Alice": None})
dataset.listen()
