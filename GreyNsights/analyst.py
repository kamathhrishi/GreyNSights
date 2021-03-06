import pickle
import dill
import socket
import random
from types import ModuleType

from .generic import Message, PrivateDataAccess
from .mpc import reconstruct
from .utils import send_msg, recv_msg, encode_msg


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

        # Use __ to make attributes private

        from .host import DataOwner

        # self.owner = owner
        self.dataset = dataset
        self.chain = chain

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
        # self.data = data

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

    def __str__(self):

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
        string += "\t \t port" + ":" + str(self.port)
        string += "\n"
        string += "\t \t host" + ":" + self.host
        string += "\n"

        return string

    def __len__(self):

        return self.length

    def hook(self):
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
                    self.host, self.port, "query", additional_data=self.additional_data
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
                    self.host, self.port, "query", additional_data=self.additional_data
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
                    self.host, self.port, "query", additional_data=self.additional_data
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
                )
                return_msg = command.execute(cmd)
                return_pt = return_msg.data
                return_pt.hook()
                return return_pt

            else:

                raise NotImplementedError

        else:

            command = Command(
                self.host,
                self.port,
                cmd,
                additional_data={"name": self.dataset, "pt_id1": self.id, "x": x},
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

    def create_shares(self, workers):

        cmd = Command(
            self.host, self.port, "create_shares", additional_data=self.additional_data
        )
        cmd.execute("create_shares", distributed_workers=workers)

    def __setitem__(self, key, newvalue):

        cmd = Command(
            self.host, self.port, "__setitem__", additional_data=self.additional_data
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
            self.host, self.port, "__getitem__", additional_data=self.additional_data
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
        cmd = Command(Pt1.host, Pt1.port, "get", additional_data=additional_data)
        return_msg = cmd.execute("get")
        return_data = return_msg.data

        return return_data

    def sample_synthetic(self):

        additional_data = {}
        additional_data["name"] = self.name
        additional_data["id"] = self.id
        cmd = Command(
            self.host, self.port, "sample_synthetic", additional_data=additional_data
        )
        return_msg = cmd.execute("sample_synthetic")
        return_pt = return_msg.data
        return_pt.hook()
        return return_pt

    def get_shares(self, workers):

        cmd = Command(
            self.host, self.port, "get_shares", additional_data=self.additional_data
        )
        return_msg = cmd.execute("get_shares", distributed_workers=workers)
        return_pt = return_msg.data
        # return_pt.hook()
        return return_pt


class Command:
    """Command class provides functionality to send commands to perfrom operations remotely.
    It Allows to keep the same framework structure as the original framework.

    Args:
        host[str]: Name of dataowner host
        port[int]: Port of datawoner
        cmd_type[str]: Type of command
        data[str]: Data of command

    """

    def __init__(
        self, host: str, port: int, cmd_type: int, data="", additional_data: dict = {}
    ):

        self.port = port
        self.data = data
        self.host = host
        self.cmd_type = cmd_type
        self.additional_data = additional_data

    def execute(self, command, *args, **kwargs):
        """Executes a given command.

        Args:
            command[str]: The command to be executed
            Additional arguments follow
        Returns:
            data: The data recieved from dataowner upon a given operation"""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))

            msg = Message(
                self.additional_data["name"],
                "",
                self.cmd_type,
                "command",
                attr=args,
                key_attr=kwargs,
                data=command,
                extra=self.additional_data,
            )

            for additional in self.additional_data.keys():

                setattr(msg, additional, self.additional_data[additional])

            if type(msg) == Message:

                # send_msg(s,dill.dumps(msg))

                s.send(dill.dumps(msg))

                """Send a message
                encoded_msg = encode_msg(dill.dumps(msg))
                s.send(str(len(encoded_msg)).encode())

                for i in range(0, len(encoded_msg)):

                    s.send(encoded_msg[i])"""

                """Recieved a message
                msg_len = int(s.recv(4).decode())

                print(msg_len)

                msg_array = "".encode()

                rcv_len = 0
                while rcv_len <= msg_len:
                    print(rcv_len)
                    msg_array += s.recv(12000)
                    rcv_len += 1"""

                # data=recv_msg(s)
                data = s.recv(120000)
                data = dill.loads(data)

                if type(data) == Message:

                    return data

                else:

                    raise TypeError

            else:

                raise TypeError

    def hook_method(self, *args, **kwargs):
        """Hook method is the method that is substituted for frameworks original function.

        Args:
            name[str]: Name of command
            Additional arguments follow"""

        new_args = []
        new_kwargs = {}

        for arg in args:
            if type(arg) == Pointer:
                new_args.append(
                    Message(
                        "",
                        "",
                        "Pointer",
                        Pointer,
                        data=arg.id,
                        extra={"chain": arg.chain},
                    )
                )
            else:
                new_args.append(arg)

        for key in kwargs.keys():
            if type(kwargs[key]) == Pointer:
                new_kwargs[key] = Message(
                    "",
                    "",
                    "Pointer",
                    Pointer,
                    data=kwargs[key].id,
                    extra={"chain": kwargs[key].chain},
                )
            else:
                new_kwargs[key] = kwargs[key]

        # Message("", "", "Pointer", Pointer, data=newvalue.id)
        recieved_msg = self.execute(self.name, *new_args, **new_kwargs)
        recieved_data = recieved_msg.data
        if type(recieved_data) == Pointer:

            recieved_data.hook()

        return recieved_data


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


