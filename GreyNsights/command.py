from .generic import Message, PrivateDataAccess
import socket
import dill


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
        self,
        host: str,
        port: int,
        cmd_type: int,
        data="",
        additional_data: dict = {},
        virtual_worker=None,
    ):

        self.virtual_worker = virtual_worker
        self.port = port
        self.data = data
        self.host = host
        self.cmd_type = cmd_type
        self.additional_data = additional_data

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

    def execute_remote(self, command, *args, **kwargs):

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
                s.send(dill.dumps(msg))
                data = s.recv(120000)
                data = dill.loads(data)

                if type(data) == Message:
                    return data

                else:
                    raise TypeError

            else:
                raise TypeError

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

    def hook_method(self, *args, **kwargs):
        """Hook method is the method that is substituted for frameworks original function.

        Args:
            name[str]: Name of command
            Additional arguments follow"""

        from .analyst import Pointer

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
