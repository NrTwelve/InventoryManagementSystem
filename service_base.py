
import cPickle

MESSAGE_CHUNK_SIZE = 4096
SERVER_PORT =  60000                # Reserve a port for the service.
CONSOLE_TERM = "MngSys>> "

ACCEPT_SERVICE_MESSAGE = "Welcome to the Inventory Management System!"
DENY_SERVICE_MESSAGE = "DENY! Reach to maximum number of connections."


class ServiceBase(object):
    """Base class for client and server, which support for communication frame and method"""
    def __init__(self):
        """ Constructor for ServiceBase """
        pass

    def send_data_message(self, socket_obj, message):
        """ sending a data message """
        msg = self.serialize_data_message({"DATA": message})
        socket_obj.sendall(msg)

    def send_error_message(self, socket_obj, message):
        """ sending an error message """
        msg = self.serialize_data_message({"ERROR": message})
        socket_obj.sendall(msg)

    def is_error_message(self, data_obj):
        """ sending an error message """
        if data_obj.has_key("ERROR"):
            print data_obj["ERROR"]
            return True
        return False

    def receive_data_message(self, socket_obj):
        """ sending a data message """
        data_str = socket_obj.recv(MESSAGE_CHUNK_SIZE)
        data_obj = self.deserialize_data(data_str)
        if not self.is_error_message(data_obj):
            print data_obj["DATA"]

    def serialize_data_message(self, data):
        """ Serialize a data object into string,
            then decide the data string base on maximum message chunk size"""
        data_str = cPickle.dumps(data)
        return data_str

    def deserialize_data(self, data_str):
        """ Deserialize data string into data object """
        data = cPickle.loads(data_str)
        return data
