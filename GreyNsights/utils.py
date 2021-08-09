# python dependencies
import pickle
import codecs
import struct


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


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack(">I", len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack(">I", raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    print("data:", data)
    print("n:", n)
    while len(data) < n:
        print("DIFFERENCE: ", n - len(data))
        print("DATA TYPE: ", type(n - len(data)))
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


BYTE_SIZE = 12000


def encode_msg(msg):
    byte_array = []

    data = msg

    for index in range(0, len(data), BYTE_SIZE):

        byte_array.append(data[index : index + BYTE_SIZE])

    # print("CHECK",check(byte_array,msg))

    return byte_array
