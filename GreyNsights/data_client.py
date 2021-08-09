# lib dependencies
from .command import Command


class DataWorker:
    """A class which represents the operations which respect to dataworkers.

    Args:
        host[str]: Host of given dataworker
        port[int]: Port of the dataworker
        data: No idea why this exists"""

    def __init__(
        self,
        host: str,
        port: int,
        data=None,
    ):
        self.port = port
        self.host = host
        self.data = data


class VirtualWorker:
    """A class which represents the operations which respect to dataworkers.

    Args:
        host[str]: Host of given dataworker
        port[int]: Port of the dataworker
        data: No idea why this exists"""

    def __init__(self, name: str, config, data=None, object_type: str = "original"):

        from .host import Dataset

        self.name = name
        self.port = None
        self.host = None
        self.config = config
        self.type = object_type
        self.objects = {}
        # Make this private type
        self.type = object_type
        self.objects = {}
        self.temp_graph = {}
        self.graph = {}
        self.buffer = {}
        if config.privacy_budget != "None":
            from .reporter import DPReporter

            self.dp_reporter = DPReporter(config.privacy_budget, 0.7)
        else:
            self.dp_reporter = None

        self.permission = "AGGREGATE-ONLY"

        dataset = Dataset(self, "sample data", data, self.config, None)
        from .analyst import Analyst

        self.data = DataSource(
            Analyst("Alice", port=65442, host="127.0.0.1"),
            self,
            self.name,
            local_dataset=dataset,
        )

    def register_obj(self, name, obj):
        self.objects[name] = obj

    def __str__(self):
        string = ""
        string += "\n"
        string += "Pointer"
        string += f"Name: {self.name}"
        string += "\n"

        return string


class DataSource:
    """Establishes a connection with the dataset hosted by the datasource.

    Args:
        worker[DataWorker]: The host of datasource
        name[str]: Name of dataset"""

    def __init__(self, analyst, worker: DataWorker, name: str, local_dataset=None):
        self.virtual = isinstance(worker, VirtualWorker)
        self.owner = worker
        self.name = name
        self.additional_data = {"name": name, "sender": analyst.name}
        self.local_dataset = local_dataset

    def init_pointer(self):
        """Initialized pointer from the hosted dataset.

        Returns:
            returned_pt[Pointer]: The returned pointer"""
        if not self.virtual:
            cmd = Command(
                self.owner.host,
                self.owner.port,
                "init_query",
                additional_data=self.additional_data,
            )
            returned_msg = cmd.execute("init")
            returned_pt = returned_msg.data
            returned_pt.hook()
            return returned_pt

        else:
            cmd = Command(
                None,
                None,
                "init_query",
                additional_data=self.additional_data,
                virtual_worker=self.owner,
            )
            returned_msg = cmd.execute("init")
            returned_pt = returned_msg.data
            returned_pt.hook()
            return returned_pt

    def get_config(self):
        """Initialized pointer from the hosted dataset.

        Returns:
            returned_pt[Pointer]: The returned pointer"""
        cmd = Command(
            self.owner.host,
            self.owner.port,
            "get_config",
            additional_data=self.additional_data,
        )
        returned_msg = cmd.execute("get_config")
        returned_pt = returned_msg.data
        return returned_pt

    def send(self, obj):
        """Send data across data to the given dataset

        Args:
            obj: A python object
        Returns:
            returned_pt[Pointer]: Pointer to the sent object

        """
        cmd = Command(
            self.owner.host,
            self.owner.port,
            "store",
            additional_data=self.additional_data,
        )
        returned_msg = cmd.execute("store", obj=obj)
        returned_pt = returned_msg.data
        returned_pt.hook()
        return returned_pt
