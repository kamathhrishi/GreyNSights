from GreyNsights.client import DataWorker, DataSource
from GreyNsights.analyst import Analyst
from GreyNsights.multiparty import WorkerGroup
from GreyNsights.frameworks import framework

frameworks = framework()

pandas = frameworks.pandas

identity = Analyst("Alice", port=65441, host="127.0.0.1")

# Initialize DataOwner1
worker1 = DataWorker(port=65444, host="127.0.0.1")
dataset1 = DataSource(identity, worker1, "Sample Data1")
config1 = dataset1.get_config()
dataset1 = config1.approve().init_pointer()

# Initialize DataOwner2
worker2 = DataWorker(port=65446, host="127.0.0.1")
dataset2 = DataSource(identity, worker2, "Sample Data2")
config2 = dataset2.get_config()
dataset2 = config2.approve().init_pointer()

# Initialize DataOwner3
worker3 = DataWorker(port=65442, host="127.0.0.1")
dataset3 = DataSource(identity, worker3, "Sample Data3")
config3 = dataset3.get_config()
dataset3 = config3.approve().init_pointer()

# Create a workergroup to which commands to all workers are executed together
group = WorkerGroup(identity)
group.add(dataset1, worker1, config1)
group.add(dataset2, worker2, config2)
group.add(dataset3, worker3, config3)

pt = group.init_pointer()

# Perform queries on all three workers together
er = pt["Money spent (euros)"].sum() + pt["Money spent (euros)"].sum()

"""Workers communicate with each other and create shares.
these exchanged shares are added by the analyst to obtain the summation of shares
which can be divided to obtain the average
#(Secure Aggregation)"""

er = pt["Money spent (euros)"].sum().get()

print(er)