class DataSource:
    """Establishes a connection with the dataset hosted by the datasource.

    Args:
        worker[DataWorker]: The host of datasource
        name[str]: Name of dataset"""

    def __init__(self, analyst, worker: DataWorker, name: str):

        self.owner = worker
        self.name = name
        self.additional_data = {"name": name, "sender": analyst.name}

    def init_pointer(self):
        """Initialized pointer from the hosted dataset.

        Returns:
            returned_pt[Pointer]: The returned pointer"""

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
        """Send across data to the given dataset

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


class SharedPointer:
    def __init__(self, pointers, workergroup, additional_data={}):

        self.workergroup = workergroup

        self.pointers = pointers

        self.fn = self.pointers[list(self.pointers.keys())[0]].fn

        self.overloaded_func = {"get": self.get}
        self.additional_data = additional_data

        if id:
            self.id = id
        else:
            self.id = random.randint(0, 1000000000000)

    def hook(self):
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

                # self.additional_data["id"] = self.id

                cmd = DistributedCommand(
                    self.pointers,
                    self.workergroup,
                    "query",
                    additional_data=self.additional_data,
                )
                setattr(cmd, "name", function)
                # setattr(cmd, "id", self.id)
                setattr(self, function, cmd.hook_method)

        # Override the hooked function with custom functionality
        for function in self.overloaded_func.keys():

            if (
                function != "__class__"
                and function != "__dict__"
                and function != "__weakref__"
            ):
                cmd = DistributedCommand(
                    self.pointers,
                    self.workergroup,
                    "query",
                    additional_data=self.additional_data,
                )
                setattr(cmd, "name", function)
                # setattr(cmd, "id", self.id)
                setattr(self, function, self.overloaded_func[function])

    def get(self):

        self.additional_data["distributed_workers"] = self.pointers
        cmd = DistributedCommand(
            self.pointers,
            self.workergroup,
            "query",
            additional_data=self.additional_data,
        )

        secret_sharing = self.workergroup.config[
            list(self.workergroup.config.keys())[0]
        ].secret_sharing

        if secret_sharing == "secure_aggregation":

            workers = {}
            for i in self.pointers.keys():

                workers[i] = {
                    "port": self.pointers[i].port,
                    "host": self.pointers[i].host,
                }

            cmd.execute("create_shares", workers=workers)
            shares = cmd.execute("get_shares", workers=workers)

            result = []

            for worker in shares.keys():
                for share in shares[worker].keys():

                    result.append(shares[worker][share])

            return reconstruct(result) / len(self.pointers)

        elif secret_sharing == "Shamirs_scheme":

            raise NotImplementedError

        else:

            pass

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

            command = DistributedCommand(
                self.pointers,
                self.workergroup,
                "query",
                additional_data={
                    "pt_id1": self.id,
                    "pt_id2": x.id,
                },
            )

            return_msg = command.execute(cmd)
            # return_pt = return_msg.data
            return_msg.hook()

            # Check if the pointers lie on the same dataset
            """if self.dataset == x.dataset:

                command = DistributedCommand(
                    self.pointers,
                    "query",
                    additional_data={
                        "name": self.dataset,
                        "pt_id1": self.id,
                        "pt_id2": x.id,
                    },
                )

                return_msg = command.execute(cmd)
                #return_pt = return_msg.data
                return_msg.hook()
                return return_msg

           else:

                raise NotImplementedError"""

        else:

            command = DistributedCommand(
                self.pointers,
                self.workergroup,
                "query",
                additional_data={
                    "name": self.dataset,
                    "pt_id1": self.id,
                    "pt_id2": x.id,
                },
            )
            return_msg = command.execute(cmd)
            return_pt = return_msg.data
            return_pt.hook()
            return return_pt

    def __add__(self, x):

        group1 = self.workergroup.objects[self.id].pointers
        group2 = x.workergroup.objects[x.id].pointers

        group_result = {}

        for worker in group1.keys():

            group_result[worker] = group1[worker] + group2[worker]

        pt = SharedPointer(group_result, self.workergroup)
        return pt
        # Cast new SharedPointer

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

    def __setitem__(self, key, newvalue):

        cmd = Command(
            self.host, self.port, "__setitem__", additional_data=self.additional_data
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

        command = DistributedCommand(self.pointers, self.workergroup, "query")

        return_pt = command.execute("__getitem__", idx=idx)
        # return_pt = return_msg.data
        return_pt.hook()
        return return_pt

        command = DistributedCommand(
            self.pointers,
            self.workergroup,
            "query",
            additional_data={
                "name": self.dataset,
            },
        )

        if type(idx) == type(self):

            return_msg = command.execute(
                "__getitem__",
                idx=Message(
                    "", "", "Pointer", Pointer, data=idx.id, extra={"chain": self.chain}
                ),
            )

        else:

            return_msg = command.execute("__getitem__", idx=idx)

        return_pt = return_msg.data
        return_pt.hook()
        return return_pt


class DistributedCommand:
    """Command class provides functionality to send commands to perfrom operations remotely.
    It Allows to keep the same framework structure as the original framework.

    Args:
        host[str]: Name of dataowner host
        port[int]: Port of datawoner
        cmd_type[str]: Type of command
        data[str]: Data of command

    """

    def __init__(
        self, pointers, workergroup, cmd_type: int, data="", additional_data: dict = {}
    ):

        self.workergroup = workergroup
        self.pointers = pointers
        self.additional_data = additional_data
        self.cmd_type = cmd_type

    def execute(self, command, *args, **kwargs):
        """Executes a given command.

        Args:
            command[str]: The command to be executed
            Additional arguments follow
        Returns:
            data: The data recieved from dataowner upon a given operation"""

        outputs = {}

        for worker in self.pointers.keys():

            outputs[worker] = getattr(self.pointers[worker], command)(*args, **kwargs)

        if command != "get" and command != "create_shares" and command != "get_shares":

            pt = SharedPointer(outputs, self.workergroup)
            # Ensure all the threee have same datatype or raise error
            self.workergroup.objects[pt.id] = pt
            pt.hook()
            return pt
            # self.workergroup

        else:

            return outputs

            """# Some random temporary hack,lets change it
            result = None

            lol = type(result)

            for worker in outputs.keys():

                if type(result) != lol:

                    result += outputs[worker] / len(outputs)

                else:

                    result = outputs[worker] / len(outputs)

            return result"""

    def unroll_args_kwargs(self, args, kwargs):

        new_args = []
        new_kwargs = {}

        for arg in args:
            if type(arg) == Pointer:
                new_args.append(
                    Message(
                        "",
                        "",
                        "Pointer",
                        Pointer,
                        data=arg.id,
                        extra={"chain": arg.chain},
                    )
                )
            else:
                new_args.append(arg)

        for key in kwargs.keys():
            if type(kwargs[key]) == Pointer:
                new_kwargs[key] = Message(
                    "",
                    "",
                    "Pointer",
                    Pointer,
                    data=kwargs[key].id,
                    extra={"chain": kwargs[key].chain},
                )
            else:
                new_kwargs[key] = kwargs[key]

        return new_args, new_kwargs

    def hook_method(self, *args, **kwargs):
        """Hook method is the method that is substituted for frameworks original function.

        Args:
            name[str]: Name of command

            Additional arguments follow"""

        new_args, new_kwargs = self.unroll_args_kwargs(args, kwargs)

        recieved_pt = self.execute(self.name, *new_args, **new_kwargs)

        if type(recieved_pt) == Pointer:

            recieved_pt.hook()

        # if recieved_pt.data == "PrivateDataAccess":

        #    raise PrivateDataAccess

        return recieved_pt


class WorkerGroup:
    """Establishes a connection with the dataset hosted by the datasource.

    Args:
        worker[DataWorker]: The host of datasource
        name[str]: Name of dataset"""

    def __init__(self, analyst):

        self.name = analyst.name
        self.config = {}
        self.workers = {}
        self.additional_data = {"name": self.name, "sender": analyst.name}
        self.objects = {}

    def init_pointer(self):
        """Initialized pointer from the hosted dataset.

        Returns:
            returned_pt[Pointer]: The returned pointer"""

        returned_pt = SharedPointer(self.workers, self)
        returned_pt.hook()

        return returned_pt

    def send(self, obj):
        """Send across data to the given dataset

        Args:
            obj: A python object
        Returns:
            returned_pt[Pointer]: Pointer to the sent object

        """

        cmd = DistributedCommand(
            self.owner.host,
            self.owner.port,
            "store",
            additional_data=self.additional_data,
        )
        returned_msg = cmd.execute("store", obj=obj)
        returned_pt = returned_msg.data
        returned_pt.hook()
        return returned_pt

    def add(self, datasource, worker, config):

        self.workers[datasource.owner_name] = datasource
        self.config[datasource.owner_name] = config
