import random

from .mpc import reconstruct
from .analyst import Command, Message, Pointer


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
                setattr(self, function, cmd.hook_method)

        # Override the hooked function with custom functionality
        for function in self.overloaded_func.keys():
            if function not in ["__class__", "__dict__", "__weakref__"]:
                cmd = DistributedCommand(
                    self.pointers,
                    self.workergroup,
                    "query",
                    additional_data=self.additional_data,
                )
                setattr(cmd, "name", function)
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

        if command not in ["get", "create_shares", "get_shares"]:
            pt = SharedPointer(outputs, self.workergroup)
            # Ensure all the three have same datatype or raise error
            self.workergroup.objects[pt.id] = pt
            pt.hook()
            return pt
        else:
            return outputs

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
