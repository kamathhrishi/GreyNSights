import socket
import pickle
import dill

from .utils import log_message
from .QueryEngine import QueryEngine
from .analyst import Pointer
from .generic import Message
from types import ModuleType
import pandas
from .frameworks import framework_support
from .handler import QueryHandler
from .graph import Node
from .synthetic import SyntheticData
from .reporter import DPReporter


class SyntheticDataset:
    def __init__(self, path, epsilon=1.0, categorical=None, candidate_keys=None):

        self.syntheticdata = SyntheticData(path, epsilon, categorical, candidate_keys)

    def random(self):

        return self.syntheticdata.random()

    def fit(self):

        return self.syntheticdata.fit()


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
        whitelist: dict = None,
        permission="AGGREGATE-ONLY",
        categorical=None,
        candidate=None,
    ):

        if type(name) == str:

            self.name = name

        else:

            print(name)
            raise TypeError

        self.owner = DataOwner(owner.name, owner.port, owner.host, "copy")
        self.host = owner.host
        self.port = owner.port
        self.data = data
        self.whitelist = whitelist
        self.buffer = {}
        self.temp_buffer = []
        self.objects = {}
        self.permission = permission
        self.categorical = (categorical,)
        self.candidate = candidate
        self.dp_reporter = DPReporter(0.1, 0.7)
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

    def __add__(self, recieved_msg: Message):

        if hasattr(recieved_msg, "x"):

            result = self.objects[recieved_msg.pt_id1] + recieved_msg.x

        else:

            result = (
                self.objects[recieved_msg.pt_id1] + self.objects[recieved_msg.pt_id2]
            )

        return self.operate("add", result)

    def __sub__(self, recieved_msg: Message):

        if hasattr(recieved_msg, "x"):

            result = self.objects[recieved_msg.pt_id1] - recieved_msg.x

        else:

            result = (
                self.objects[recieved_msg.pt_id1] - self.objects[recieved_msg.pt_id2]
            )

        return self.operate(result)

    def __mul__(self, recieved_msg: Message):

        if hasattr(recieved_msg, "x"):

            result = self.objects[recieved_msg.pt_id1] * recieved_msg.x

        else:

            result = (
                self.objects[recieved_msg.pt_id1] * self.objects[recieved_msg.pt_id2]
            )

        return self.operate("sub", result)

    def __truediv__(self, recieved_msg: Message):

        if hasattr(recieved_msg, "x"):

            result = self.objects[recieved_msg.pt_id1] / recieved_msg.x

        else:

            result = (
                self.objects[recieved_msg.pt_id1] / self.objects[recieved_msg.pt_id2]
            )

        return self.operate("truediv", result)

    def __and__(self, recieved_msg: Message):

        if hasattr(recieved_msg, "x"):

            result = self.objects[recieved_msg.pt_id1] & recieved_msg.x

        else:

            result = (
                self.objects[recieved_msg.pt_id1] & self.objects[recieved_msg.pt_id2]
            )

        return self.operate("and", result)

    def __or__(self, recieved_msg: Message):

        if hasattr(recieved_msg, "x"):

            result = self.objects[recieved_msg.pt_id1] | recieved_msg.x

        else:

            result = (
                self.objects[recieved_msg.pt_id1] | self.objects[recieved_msg.pt_id2]
            )

        return self.operate("or", result)

    def __invert__(self, recieved_msg: Message):

        result = self.objects[recieved_msg.pt_id1]
        return self.operate("invert", result)

    def __lt__(self, recieved_msg):

        if hasattr(recieved_msg, "x"):

            result = self.objects[recieved_msg.pt_id1] < recieved_msg.x

        else:

            result = (
                self.objects[recieved_msg.pt_id1] < self.objects[recieved_msg.pt_id2]
            )

        return self.operate("lt", result)

    def __lte__(self, recieved_msg: Message):

        if hasattr(recieved_msg, "x"):

            result = self.objects[recieved_msg.pt_id1] <= recieved_msg.x
        else:

            result = (
                self.objects[recieved_msg.pt_id1] <= self.objects[recieved_msg.pt_id2]
            )

        return self.operate("lte", result)

    def __gte__(self, recieved_msg: Message):

        if hasattr(recieved_msg, "x"):

            result = self.objects[recieved_msg.pt_id1] >= recieved_msg.x

        else:

            result = (
                self.objects[recieved_msg.pt_id1] >= self.objects[recieved_msg.pt_id2]
            )

        return self.operate("gte", result)

    def __gt__(self, recieved_msg: Message):

        if hasattr(recieved_msg, "x"):

            result = self.objects[recieved_msg.pt_id1] > recieved_msg.x

        else:

            result = (
                self.objects[recieved_msg.pt_id1] > self.objects[recieved_msg.pt_id2]
            )

        return self.operate("gt", result)

    def __getitem__(self, recieved_msg: Message):
        data = self.objects[recieved_msg.id]
        data = data[recieved_msg.key_attr["idx"]]
        return self.operate("getitem", data)

    def __setitem__(self, recieved_msg):
        data = self.objects[recieved_msg.id]
        data[recieved_msg.key_attr["key"]] = recieved_msg.key_attr["newvalue"]
        return self.operate("setitem", data)

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

            else:

                new_args.append(i)

        for j in recieved_msg.key_attr.keys():

            if (
                type(recieved_msg.key_attr[j]) == Message
                and recieved_msg.key_attr[j].msg_type == "Pointer"
            ):

                new_kwargs[j] = self.objects[recieved_msg.key_attr[j].data]
                self.temp_buffer.append(self.buffer[recieved_msg.key_attr[j].data])

            else:

                new_kwargs[j] = recieved_msg.key_attr[j]

        recieved_msg.attr = new_args
        recieved_msg.key_attr = new_kwargs

        return recieved_msg

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

            recieved_msg = dill.loads(conn.recv(120000000))

            if type(recieved_msg) != Message:

                raise TypeError

            # Checks if the dataset is the intended dataset. In future some sort of authentication should be present in this phase.

            """if recieved_msg.name != self.name:

                raise NameError("Dataset " + recieved_msg.name + " not found")

            recieved_msg = recieved_msg"""

            # Substitute for type of message , should be replaced by type of message in furture

            if hasattr(recieved_msg, "id"):

                data = self.objects[recieved_msg.id]
                query = recieved_msg.data
                for item in self.buffer[recieved_msg.id].parents:

                    self.temp_buffer.append(item)

            else:

                data = self.data
                query = recieved_msg.data

            recieved_msg = self.replace_pt_with_data(recieved_msg)

            internal_queries = {
                "__getitem__": self.__getitem__,
                "__add__": self.__add__,
                "__sub__": self.__sub__,
                "__mul__": self.__mul__,
                "__truediv__": self.__truediv__,
                "__and__": self.__and__,
                "__or__": self.__or__,
                "__gte__": self.__gte__,
                "__gt__": self.__gt__,
                "__lt__": self.__lt__,
                "__lte__": self.__lte__,
                "__setitem__": self.__setitem__,
            }

            if type(query) == str and (query in internal_queries.keys()):

                sent_msg = internal_queries[query](recieved_msg=recieved_msg)

            else:

                sent_msg = query_handler.handle(
                    self.temp_buffer, recieved_msg=recieved_msg, data=data, query=query
                )

            self.temp_buffer = []

            # Sends pickled message
            if type(sent_msg) == Message:

                conn.sendall(dill.dumps(sent_msg))

            else:

                raise TypeError
