import hashlib, binascii
import getpass
import cPickle

MESSAGE_CHUNK_SIZE = 4096
SERVER_DEFAULT_PORT = 60000                # Reserve a port for the service.
CONSOLE_TERM = "MngSys>> "
EXIT_COMMAND = "exit"
NEW_USER_COMMAND = "new_user"

WELCOME_SERVICE_MESSAGE = "Welcome to the Inventory Management System!"
ACCEPT_SERVICE_MESSAGE = "Hello %s!"
DENY_SERVICE_MESSAGE = "ACCESS DENIED! Reach to maximum number of connections."

def serialize_data_message(data):
    """ Serialize a data object into string,
        then decide the data string base on maximum message chunk size"""
    data_str = cPickle.dumps(data)
    return data_str

def deserialize_data(data_str):
    """ Deserialize data string into data object """
    data = cPickle.loads(data_str)
    return data

def is_error_message(data_obj):
    """ sending an error message """
    if data_obj.has_key("ERROR"):
        return True
    return False

def receive_data_message(socket_obj):
    """ sending a data message """
    data_str = socket_obj.recv(MESSAGE_CHUNK_SIZE)
    data_obj = deserialize_data(data_str)
    if is_error_message(data_obj):
        return data_obj["ERROR"]
    return data_obj["DATA"]

def send_data_message(socket_obj, message):
    """ sending a data message """
    msg = serialize_data_message({"DATA": message})
    socket_obj.sendall(msg)

def send_error_message(socket_obj, message):
    """ sending an error message """
    msg = serialize_data_message({"ERROR": message})
    socket_obj.sendall(msg)

def create_secure_user_info(username, password):
    """ Encrypting user info into hash """
    password_hash = binascii.hexlify(hashlib.pbkdf2_hmac(
            'sha256', password, username, 100000))
    return {'username': username, 'password_hash': password_hash}

def get_user_info():
    username = raw_input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    user_info = create_secure_user_info(username, password)
    return user_info

def create_new_user():
    command_info = NEW_USER_COMMAND
    user_info = get_user_info()
    command_info += " username=" + user_info["username"]
    command_info += " password_hash=" + user_info["password_hash"]
    command_info += " usertype=" + raw_input("Enter usertype: ")
    return command_info
