# Imports required libraries
import pandas
from GreyNsights.host import Dataset, DataOwner

# Load Dataset using reqular pandas
dataset = pandas.read_csv("US_Accidents_June20.csv")

# Register dataowner , a point of improvement is stronger identity management
owner = DataOwner("Bob", port=65441, host="127.0.0.1")

# Hosts the dataset called 'Sample Data'
# In future we need a sort of config file to agree upon permissions between analyst and dataowner
dataset = Dataset(owner, "Sample Data", dataset, whitelist={"Alice": None})

# Begin serving requests
dataset.listen()
