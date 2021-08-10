# python dependencies
import random

# lib dependencies
from .command import Command
from .generic import Message


class Analyst:
    """Class to keep the identity of analyst. In future I would want this to be linked to identity managemenet somehow.
    Link with public certificate?

    Args:
        name[str]: Name of the analyst
        host[str]: Host of analyst [Not functional yet]
        port[int]: Port of analyst [Not functional yet]
        type[str]: Whether its the original analyst or a reference

    """

    def __init__(self, name: str, host: str, port: int, type: str = None):

        self.name = name
        self.host = host
        self.port = port
        self.type = type


class Pointer:
    """Pointers store references to datasets or results of datasets. Instead of sending the entire dataset back and forth , the computed results are stored
    in the DataOwner's side and can be manipulated or retrieved according to convinience , reducing communication costs.

    Args:
        host[str]: Name of the host of pointer
        port[int]: Port of pointer
        data: The data stored in the pointer
        additional_data[dict]: Additional data to be passed on through pointer
    """

    def __init__(
        self,
        owner,
        dataset: str,
        host: str = None,
        port: int = None,
        data=None,
        chain=None,
        data_type=None,
        additional_data: dict = {},
        id: int = None,
        child=None,
    ):

        # Use __ to keep attributes private

        from .client import VirtualWorker
        from .host import DataOwner

        # self.owner = owner
        self.dataset = dataset
        self.chain = chain
        self.virtual_worker = None

        if isinstance(owner, VirtualWorker):
            self.virtual_worker = owner

        if owner == DataOwner:
            self.port = DataOwner.port
            self.host = host.host
        else:
            self.port = port
            self.host = host

        self.owner_name = owner.name

        if type(self.owner_name) != str:
            raise TypeError

        if id:
            self.id = id
        else:
            self.id = random.randint(0, 1000000000000)

        self.access = None
        self.fn = dir(data)
        self.dtype = type(data)

        if hasattr(data, "__len__"):
            self.length_init = len(data)
        else:
            self.length_init = None

        if hasattr(data, "shape"):
            self.shape_init = list(data.shape)
            if len(self.shape_init) != 0:
                self.shape_init[0] = -1
                self.shape_init = tuple(self.shape_init)
        else:
            self.shape_init = None

        if hasattr(data, "columns"):
            self.columns_init = data.columns
        else:
            self.columns_init = None

        self.additional_data = additional_data
        self.overloaded_func = {"get": self.get_data}

        self.properties = {
            "columns": self.columns_init,
            "shape": self.shape_init,
            "dtype": self.dtype,
            "create_shares": self.create_shares,
            "get_shares": self.get_shares,
        }

    def __str__(self) -> str:

        string = ""
        string += "\n"
        string += "Pointer" + "->" + self.owner_name
        string += "\n"
        string += "\t \t dataset" + ":" + str(self.dataset)
        string += "\n"
        string += "\t \t dtype" + ":" + str(self.dtype)
        string += "\n"
        string += "\t \t id" + ":" + str(self.id)
        string += "\n"
        if self.port:
            string += "\t \t port" + ":" + str(self.port)
        else:
            string += "\t \t port" + ":" + " None"

        string += "\n"
        if self.host:
            string += "\t \t host" + ":" + self.host
        else:
            string += "\t \t host" + ":" + " None"
        string += "\n"

        return string

    def __len__(self) -> int:
        return self.length

    def hook(self) -> None:
        """
        Provide the pointer the same substitute functions as the desired datatype.
        """

        # Hook all the functions
        for function in self.fn:

            if (
                function != "__class__"
                and function != "__dict__"
                and function != "__weakref__"
                and function not in self.overloaded_func.keys()
            ):

                self.additional_data["id"] = self.id

                cmd = Command(
                    self.host,
                    self.port,
                    "query",
                    additional_data=self.additional_data,
                    virtual_worker=self.virtual_worker,
                )
                setattr(cmd, "name", function)
                setattr(cmd, "port", self.port)
                setattr(cmd, "id", self.id)
                setattr(self, function, cmd.hook_method)

        # Override the hooked function with custom functionality
        for function in self.overloaded_func.keys():

            if (
                function != "__class__"
                and function != "__dict__"
                and function != "__weakref__"
            ):
                self.additional_data["id"] = self.id

                cmd = Command(
                    self.host,
                    self.port,
                    "query",
                    additional_data=self.additional_data,
                    virtual_worker=self.virtual_worker,
                )
                setattr(cmd, "name", function)
                setattr(cmd, "port", self.port)
                setattr(cmd, "id", self.id)
                setattr(self, function, cmd.hook_method)

        # Override the hooked function with properties of datatype
        for function in self.properties.keys():

            if (
                function != "__class__"
                and function != "__dict__"
                and function != "__weakref__"
            ):
                self.additional_data["id"] = self.id

                cmd = Command(
                    self.host,
                    self.port,
                    "query",
                    additional_data=self.additional_data,
                    virtual_worker=self.virtual_worker,
                )
                setattr(cmd, "name", function)
                setattr(cmd, "port", self.port)
                setattr(cmd, "id", self.id)
                setattr(self, function, self.properties[function])

    def operate(self, cmd: str, x=None):
        """Execute a given arithmetic/logical operation by sending a command across.
        Currently supports pointer operation on same dataset only.

        Args:
            cmd[str]: The command to be sent across
            x[Pointer/int/float]: The other operator
        Returns:
            Pt[Pointer]: Pointer to the given computation."""

        # Perform computation depending on if x is a pointer or a float/int
        if type(x) != None and type(x) == type(self):

            # Check if the pointers lie on the same dataset
            if self.dataset == x.dataset:
                command = Command(
                    self.host,
                    self.port,
                    cmd,
                    additional_data={
                        "name": self.dataset,
                        "pt_id1": self.id,
                        "pt_id2": x.id,
                    },
                    virtual_worker=self.virtual_worker,
                )
                return_msg = command.execute(cmd)
                return_pt = return_msg.data
                return_pt.hook()
                return return_pt

            else:
                raise NotImplementedError("Pointers do not lie in the same dataset")

        else:
            command = Command(
                self.host,
                self.port,
                cmd,
                additional_data={"name": self.dataset, "pt_id1": self.id, "x": x},
                virtual_worker=self.virtual_worker,
            )
            return_msg = command.execute(cmd)
            return_pt = return_msg.data
            return_pt.hook()
            return return_pt

    def __add__(self, x):
        return self.operate("__add__", x)

    def __truediv__(self, x):
        return self.operate("__truediv__", x)

    def __sub__(self, x):
        return self.operate("__sub__", x)

    def __mul__(self, x):
        return self.operate("__mul__", x)

    def __and__(self, x):
        return self.operate("__and__", x)

    def __or__(self, x):
        return self.operate("__or__", x)

    def __invert__(self):
        return self.operate("__invert__")

    def __lt__(self, x):
        return self.operate("__lt__", x)

    def __ge__(self, x):
        return self.operate("__ge__", x)

    def __gt__(self, x):
        return self.operate("__gt__", x)

    def __lte__(self, x):
        return self.operate("__lte__", x)

    def __eq__(self, x):
        return self.operate("__eq__", x)

    def __ne__(self, x):
        return self.operate("__ne__", x)

    def create_shares(self, workers) -> None:

        cmd = Command(
            self.host,
            self.port,
            "create_shares",
            additional_data=self.additional_data,
            virtual_worker=self.virtual_worker,
        )
        cmd.execute("create_shares", distributed_workers=workers)

    def __setitem__(self, key, newvalue):

        cmd = Command(
            self.host,
            self.port,
            "__setitem__",
            additional_data=self.additional_data,
            virtual_worker=self.virtual_worker,
        )

        if type(newvalue) == type(self):

            return_msg = cmd.execute(
                "__setitem__",
                key=key,
                newvalue=Message(
                    "",
                    "",
                    "Pointer",
                    Pointer,
                    data=newvalue.id,
                    extra={"chain": self.chain},
                ),
            )

        else:

            return_msg = cmd.execute("__setitem__", key=key, newvalue=newvalue)

        return_pt = return_msg.data
        return_pt.hook()
        return return_pt

    def __getitem__(self, idx):

        cmd = Command(
            self.host,
            self.port,
            "__getitem__",
            additional_data=self.additional_data,
            virtual_worker=self.virtual_worker,
        )

        if type(idx) == type(self):
            return_msg = cmd.execute(
                "__getitem__",
                idx=Message(
                    "", "", "Pointer", Pointer, data=idx.id, extra={"chain": self.chain}
                ),
            )

        else:
            return_msg = cmd.execute("__getitem__", idx=idx)

        return_pt = return_msg.data
        return_pt.hook()
        return return_pt

    def pt_duplicate(self):

        pt = Pointer(
            self.owner,
            self.name,
            self.host,
            self.port,
            None,
            child=None,
            chain=self.chain,
            data_type=self.data_type,
            additional_data=self.additional_data,
        )

        return pt

    def get_data(self, Pt1):
        """Function to get the raw data from a given pointer. Will have to integrate with a QueryAnalyzer
        to understand if the dataset is a private datapoint or not.

        Args:
            Pt1[Pointer]: The pointer from which raw data must be retrieved
        Returns:
            pt: The raw data from pointer"""

        additional_data = Pt1.additional_data
        additional_data["id"] = Pt1.id
        cmd = Command(
            Pt1.host,
            Pt1.port,
            "get",
            additional_data=additional_data,
            virtual_worker=self.virtual_worker,
        )
        return_msg = cmd.execute("get")
        return_data = return_msg.data

        return return_data

    def sample_synthetic(self):
        """
        additional_data = {}
        additional_data["name"] = self.name
        additional_data["id"] = self.id
        cmd = Command(
            self.host,
            self.port,
            "sample_synthetic",
            additional_data=additional_data,
            virtual_worker=self.virtual_worker,
        )
        return_msg = cmd.execute("sample_synthetic")
        return_pt = return_msg.data
        return_pt.hook()
        return return_pt
        """
        raise NotImplementedError(
            "Sampling synthetic datasets is not currently available."
        )

    def get_shares(self, workers):
        cmd = Command(
            self.host,
            self.port,
            "get_shares",
            additional_data=self.additional_data,
            virtual_worker=self.virtual_worker,
        )
        return_msg = cmd.execute("get_shares", distributed_workers=workers)
        return_pt = return_msg.data
        # return_pt.hook()
        return return_pt
