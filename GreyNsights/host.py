import socket
import pickle
import dill
from types import ModuleType
import pandas

from .utils import log_message
from .QueryEngine import QueryEngine
from .analyst import Pointer
from .generic import Message
from .frameworks import framework_support
from .handler import QueryHandler
from .graph import Node
from .mpc import gen_shares
from .analyst import Command
from .utils import send_msg, recv_msg, encode_msg


class DataOwner:
    """DataOwner class handles all the functionalities relating to the Data owner (the host or owner of the data).
    It also stores the relevent details.

    Args:
        name[str]: Name of the Data Owner
        port[int]: Port through which data owner hosts dataset
        host[str]: The name of host
        object_type[str]: If the reference of dataowner is original or reference. Can be used to set permissions later.

    """

    def __init__(self, name: str, port: int, host: str, object_type: str = "original"):

        self.name = name
        self.port = port
        self.host = host

        # Make this private type
        self.type = object_type
        self.objects = {}

    def register_obj(self, name, obj):

        self.objects[name] = obj


class Dataset:
    """Dataset handles all the functionalities relating to hosting the dataset and executing the commands on the host.

    Args:
        owner[DataOwner]: The owner of the dataset
        name[str]: Name of the dataset
        data: The dataset

    """

    def __init__(
        self,
        owner: DataOwner,
        name: str,
        data,
        config,
        whitelist: dict = None,
        permission="AGGREGATE-ONLY",
    ):

        if type(name) == str:

            self.name = name

        else:

            raise TypeError

        if isinstance(owner, DataOwner):
            self.owner = DataOwner(owner.name, owner.port, owner.host, "copy")

        else:
            self.owner = owner

        self.shares = {}
        self.config = config
        self.host = owner.host
        self.port = owner.port
        self.data = data
        self.whitelist = whitelist
        self.buffer = {}
        self.temp_graph = []
        self.graph = {}
        self.temp_buffer = []
        self.objects = {}
        self.permission = permission
        if config.privacy_budget != "None":
            from .reporter import DPReporter

            self.dp_reporter = DPReporter(config.privacy_budget, 0.7)
        else:
            self.dp_reporter = None

        self.mpc_shares = {}

        if config.dataset_name != self.name and config.owner_name != owner.name:

            print("Config Rejected")
            print(self.name)
            print(owner.name)

        if self.config.private_columns != "None":

            print("Private COlumns Exist")
            print(config.private_columns)
            self.data = self.data.drop(config.private_columns, axis=1)

        owner.register_obj(name, self)

    def register_obj(self, name, obj):
        """Register object on the dataset.

        Args:
            name[str]: Name of the object to be registered
            obj: The object to be registered"""

        self.objects[name] = obj

    def operate(self, query, result):
        """Register result of arithmetic/logical operator and send it across as a pointer

        Args:
            result: The result of arithmetic/logical operation
        Returns:
            sent_msg[Message]: The pointer sent across after registering result of operation

        """

        Pt = Pointer(
            self.owner,
            self.name,
            self.host,
            self.port,
            data=result,
            additional_data={"name": self.name},
            data_type=type(result),
        )

        n = Node(query, parents=self.temp_buffer)

        self.objects[Pt.id] = result
        self.buffer[Pt.id] = n

        sent_msg = Message(
            self.owner.name,
            "",
            "resultant_pointer",
            "pointer",
            data=Pt,
            extra={"name": self.owner.name, "id": Pt.id},
        )

        return sent_msg

    def __getitem__(self, recieved_msg: Message, query=None):

        try:
            data = self.objects[recieved_msg.id]
        except KeyError:
            data = self.owner.objects[recieved_msg.id]

        data = data[recieved_msg.key_attr["idx"]]
        return self.operate("getitem", data)

    def __setitem__(self, recieved_msg, query=None):
        try:
            data = self.objects[recieved_msg.id]
        except KeyError:
            data = self.owner.objects[recieved_msg.id]

        data[recieved_msg.key_attr["key"]] = recieved_msg.key_attr["newvalue"]
        return self.operate("setitem", data)

    def register_share(self, recieved_msg, query=None):

        self.mpc_shares[recieved_msg.name] = recieved_msg.mpc_share

        sent_msg = Message(
            self.owner.name,
            "",
            "resultant_pointer",
            "pointer",
            data=None,
            extra={"name": self.owner.name},
        )

        return sent_msg

    def create_shares(self, recieved_msg, query=None):

        try:
            data = self.objects[recieved_msg.id]
        except KeyError:
            data = self.owner.objects[recieved_msg.id]

        workers = recieved_msg.key_attr["distributed_workers"]
        generated_shares = gen_shares(data, len(workers))

        idx = 0

        for worker in workers.keys():
            if workers[worker]["port"] != self.port:

                additional_data = {
                    "name": self.name,
                    "mpc_share": generated_shares[idx],
                }

                cmd = Command(
                    workers[worker]["host"],
                    workers[worker]["port"],
                    "register_share",
                    additional_data=additional_data,
                )
                cmd.execute("register_share")

            else:
                self.mpc_shares[self.name] = generated_shares[idx]

            idx += 1

        sent_msg = Message(
            self.owner.name,
            "",
            "resultant_pointer",
            "pointer",
            data=None,
            extra={"name": self.owner.name},
        )

        return sent_msg

    def replace_pt_with_data(self, recieved_msg):
        """Given the arguments passed as pointers with Message pointers , the message pointers will be
        replaced with the original pointer data

        Args:
            recieved_msg: The recieved messsage which might have pointers
        Returns:
            recieved_msg: The recieved message with original data"""

        new_args = []
        new_kwargs = {}

        for i in recieved_msg.attr:
            if type(i) == Message and i.msg_type == "Pointer":
                new_args.append(self.objects[i.data])
                self.temp_buffer.append(self.buffer[i.data])
                # elf.temp_graph.append(i.data)

            else:
                new_args.append(i)

        for j in recieved_msg.key_attr.keys():
            if (
                type(recieved_msg.key_attr[j]) == Message
                and recieved_msg.key_attr[j].msg_type == "Pointer"
            ):
                new_kwargs[j] = self.objects[recieved_msg.key_attr[j].data]
                self.temp_buffer.append(self.buffer[recieved_msg.key_attr[j].data])
                # self.temp_graph.append(j.data)
            else:
                new_kwargs[j] = recieved_msg.key_attr[j]

        recieved_msg.attr = new_args
        recieved_msg.key_attr = new_kwargs

        return recieved_msg

    def get_shares(self, recieved_msg, query=None):

        sent_msg = Message(
            self.owner.name,
            "",
            "mpc_shares",
            "mpc_shares",
            data=self.mpc_shares,
            extra={"name": self.owner.name},
        )

        self.mpc_shares = {}

        return sent_msg

    def get_config(self, recieved_msg, query=None):

        sent_msg = Message(
            self.owner.name,
            "",
            "mpc_shares",
            "mpc_shares",
            data=self.config,
            extra={"name": self.owner.name},
        )

        return sent_msg

    def exec_operation(self, recieved_msg, query=None):

        import operator

        op_str = query.replace("_", "")
        op = getattr(operator, query)

        if hasattr(recieved_msg, "x"):
            result = op(self.objects[recieved_msg.pt_id1], recieved_msg.x)
        else:
            result = op(
                self.objects[recieved_msg.pt_id1], self.objects[recieved_msg.pt_id2]
            )

        return self.operate(op_str, result)

    def handle_request(self, recieved_msg, query_handler):

        self.temp_graph = []

        if type(recieved_msg) != Message:

            raise TypeError

        # Checks if the dataset is the intended dataset. In future some sort of authentication should be present in this phase.
        """if recieved_msg.name != self.name:

                raise NameError("Dataset " + recieved_msg.name + " not found")

        recieved_msg = recieved_msg"""

        # Substitute for type of message , should be replaced by type of message in furture
        if hasattr(recieved_msg, "id"):
            try:
                data = self.objects[recieved_msg.id]
            except KeyError:
                data = self.owner.objects[recieved_msg.id]

            query = recieved_msg.data
            self.temp_graph.append([recieved_msg.id, recieved_msg.data])

        else:
            data = self.data
            query = recieved_msg.data

        recieved_msg = self.replace_pt_with_data(recieved_msg)

        internal_queries = {
            "__getitem__": self.__getitem__,
            "__setitem__": self.__setitem__,
            "__add__": self.exec_operation,
            "__sub__": self.exec_operation,
            "__mul__": self.exec_operation,
            "__truediv__": self.exec_operation,
            "__and__": self.exec_operation,
            "__or__": self.exec_operation,
            "__gte__": self.exec_operation,
            "__gt__": self.exec_operation,
            "__lt__": self.exec_operation,
            "__lte__": self.exec_operation,
            "register_share": self.register_share,
            "create_shares": self.create_shares,
            "get_config": self.get_config,
            "get_shares": self.get_shares,
        }

        if type(query) == str and (query in internal_queries.keys()):
            sent_msg = internal_queries[query](recieved_msg=recieved_msg, query=query)

        else:
            sent_msg = query_handler.handle(
                self.temp_buffer, recieved_msg=recieved_msg, data=data, query=query
            )
            self.temp_buffer = []

        return sent_msg

    def listen(self):
        """Listens for queries and requests from analyst and executes the queries. The queries are either directly sent or processed by QueryEngine."""

        # REFRACTOR REQUIRED: abstract and write seperate functions for various functionalities and cleaner if else statements

        # Establishes a socket connection and begins to listen requests
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen()

        log_message(
            "Connection",
            self.name
            + " Listening to requests from port "
            + str(self.host)
            + " "
            + str(self.port),
        )

        # Continiously listens until terminated
        while True:
            # Waits until a request is present
            conn, address = s.accept()
            query_handler = QueryHandler(self, self.name, self.host, self.port)

            log_message(
                "Connection",
                "Connection from " + str(address) + " has been established",
            )
            log_message("Dataset Name", self.name)

            recieved_msg = conn.recv(1200000)
            recieved_msg = dill.loads(recieved_msg)

            sent_msg = self.handle_request(recieved_msg, query_handler)

            # Sends pickled message
            if type(sent_msg) == Message:
                # send_msg(conn,dill.dumps(sent_msg))
                conn.sendall(dill.dumps(sent_msg))
            else:
                raise TypeError(f"{type(sent_msg)} is not valid type for message")
