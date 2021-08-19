import pickle
import socket
from types import ModuleType

import matplotlib
import nltk
import numpy
import pandas

from .analyst import Pointer
from .generic import Message

# Frameworks supported by GreyNsights
framework_support = {
    "pandas": pandas,
    "matplotlib": matplotlib,
    "nltk": nltk,
    "numpy": numpy,
}
framework_attr = {"pandas": ["shape", "len", "columns"]}

# nltk.download('punkt')
class SupportQueries:
    def __init__(self):

        self.pandas = [
            "sum",
            "mean",
            "describe",
            "std",
            "value_counts",
            "sample_synthetic",
            "median",
            "count",
            "min",
            "max",
        ]


class Command:
    """Command class provides functionality to send commands to perfrom operations remotely.
    It Allows to keep the same framework structure as the original framework.

    Args:
        name[str]: Name of the command
        chain[list]: List of sequential commands
        cmd_type[str]: Type of command
        framework[str]: Name of framework
    """

    def __init__(self, name, chain, cmd_type, framework, hook=[],virtual_worker=None):
    
        self.virtual_worker = virtual_worker
        self.name = name
        self.chain = chain
        self.hook = hook
        self.framework = framework
        self.additional_data = {}
        self.cmd_type = cmd_type
        
    def execute_virtual(self, command, *args, **kwargs):
        

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
            from .handler import QueryHandler

            query_handler = QueryHandler(
                self.virtual_worker, self.virtual_worker.name, None, None
            )


            return self.virtual_worker.data.local_dataset.handle_request(
                msg, query_handler
            )
        
    def execute(self, command, *args, **kwargs):
        """Executes a given command.

        Args:
            command[str]: The command to be executed
            Additional arguments follow
        Returns:
            data: The data recieved from dataowner upon a given operation"""

        # Maybe change how this handled?
        if self.host and self.port:
            return self.execute_remote(command, *args, **kwargs)

        elif (not self.host) and (not self.port):
            return self.execute_virtual(command, *args, **kwargs)

        else:
            raise TypeError(
                "port and host need to be speccified for remote execution or None of them for virtual. "
            )

    def execute_remote(self, command, *args, **kwargs):
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
                data=self.chain,
                extra=self.additional_data,
            )

            for additional in self.additional_data.keys():

                setattr(msg, additional, self.additional_data[additional])

            s.sendall(pickle.dumps(msg))
            data = s.recv(120000000)
            data = pickle.loads(data)

            if type(data) == Message:

                return data

            else:

                raise TypeError

    def find_pointer(self, *args, **kwargs):
        """From the given pointer as arguments it can infer the host and port the command has to be sent to.

        Args:
            The arguments and key word arguments
        Returns:
            The infered host , port and name"""

        port = None
        host = None
        name = None

        new_args = []
        new_kwargs = {}

        for item in args:

            if type(item) == Pointer:

                port = item.port
                host = item.host
                name = item.owner_name
                new_args.append(Message("", "", "Pointer", Pointer, data=item.id))

            else:

                new_args.append(item)

        for item in kwargs.keys():

            if type(kwargs) == Pointer:

                port = item.port
                host = item.host
                name = item.owner_name
                new_kwargs[item] = Message(
                    "", "", "Pointer", Pointer, data=kwargs[item].id
                )

            else:

                new_kwargs[item] = kwargs[item]

        return port, host, name, new_args, new_kwargs

    def hook_method(self, *args, **kwargs):
        """Hook method is the method that is substituted for frameworks original function.

        Returns:
            data: The data recieved after performing given operation"""

        port, host, name, new_args, new_kwargs = self.find_pointer(*args, **kwargs)

        self.host = host
        self.port = port

        self.additional_data = {
            "name": name,
            "framework": self.framework,
        }
        
        print("HOOK METHOD: ",self.name)

        recieved_msg = self.execute(self.name, *new_args, **new_kwargs)
        recieved_data = recieved_msg.data
        if type(recieved_data) == Pointer:

            recieved_data.hook()

        return recieved_data


class Base_Framework:
    """This class defines how to hook an overall framework. This does it only upto a depth of 2.
    This needs to be replaced further with a
    clean recursive implementation.

    Args:
        framework: The original framework to be hooked
        name[str]: name of the framework

    """

    def __init__(self, framework, name: str,virtual_worker=None):

        self.framework = framework
        self.name = name
        self.virtual_worker = virtual_worker

    def hook_module(self):
        """Hook method is the method that is substituted for frameworks original function.

        Returns:
            frame: The hooked framework object"""

        frame = Command(self.name, [], "query", self.name,virtual_worker=self.virtual_worker)

        for i in dir(self.framework):

            cmd1 = Command(i, [i], "query", self.name,virtual_worker=self.virtual_worker)

            if isinstance(getattr(self.framework, i), ModuleType):

                for j in dir(getattr(self.framework, i)):

                    ar = [i, j]
                    cmd2 = Command(
                        ar,
                        ar,
                        "query",
                        self.name,
                        hook=dir(getattr(getattr(self.framework, i), j)),
                        virtual_worker=self.virtual_worker
                    )
                    setattr(cmd1, j, cmd2.hook_method)

            else:

                setattr(cmd1, i, cmd1.hook_method)

            if isinstance(getattr(self.framework, i), ModuleType):

                setattr(frame, i, cmd1)

            else:

                setattr(frame, i, cmd1.hook_method)

        return frame


class framework:
    def __init__(self,virtual_worker=None):

        self.pandas = Base_Framework(pandas, "pandas",virtual_worker=virtual_worker).hook_module().pandas
        self.matplotlib = Base_Framework(matplotlib, "matplotlib",virtual_worker=virtual_worker).hook_module()
        self.nltk = Base_Framework(nltk, "nltk",virtual_worker=virtual_worker).hook_module()
        self.numpy = Base_Framework(numpy, "numpy",virtual_worker=virtual_worker).hook_module()
