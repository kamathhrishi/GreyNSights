"""Generic functions for GreyNSights."""


class Message:
    """Messages are generic datatypes to exchange information between server/client

    Args:
        sender_name (str): Name of the sender
        recieved_name (str): name of the reciever
        msg_type (str): Type of message
        dtype (str): Datatype of data in message
        attr (list): The arguments carried by message
        key_attr (Dict): The key word arguments carried by Dict
    """

    def __init__(
        self,
        sender_name,
        reciever_name,
        msg_type,
        dtype,
        attr=None,
        key_attr=None,
        data=None,
        extra={},
        framework=None
    ):

        self.reciever_name = reciever_name
        self.sender_name = sender_name
        self.data = data
        self.msg_type = msg_type
        self.attr = attr
        self.key_attr = key_attr
        self.dtype = dtype
        self.framework = framework

        for key in extra.keys():

            setattr(self, key, extra[key])

    def __str__(self):

        string = ""

        string += "\n"
        string += "Message" + "->" + self.msg_type
        string += "\n"
        string += "\t \t dtype" + ":" + str(self.dtype)
        string += "\n"
        string += "\t \t sender" + ":" + str(self.sender_name)
        string += "\n"
        string += "\t \t reciever" + ":" + str(self.reciever_name)
        string += "\n"

        attr_str = ""

        for attr in dir(self):

            attr_str += attr
            attr_str += "\n"

        string += "\t \t Attributes"
        string += attr_str
        string += "\n"

        return string


class PrivateDataAccess(Exception):
    def __str__(self):

        return "Private Data was accessed"
