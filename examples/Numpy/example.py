import numpy as np

from GreyNsights.client import VirtualWorker
from GreyNsights.config import Config
from GreyNsights.frameworks import framework
from GreyNsights.host import DataOwner, Dataset

array = np.array([1, 2, 3, 4, 5])

config = Config()
config.load("test_config.yaml")
owner = VirtualWorker("Bob", config, data=array)

# numpy support doesn't DP support yet

# owner = DataOwner("Bob", port=None, host=None,data=dataset)

array = owner.data.init_pointer()

print("OWNER OBJECTS: ",owner.objects)

frameworks = framework(virtual_worker=owner)
numpy = frameworks.numpy

print(numpy.mean(array).get())

print(array)
print(array.mean().get())
print(array.sum().get())
print(array.max().get())
