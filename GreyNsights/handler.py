from .utils import log_message
from .QueryEngine import QueryEngine
from .analyst import Pointer
from .generic import Message, PrivateDataAccess
from types import ModuleType
import pandas
from .frameworks import framework_support
from .analyst import Command
from .graph import Node, visualize, validate
from .mpc import gen_shares
import random


class QueryHandler:
    """Handles and performs all queries or operations on the host side(DataOwner).

    Args:
        owner[DataOwner]: The DataOwner object
        name[str]: Name of the DataOwner
        host[str]: Host of DataOwner
        port[int]: Port of DataOwner"""

    def __init__(self, owner, name, host, port):

        self.owner = owner
        self.name = name
        self.port = port
        self.host = host

    def handle(self, buffer, **kwargs):
        """Handle given command by DataOwner appropriately

        Args:
             kwargs: Contains the recieved message , data and query.
        returns:
             sent_msg: The corresponding query output

        """

        query = kwargs["query"]
        data = kwargs["data"]
        recieved_msg = kwargs["recieved_msg"]

        # args.pop(0)

        dic = {
            "get": self.return_pointer,
            "init": self.init_pointer,
            "store": self.store_val,
            "handle_query": self.handle_query,
        }

        self.dp_queries = ["count", "mean", "sum", "percentile", "max", "min", "median"]

        print("\n")
        print(query)
        print("\n")

        if (
            type(query) == str
            and query in self.dp_queries
            and self.owner.config.privacy_budget != "None"
        ):

            print("\n")
            print("Does this satisfy?")
            print("\n")
            sent_msg = self.handle_dp_query(
                buffer, data=data, query=query, recieved_msg=recieved_msg
            )

        else:

            sent_msg = None

            if type(query) == str and query in dic.keys():

                sent_msg = dic[query](
                    buffer, data=data, query=query, recieved_msg=recieved_msg
                )

            else:

                if hasattr(recieved_msg, "framework"):

                    sent_msg = self.handle_query(
                        buffer, data=data, query=query, recieved_msg=recieved_msg
                    )

                else:

                    sent_msg = self.handle_query(
                        buffer, data=data, query=query, recieved_msg=recieved_msg
                    )

        return sent_msg

    def handle_dp_query(self, buffer, *args, **kwargs):

        data = kwargs["data"]
        query = kwargs["query"]

        log_message("Query", query)

        result = self.owner.dp_reporter.query(query, data)

        sent_pt = Pointer(
            self.owner,
            self.name,
            self.host,
            self.port,
            result,
            child=dir(result),
            data_type=type(result),
            additional_data={"name": self.name},
        )

        buffer.append(query)

        """for item in self.owner.temp_graph:
            print("Graph ITEM: ", item)

            if item not in self.owner.graph.keys():

                self.owner.graph[item] = False

            else:

                self.owner.graph[item] = True

        print("\n")
        print("BUFFER: ", self.owner.graph)
        print("\n")"""

        n = Node(query, parents=buffer)
        # print("\n")
        # print("\n")
        # print("VISUALIZE")
        # visualize(n)
        # print("\n")
        # print("\n")

        self.owner.buffer[sent_pt.id] = n
        self.owner.objects[sent_pt.id] = result

        sent_msg = Message(
            self.owner.name,
            "",
            "resultant_pointer",
            "pointer",
            data=sent_pt,
            extra={"name": self.owner.name, "id": sent_pt.id},
        )

        return sent_msg

    def init_pointer(self, buffer, *args, **kwargs):
        """Initialize pointer from given dataset"""

        data = kwargs["data"]
        query = kwargs["query"]

        log_message("Query", query)
        query_engine = QueryEngine()
        result = data
        result = query_engine.call(result, data, query)
        # Registers the result as a pointer in the DataOwner's list of objects and sends pointer for reference.
        sent_pt = Pointer(
            self.owner,
            self.name,
            self.host,
            self.port,
            result,
            child=dir(result),
            data_type=type(result),
            additional_data={"name": self.name},
        )

        buffer.append("init")

        for item in self.owner.temp_graph:

            print("GRAPH ITEM: ", item)

            if item not in self.owner.graph.keys():

                self.owner.graph[item] = False

            else:

                self.owner.graph[item] = True

        # self.owner.graph[sent_pt.id]=Node("init",parents=[])
        print("\n")
        print("BUFFER: ", self.owner.graph)
        print("\n")

        self.owner.buffer[sent_pt.id] = Node("init", parents=buffer)
        self.owner.objects[sent_pt.id] = result

        print("\n")
        print(self.owner)
        print("Owner: ", self.owner.objects)

        sent_msg = Message(
            self.owner.name,
            "",
            "resultant_pointer",
            "pointer",
            data=sent_pt,
            extra={"name": self.owner.name, "id": sent_pt.id},
        )

        return sent_msg

    def return_pointer(self, buffer, *args, **kwargs):

        recieved_msg = kwargs["recieved_msg"]

        if self.owner.permission == "AGGREGATE-ONLY":

            if validate(self.owner.buffer[recieved_msg.id]):

                sent_msg = self.owner.objects[recieved_msg.id]

                sent_msg = Message(
                    self.owner.name,
                    "",
                    "resultant_pointer",
                    "pointer",
                    data=sent_msg,
                    extra={"name": self.name},
                )

                return sent_msg

            else:

                sent_msg = Message(
                    self.owner.name,
                    "",
                    "Error",
                    "Error",
                    data="PrivateDataAccess",
                    extra={"name": self.name},
                )

                return sent_msg

        else:

            if validate(self.owner.buffer[recieved_msg.id]):

                sent_msg = self.owner.objects[recieved_msg.id]

                sent_msg = Message(
                    self.owner.name,
                    "",
                    "resultant_pointer",
                    "pointer",
                    data=sent_msg,
                    extra={"name": self.name},
                )

                return sent_msg

    def store_val(self, buffer, *args, **kwargs):
        """Register a given value in the DataOwner side.

        Args:
             kwargs: Contains the recieved message , data and query.
        returns:
             sent_msg: The corresponding pointer

        """

        recieved_msg = kwargs["recieved_msg"]
        result = recieved_msg.key_attr["obj"]

        sent_pt = Pointer(
            self.owner,
            self.name,
            self.host,
            self.port,
            result,
            child=dir(result),
            data_type=type(result),
            additional_data={"name": self.name},
        )

        buffer.append("store")
        self.owner.objects[sent_pt.id] = result

        for item in self.owner.temp_graph:

            print("GRAPH ITEM: ", item)

            if item not in self.owner.graph.keys():

                self.owner.graph[item] = False

            else:

                self.owner.graph[item] = True

        print("\n")
        print("BUFFER: ", self.owner.graph)
        print("\n")

        self.owner.buffer[sent_pt.id] = Node("store", parents=buffer)

        sent_msg = Message(
            self.owner.name,
            "",
            "resultant_pointer",
            "pointer",
            data=sent_pt,
            extra={"name": self.owner.name, "id": sent_pt.id},
        )

        return sent_msg

    def handle_query(self, buffer, *args, **kwargs):
        """Handles a given query appropriately

        Args:
             kwargs: Contains the recieved message , data and query.
        returns:
             sent_msg[Message]: The corresponding output of query

        """

        data = kwargs.pop("data")
        query = kwargs.pop("query")
        recieved_msg = kwargs.pop("recieved_msg")

        args = recieved_msg.attr
        kwargs = recieved_msg.key_attr

        if hasattr(recieved_msg, "framework"):

            framework = recieved_msg.framework

        else:

            framework = None

        # Remove framework from kwargs

        if type(query) != list:

            result = getattr(data, query)(*args, **kwargs)

        else:

            partial_result = None

            for q in query:

                if len(kwargs) != 0:

                    if partial_result:

                        # result = getattr(partial_result, q)(data, *args, **kwargs)
                        result = getattr(partial_result, q)(*args, **kwargs)
                        partial_result = result

                    else:

                        if isinstance(
                            getattr(framework_support[framework], q), ModuleType
                        ):

                            result = getattr(framework_support[framework], q)
                            partial_result = result

                        else:

                            result = getattr(framework_support[framework], q)(
                                *args, **kwargs
                            )
                            partial_result = result

                else:

                    if partial_result:

                        result = getattr(partial_result, q)(*args, **kwargs)
                        partial_result = result

                    else:

                        if isinstance(
                            getattr(framework_support[framework], q), ModuleType
                        ):

                            result = getattr(framework_support[framework], q)
                            partial_result = result

                        else:

                            result = getattr(framework_support[framework], q)(
                                *args, **kwargs
                            )
                            partial_result = result

        log_message("Query", query)
        query_engine = QueryEngine()
        result = query_engine.call(result, data, query)

        # Registers the result as a pointer in the DataOwner's list of objects and sends pointer for reference.

        sent_pt = Pointer(
            self.owner,
            self.name,
            self.host,
            self.port,
            result,
            child=dir(result),
            data_type=type(result),
            additional_data={"name": self.name},
        )

        buffer.append(query)

        """for item in self.owner.temp_graph:

            print("GRAPH ITEM: ", item)

            if item not in self.owner.graph.keys():

                self.owner.graph[item] = False

            else:

                self.owner.graph[item] = True"""

        print("\n")
        print("BUFFER: ", self.owner.graph)
        print("\n")
        n = Node(query, parents=buffer)
        # print("\n")
        # print("\n")
        # print("VISUALIZE")
        # visualize(n)
        # print("\n")
        # print("\n")

        self.owner.buffer[sent_pt.id] = n
        self.owner.objects[sent_pt.id] = result

        sent_msg = Message(
            self.owner.name,
            "",
            "resultant_pointer",
            "pointer",
            data=sent_pt,
            extra={"name": self.owner.name, "id": sent_pt.id},
        )

        return sent_msg
