import pickle
import codecs


def pickle_string_to_obj(obj):
    return pickle.loads(codecs.decode(obj, "base64"))


def get_encoded_obj(obj):
    return codecs.encode(pickle.dumps(obj), "base64").decode()


def log_message(msg_type: str, message: str):
    """The default style of log messages displayed on DataOwner's screen

    args[str]: The type of message
    message[str]: The message to be displayed

    """
    print("Logger", "<" + msg_type + ">", ":", message)
